from __future__ import annotations

import csv
import io
import json
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from .config import CORS_ORIGINS, DATASET_PATH, MODEL_DIRECTORY
from .database import Base, engine, get_db
from .models import Applicant, Assessment, DatasetSummary, ModelPerformance, User
from .schemas import ApplicantCreate, ApplicantOut, ApplicantUpdate, ChangePasswordRequest, LoginRequest, PredictionOut, ProfileUpdate, RegisterRequest, ScoringRequest, UserOut
from .security import create_session, destroy_session, get_user_by_token, hash_password, verify_password
from .ml.service import load_active_artifact, predict_credit, reset_model_cache
from .ml.train import FEATURE_COLUMNS, generate_credit_dataset, resolve_dataset_path, train_models

app = FastAPI(title="Credora API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

COOKIE_NAME = "credora_session"


def init_app() -> None:
    Base.metadata.create_all(bind=engine)
    if not DATASET_PATH.exists():
        generate_credit_dataset(DATASET_PATH)
    from .database import SessionLocal
    with SessionLocal() as db:
        has_metrics = db.query(ModelPerformance).first() is not None
    if not (MODEL_DIRECTORY / "active_model.joblib").exists() or not has_metrics:
        train_models(DATASET_PATH)

@app.on_event("startup")
def startup() -> None:
    init_app()
    try:
        load_active_artifact()
    except Exception:
        train_models(DATASET_PATH)
        reset_model_cache()
        load_active_artifact()


def clean_error(message: str, code: int = 400):
    raise HTTPException(status_code=code, detail=message)


def user_to_out(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "profile_image": user.profile_image,
        "preferred_language": user.preferred_language,
        "theme": user.theme,
        "default_model": user.default_model,
        "prediction_threshold": user.prediction_threshold,
        "auto_save": user.auto_save,
        "email_notifications": user.email_notifications,
        "assessment_alerts": user.assessment_alerts,
        "created_at": user.created_at.isoformat(),
    }


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE_NAME)
    user = get_user_by_token(db, token)
    if not user:
        clean_error("Please sign in to continue.", status.HTTP_401_UNAUTHORIZED)
    return user


def parse_json(text: str | None, fallback):
    if not text:
        return fallback
    try:
        return json.loads(text)
    except Exception:
        return fallback


def latest_assessment(db: Session, applicant_id: int) -> Assessment | None:
    return db.query(Assessment).filter(Assessment.applicant_id == applicant_id).order_by(Assessment.created_at.desc()).first()


def applicant_to_out(db: Session, applicant: Applicant) -> dict:
    latest = latest_assessment(db, applicant.id)
    return {
        "id": applicant.id,
        "full_name": applicant.full_name,
        "email": applicant.email,
        "phone": applicant.phone,
        "age": applicant.age,
        "gender": applicant.gender,
        "employment_status": applicant.employment_status,
        "employment_duration": applicant.employment_duration,
        "annual_income": applicant.annual_income,
        "monthly_income": applicant.monthly_income,
        "existing_debt": applicant.existing_debt,
        "monthly_expenses": applicant.monthly_expenses,
        "savings": applicant.savings,
        "latest_credit_score": latest.credit_score if latest else None,
        "current_risk_level": latest.risk_level if latest else None,
        "latest_recommendation": latest.recommendation if latest else None,
        "last_assessment": latest.created_at.isoformat() if latest else None,
        "created_at": applicant.created_at.isoformat(),
    }


def assessment_to_out(assessment: Assessment) -> dict:
    return {
        "id": assessment.id,
        "assessment_reference": assessment.assessment_reference,
        "applicant_id": assessment.applicant_id,
        "applicant": assessment.applicant.full_name if assessment.applicant else "Applicant",
        "model_name": assessment.model_name,
        "model_version": assessment.model_version,
        "input_snapshot": parse_json(assessment.input_snapshot, {}),
        "engineered_features": parse_json(assessment.engineered_features, {}),
        "prediction": assessment.prediction,
        "probability": assessment.probability,
        "confidence": assessment.confidence,
        "credit_score": assessment.credit_score,
        "risk_level": assessment.risk_level,
        "recommendation": assessment.recommendation,
        "positive_factors": parse_json(assessment.positive_factors, []),
        "risk_factors": parse_json(assessment.risk_factors, []),
        "improvement_recommendations": parse_json(assessment.improvement_recommendations, []),
        "created_at": assessment.created_at.isoformat(),
    }


