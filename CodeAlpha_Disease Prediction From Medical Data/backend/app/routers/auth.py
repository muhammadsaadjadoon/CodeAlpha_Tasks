from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..auth import (
    authenticate_user,
    clear_session_cookie,
    get_current_user,
    issue_session_cookie,
    register_runtime_user,
    update_runtime_user_profile,
)
from ..config import Settings, get_settings
from ..schemas import LoginRequest, LoginResponse, ProfileUpdateRequest, RegisterRequest, RegisterResponse, UserResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, settings: Settings = Depends(get_settings)):
    user = register_runtime_user(payload.full_name, str(payload.email), payload.password, settings)
    if user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    issue_session_cookie(response, user, settings)
    return RegisterResponse(user=user)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, settings: Settings = Depends(get_settings)):
    user = authenticate_user(str(payload.email), payload.password, settings)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    issue_session_cookie(response, user, settings)
    return LoginResponse(user=user)


@router.get("/me", response_model=UserResponse)
def me(user: UserResponse = Depends(get_current_user)):
    return user


@router.post("/profile", response_model=UserResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    response: Response,
    current_user: UserResponse = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    user = update_runtime_user_profile(
        current_user=current_user,
        display_name=payload.display_name,
        email=str(payload.email),
        settings=settings,
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="That email address is already in use")
    issue_session_cookie(response, user, settings)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, settings: Settings = Depends(get_settings)):
    clear_session_cookie(response, settings)
    return None
