from app.ml.service import score_from_probability, risk_level, predict_credit
from app.ml.features import engineer_features


def test_score_conversion_bounds():
    assert score_from_probability(0) == 300
    assert score_from_probability(1) == 850
    assert 300 <= score_from_probability(.52) <= 850


def test_risk_classification():
    assert risk_level(800) == "Low Risk"
    assert risk_level(700) == "Moderate Risk"
    assert risk_level(620) == "Elevated Risk"
    assert risk_level(520) == "High Risk"


def test_feature_engineering_safe_ratios():
    f = engineer_features({"annual_income": 0, "monthly_income": 0, "existing_debt": 1000, "monthly_expenses": 100})
    assert f["debt_to_income_ratio"] == 0
    assert f["expense_to_income_ratio"] == 0


def test_prediction_shape():
    result = predict_credit({
        "full_name":"Test User","email":"test@example.com","age":35,"annual_income":70000,"monthly_income":5800,
        "employment_status":"employed","employment_duration":5,"existing_debt":12000,"monthly_expenses":3000,"savings":10000,
        "loan_amount":15000,"loan_purpose":"personal","loan_term":36,"existing_loans":2,"credit_history_length":7,
        "previous_defaults":0,"late_payments":0,"payment_behaviour":"consistent","credit_utilization":.28,"outstanding_credit_balance":9000
    })
    assert "credit_score" in result
    assert 300 <= result["credit_score"] <= 850
    assert result["risk_level"] in {"Low Risk", "Moderate Risk", "Elevated Risk", "High Risk"}