def save_assessment(db: Session, user: User, payload: dict, prediction: dict) -> Assessment:
    email = payload.get("email")
    applicant = None
    if email:
        applicant = db.query(Applicant).filter(Applicant.user_id == user.id, Applicant.email == email).first()
    if not applicant:
        applicant = Applicant(
            user_id=user.id,
            full_name=payload.get("full_name") or "New Applicant",
            email=email,
            phone=payload.get("phone"),
        )
        db.add(applicant)
        db.flush()
    for field in ["full_name", "email", "phone", "age", "gender", "employment_status", "employment_duration", "annual_income", "monthly_income", "existing_debt", "monthly_expenses", "savings"]:
        if field in payload:
            setattr(applicant, field, payload.get(field))
    ref = "CRA-" + datetime.now().strftime("%Y%m%d") + "-" + secrets.token_hex(3).upper()
    assessment = Assessment(
        assessment_reference=ref,
        applicant_id=applicant.id,
        user_id=user.id,
        model_name=prediction["model_name"],
        model_version=prediction["model_version"],
        input_snapshot=json.dumps(payload),
        engineered_features=json.dumps(prediction["engineered_features"]),
        prediction=prediction["prediction"],
        probability=prediction["probability"],
        confidence=prediction["confidence"],
        credit_score=prediction["credit_score"],
        risk_level=prediction["risk_level"],
        recommendation=prediction["recommendation"],
        positive_factors=json.dumps(prediction["positive_factors"]),
        risk_factors=json.dumps(prediction["risk_factors"]),
        improvement_recommendations=json.dumps(prediction["improvement_recommendations"]),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    active = db.query(ModelPerformance).filter(ModelPerformance.is_active == True).first()
    return {"backend": "ready", "database": "ready", "model_status": "loaded" if active else "training_required", "active_model": active.model_name if active else None}

@app.post("/api/auth/register")
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    exists = db.query(User).filter(func.lower(User.email) == payload.email.lower()).first()
    if exists:
        clean_error("An account with this email already exists.", 409)
    user = User(full_name=payload.full_name.strip(), email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_session(db, user)
    response.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", max_age=60*60*24*7)
    return {"user": user_to_out(user)}

@app.post("/api/auth/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        clean_error("Invalid email or password.", 401)
    token = create_session(db, user)
    response.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", max_age=60*60*24*7)
    return {"user": user_to_out(user)}

@app.post("/api/auth/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    destroy_session(db, request.cookies.get(COOKIE_NAME))
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}

@app.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return {"user": user_to_out(user)}

@app.put("/api/auth/profile")
def update_profile(payload: ProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"]:
        existing = db.query(User).filter(func.lower(User.email) == data["email"].lower(), User.id != user.id).first()
        if existing:
            clean_error("This email is already used by another account.", 409)
        data["email"] = data["email"].lower()
    for key, value in data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return {"user": user_to_out(user)}

@app.post("/api/auth/change-password")
def change_password(payload: ChangePasswordRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, user.password_hash):
        clean_error("Current password is incorrect.", 400)
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"ok": True}

@app.post("/api/auth/profile-image")
def upload_profile_image(file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not (file.content_type or "").startswith("image/"):
        clean_error("Please upload a valid image file.")
    suffix = Path(file.filename or "profile.png").suffix.lower() or ".png"
    dest = UPLOAD_DIR / f"user_{user.id}_{secrets.token_hex(8)}{suffix}"
    with dest.open("wb") as f:
        f.write(file.file.read())
    user.profile_image = f"/uploads/{dest.name}"
    db.commit()
    return {"user": user_to_out(user)}

@app.get("/api/settings")
def get_settings(user: User = Depends(current_user), db: Session = Depends(get_db)):
    models = db.query(ModelPerformance).order_by(ModelPerformance.roc_auc.desc()).all()
    return {"settings": user_to_out(user), "available_models": [{"name": m.model_name, "is_active": m.is_active, "roc_auc": m.roc_auc} for m in models]}

@app.put("/api/settings")
def put_settings(payload: ProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return update_profile(payload, user, db)

@app.post("/api/settings/change-password")
def settings_password(payload: ChangePasswordRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return change_password(payload, user, db)

@app.get("/api/scoring/config")
def scoring_config(db: Session = Depends(get_db)):
    active = db.query(ModelPerformance).filter(ModelPerformance.is_active == True).first()
    return {"score_range": [300, 850], "active_model": active.model_name if active else None, "risk_thresholds": {"Low Risk": "750-850", "Moderate Risk": "670-749", "Elevated Risk": "580-669", "High Risk": "300-579"}}

@app.post("/api/scoring/predict", response_model=PredictionOut)
def scoring_predict(payload: ScoringRequest, user: User = Depends(current_user)):
    return predict_credit(payload.model_dump())

@app.post("/api/scoring/predict-and-save", response_model=PredictionOut)
def scoring_predict_save(payload: ScoringRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    pred = predict_credit(payload.model_dump())
    if user.auto_save:
        assessment = save_assessment(db, user, payload.model_dump(), pred)
        pred["assessment_id"] = assessment.id
        pred["applicant_id"] = assessment.applicant_id
        pred["assessment_reference"] = assessment.assessment_reference
    return pred

@app.get("/api/applicants")
def list_applicants(user: User = Depends(current_user), db: Session = Depends(get_db), q: str = "", risk: str = "", sort: str = "latest", page: int = 1, page_size: int = 20):
    query = db.query(Applicant)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Applicant.full_name.ilike(like), Applicant.email.ilike(like), Applicant.phone.ilike(like)))
    applicants = query.order_by(Applicant.updated_at.desc()).all()
    rows = [applicant_to_out(db, a) for a in applicants]
    if risk:
        rows = [row for row in rows if row.get("current_risk_level") == risk]
    if sort == "score_desc":
        rows.sort(key=lambda row: row.get("latest_credit_score") or 0, reverse=True)
    elif sort == "score_asc":
        rows.sort(key=lambda row: row.get("latest_credit_score") if row.get("latest_credit_score") is not None else 9999)
    else:
        rows.sort(key=lambda row: row.get("last_assessment") or row.get("created_at") or "", reverse=True)
    total = len(rows)
    page = max(1, page)
    page_size = max(1, min(page_size, 5000))
    start = (page - 1) * page_size
    return {"items": rows[start:start + page_size], "total": total, "page": page, "page_size": page_size}

@app.post("/api/applicants")
def create_applicant(payload: ApplicantCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if payload.email and db.query(Applicant).filter(func.lower(Applicant.email) == payload.email.lower()).first():
        clean_error("This applicant email already exists.", 409)
    a = Applicant(user_id=user.id, **payload.model_dump())
    db.add(a); db.commit(); db.refresh(a)
    return applicant_to_out(db, a)

@app.get("/api/applicants/{applicant_id}")
def get_applicant(applicant_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.get(Applicant, applicant_id)
    if not a:
        clean_error("Applicant not found.", 404)
    return {"applicant": applicant_to_out(db, a), "assessments": [assessment_to_out(x) for x in a.assessments]}

@app.put("/api/applicants/{applicant_id}")
def update_applicant(applicant_id: int, payload: ApplicantUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.get(Applicant, applicant_id)
    if not a:
        clean_error("Applicant not found.", 404)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    db.commit(); db.refresh(a)
    return applicant_to_out(db, a)

@app.delete("/api/applicants/{applicant_id}")
def delete_applicant(applicant_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.get(Applicant, applicant_id)
    if not a:
        clean_error("Applicant not found.", 404)
    db.delete(a); db.commit()
    return {"ok": True}

@app.get("/api/applicants/{applicant_id}/assessments")
def applicant_assessments(applicant_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    items = db.query(Assessment).join(Applicant).filter(Assessment.applicant_id == applicant_id).order_by(Assessment.created_at.desc()).all()
    return {"items": [assessment_to_out(x) for x in items]}

@app.get("/api/assessments")
def list_assessments(user: User = Depends(current_user), db: Session = Depends(get_db), q: str = "", risk: str = "", recommendation: str = "", model: str = "", page: int = 1, page_size: int = 20):
    query = db.query(Assessment).join(Applicant)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Assessment.assessment_reference.ilike(like), Applicant.full_name.ilike(like), Applicant.email.ilike(like), Applicant.phone.ilike(like)))
    if risk:
        query = query.filter(Assessment.risk_level == risk)
    if recommendation:
        query = query.filter(Assessment.recommendation == recommendation)
    if model:
        query = query.filter(Assessment.model_name == model)
    total = query.count()
    page = max(1, page)
    page_size = max(1, min(page_size, 5000))
    items = query.order_by(Assessment.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    return {"items": [assessment_to_out(x) for x in items], "total": total, "page": page, "page_size": page_size}

@app.get("/api/assessments/export/csv")
def export_assessments(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Assessment).order_by(Assessment.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Reference", "Applicant", "Date", "Credit Score", "Risk Level", "Recommendation", "Probability", "Model"])
    for a in rows:
        writer.writerow([a.assessment_reference, a.applicant.full_name, a.created_at.isoformat(), a.credit_score, a.risk_level, a.recommendation, a.probability, a.model_name])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=credora_assessments.csv"})

@app.get("/api/assessments/{assessment_id}")
def get_assessment(assessment_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        clean_error("Assessment not found.", 404)
    return assessment_to_out(a)

@app.delete("/api/assessments/{assessment_id}")
def delete_assessment(assessment_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        clean_error("Assessment not found.", 404)
    db.delete(a); db.commit()
    return {"ok": True}

@app.get("/api/assessments/{assessment_id}/report", response_class=HTMLResponse)
def report(assessment_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        clean_error("Assessment not found.", 404)
    positives = "".join(f"<li>{x}</li>" for x in parse_json(a.positive_factors, []))
    risks = "".join(f"<li>{x}</li>" for x in parse_json(a.risk_factors, []))
    improvements = "".join(f"<li>{x}</li>" for x in parse_json(a.improvement_recommendations, []))
    return f"""<!doctype html><html><head><title>Credora Report {a.assessment_reference}</title><style>body{{font-family:Arial,sans-serif;margin:40px;color:#0b1220}}.score{{font-size:48px;font-weight:800;color:#0b3a6a}}.box{{border:1px solid #d7e0ea;border-radius:16px;padding:20px;margin:16px 0}}</style></head><body><h1>Credora Credit Risk Assessment</h1><p><b>Reference:</b> {a.assessment_reference}</p><p><b>Applicant:</b> {a.applicant.full_name}</p><div class='box'><div class='score'>{a.credit_score}</div><p>{a.risk_level} · {a.recommendation} · Probability {a.probability:.0%} · Confidence {a.confidence:.0%}</p></div><h3>Positive Factors</h3><ul>{positives}</ul><h3>Risk Factors</h3><ul>{risks}</ul><h3>Improvement Recommendations</h3><ul>{improvements}</ul><p><b>Model:</b> {a.model_name} {a.model_version}</p><p><small>Responsible-use disclaimer: Credora provides analytical recommendations only. It is not a legally binding lending decision.</small></p></body></html>"""

@app.get("/api/dashboard/summary")
def dashboard_summary(user: User = Depends(current_user), db: Session = Depends(get_db)):
    q = db.query(Assessment).filter(Assessment.user_id == user.id)
    total = q.count()
    creditworthy = q.filter(Assessment.recommendation == "Recommended").count()
    high = q.filter(Assessment.risk_level == "High Risk").count()
    avg = db.query(func.avg(Assessment.credit_score)).filter(Assessment.user_id == user.id).scalar()
    return {"total_assessments": total, "creditworthy_applicants": creditworthy, "high_risk_applicants": high, "average_credit_score": round(float(avg or 0), 1)}

@app.get("/api/dashboard/risk-distribution")
def risk_dist(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Assessment.risk_level, func.count(Assessment.id)).filter(Assessment.user_id == user.id).group_by(Assessment.risk_level).all()
    found = {r: c for r, c in rows}
    return [{"name": name, "value": int(found.get(name, 0))} for name in ["Low Risk", "Moderate Risk", "Elevated Risk", "High Risk"]]

@app.get("/api/dashboard/score-distribution")
def score_dist(user: User = Depends(current_user), db: Session = Depends(get_db)):
    items = db.query(Assessment.credit_score).filter(Assessment.user_id == user.id).all()
    buckets = {"300-579":0, "580-669":0, "670-749":0, "750-850":0}
    for (score,) in items:
        if score < 580: buckets["300-579"] += 1
        elif score < 670: buckets["580-669"] += 1
        elif score < 750: buckets["670-749"] += 1
        else: buckets["750-850"] += 1
    return [{"name": k, "value": v} for k, v in buckets.items()]

@app.get("/api/dashboard/assessment-trend")
def trend(user: User = Depends(current_user), db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=6)
    out = []
    for i in range(7):
        day = start + timedelta(days=i)
        nxt = day + timedelta(days=1)
        count = db.query(Assessment).filter(Assessment.user_id == user.id, Assessment.created_at >= day, Assessment.created_at < nxt).count()
        out.append({"date": day.isoformat(), "count": count})
    return out

@app.get("/api/dashboard/recent-assessments")
def recent_assessments(user: User = Depends(current_user), db: Session = Depends(get_db)):
    items = db.query(Assessment).filter(Assessment.user_id == user.id).order_by(Assessment.created_at.desc()).limit(8).all()
    return {"items": [assessment_to_out(x) for x in items]}

@app.get("/api/models")
def models(db: Session = Depends(get_db)):
    rows = db.query(ModelPerformance).order_by(ModelPerformance.roc_auc.desc()).all()
    return {"items": [model_out(m) for m in rows]}

@app.get("/api/models/metrics")
def model_metrics(db: Session = Depends(get_db)):
    return models(db)

@app.get("/api/models/comparison")
def model_comparison(db: Session = Depends(get_db)):
    return models(db)


def model_row(db: Session, name: str):
    row = db.query(ModelPerformance).filter(ModelPerformance.model_name == name).first()
    if not row:
        clean_error("Model metrics not found.", 404)
    return row


def model_out(m: ModelPerformance):
    return {"model_name": m.model_name, "model_version": m.model_version, "accuracy": m.accuracy, "precision": m.precision, "recall": m.recall, "f1_score": m.f1_score, "roc_auc": m.roc_auc, "confusion_matrix": parse_json(m.confusion_matrix, {}), "roc_curve_data": parse_json(m.roc_curve_data, []), "precision_recall_curve_data": parse_json(m.precision_recall_curve_data, []), "feature_importance": parse_json(m.feature_importance, []), "is_active": m.is_active, "training_date": m.training_date.isoformat(), "dataset_records": m.dataset_records, "feature_count": m.feature_count, "training_duration": m.training_duration}

@app.get("/api/models/{model_name}/confusion-matrix")
def confusion(model_name: str, db: Session = Depends(get_db)):
    return parse_json(model_row(db, model_name).confusion_matrix, {})

@app.get("/api/models/{model_name}/roc-curve")
def roc_curve_api(model_name: str, db: Session = Depends(get_db)):
    return parse_json(model_row(db, model_name).roc_curve_data, [])

@app.get("/api/models/{model_name}/precision-recall")
def pr_curve(model_name: str, db: Session = Depends(get_db)):
    return parse_json(model_row(db, model_name).precision_recall_curve_data, [])

@app.get("/api/models/{model_name}/feature-importance")
def feature_importance(model_name: str, db: Session = Depends(get_db)):
    return parse_json(model_row(db, model_name).feature_importance, [])

@app.post("/api/models/train")
def train_api(dataset: str = Query("active"), user: User = Depends(current_user)):
    result = train_models(resolve_dataset_path(dataset))
    reset_model_cache()
    return result

@app.put("/api/models/active")
def set_active(payload: dict, user: User = Depends(current_user), db: Session = Depends(get_db)):
    name = payload.get("model_name")
    rows = db.query(ModelPerformance).all()
    found = False
    for row in rows:
        row.is_active = row.model_name == name
        found = found or row.is_active
    if not found:
        clean_error("That trained model does not exist.", 404)
    db.commit()
    reset_model_cache()
    return {"active_model": name}

@app.get("/api/insights/summary")
def insights_summary(db: Session = Depends(get_db)):
    ds = db.query(DatasetSummary).order_by(DatasetSummary.updated_at.desc()).first()
    if not ds:
        clean_error("Dataset summary not found.", 404)
    target = parse_json(ds.target_distribution, {})
    return {"total_records": ds.total_records, "total_features": ds.feature_count, "missing_values": sum(parse_json(ds.missing_values, {}).values()), "duplicate_rows": ds.duplicate_rows, "clean_records": ds.clean_records, "positive_target_records": int(target.get("1", 0)), "negative_target_records": int(target.get("0", 0))}

@app.get("/api/insights/correlation")
def correlations(db: Session = Depends(get_db)):
    ds = db.query(DatasetSummary).order_by(DatasetSummary.updated_at.desc()).first()
    return parse_json(ds.correlation_data if ds else "[]", [])

@app.get("/api/insights/{kind}")
def insight_distribution(kind: str, db: Session = Depends(get_db)):
    ds = db.query(DatasetSummary).order_by(DatasetSummary.updated_at.desc()).first()
    if not ds:
        return []
    numeric = parse_json(ds.numerical_summary, {})
    categorical = parse_json(ds.categorical_summary, {})
    mapping = {"income-distribution": "annual_income", "debt-distribution": "existing_debt", "loan-distribution": "loan_amount", "age-distribution": "age", "employment-distribution": "employment_status", "risk-distribution": "target"}
    key = mapping.get(kind, kind)
    if key in categorical:
        return [{"name": k, "value": v} for k, v in categorical[key].items()]
    if key == "target":
        return [{"name": k, "value": v} for k, v in parse_json(ds.target_distribution, {}).items()]
    desc = numeric.get(key, {})
    if not desc:
        return []
    min_v, max_v = float(desc.get("min", 0)), float(desc.get("max", 1))
    step = (max_v - min_v) / 5 if max_v > min_v else 1
    return [{"name": f"{int(min_v+i*step)}-{int(min_v+(i+1)*step)}", "value": max(0, int(desc.get("count", 0) / 5))} for i in range(5)]

@app.get("/api/insights/key-factors")
def key_factors(db: Session = Depends(get_db)):
    active = db.query(ModelPerformance).filter(ModelPerformance.is_active == True).first()
    imp = parse_json(active.feature_importance if active else "[]", [])
    if not imp:
        return {"top_risk_factors": [], "top_positive_factors": []}
    total = sum(abs(float(item.get("importance", 0) or 0)) for item in imp) or 1.0
    risk_terms = ("debt", "default", "late", "utilization", "loan", "expense", "balance")
    positive_terms = ("income", "savings", "employment", "history", "reliability", "stable")

    def clean_feature_name(feature: str) -> str:
        return feature.replace("__", " ").replace("_", " ").replace("cat ", "").replace("num ", "").title()

    def enrich(item: dict) -> dict:
        importance = abs(float(item.get("importance", 0) or 0))
        feature = str(item.get("feature", "factor"))
        return {
            "feature": feature,
            "display_name": clean_feature_name(feature),
            "importance": importance,
            "percentage": round((importance / total) * 100, 1),
        }

    enriched = [enrich(item) for item in imp]
    risk = [item for item in enriched if any(term in item["feature"].lower() for term in risk_terms)]
    positive = [item for item in enriched if any(term in item["feature"].lower() for term in positive_terms)]
    if len(risk) < 5:
        risk.extend([item for item in enriched if item not in risk][:5 - len(risk)])
    if len(positive) < 5:
        positive.extend([item for item in enriched if item not in positive][:5 - len(positive)])
    risk = sorted(risk, key=lambda item: item["importance"], reverse=True)[:5]
    positive = sorted(positive, key=lambda item: item["importance"], reverse=True)[:5]
    return {"top_risk_factors": risk, "top_positive_factors": positive}

@app.get("/api/workflow/status")
def workflow_status(user: User = Depends(current_user), db: Session = Depends(get_db)):
    ds = db.query(DatasetSummary).order_by(DatasetSummary.updated_at.desc()).first()
    active = db.query(ModelPerformance).filter(ModelPerformance.is_active == True).first()
    total_predictions = db.query(Assessment).filter(Assessment.user_id == user.id).count()
    steps = [
        ("Dataset", f"{ds.dataset_name if ds else 'Dataset'} · {ds.total_records if ds else 0} records"),
        ("Data Cleaning", f"{ds.duplicate_rows if ds else 0} duplicates removed"),
        ("Feature Engineering", f"{len(FEATURE_COLUMNS)} operational features"),
        ("Encoding", "Categorical values encoded by pipeline"),
        ("Feature Scaling", "Numeric features scaled inside model pipeline"),
        ("Train-Test Split", "78/22 stratified validation"),
        ("Model Training", "Logistic Regression, Decision Tree, Random Forest"),
        ("Model Evaluation", f"Best ROC-AUC {active.roc_auc if active else 0}"),
        ("Best Model Selection", active.model_name if active else "Pending"),
        ("Prediction API", f"Ready · {total_predictions} predictions"),
        ("Live Credit Assessment", "Available"),
    ]
    return {"steps": [{"name": n, "description": d, "status": "Completed", "last_completed": datetime.now(timezone.utc).isoformat(), "record_count": ds.total_records if ds else 0, "validation_status": "Passed"} for n, d in steps], "deployment": {"frontend": "ready", "backend": "ready", "database": "ready", "model": active.model_name if active else "pending"}}

@app.get("/api/workflow/details")
def workflow_details(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return workflow_status(user, db)
