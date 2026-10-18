import random
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User
from app.schemas import (
    RegisterRequest,
    LoginRequest,
    VerifyOTPRequest,
    ResendOTPRequest,
    AuthResponse,
    UserResponse,
)
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.email import send_otp_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username is already taken")

    otp = generate_otp()
    expiry = int(time.time() * 1000) + (10 * 60 * 1000)  # 10 mins

    new_user = User(
        name=payload.name,
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        is_verified=False,
        otp_code=otp,
        otp_expiry=expiry,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    await send_otp_email(new_user.email, otp)
    token = create_access_token(new_user.id)
    return AuthResponse(token=token, user=UserResponse.model_validate(new_user))


@router.post("/verify-otp")
def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_time = int(time.time() * 1000)
    if user.otp_code != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if user.otp_expiry and current_time > user.otp_expiry:
        raise HTTPException(status_code=400, detail="OTP has expired")

    user.is_verified = True
    user.otp_code = None
    user.otp_expiry = None
    db.commit()

    token = create_access_token(user.id)
    return {"message": "Account verified successfully", "token": token}


@router.post("/resend-otp")
async def resend_otp(payload: ResendOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    user.otp_code = otp
    user.otp_expiry = int(time.time() * 1000) + (10 * 60 * 1000)
    db.commit()

    await send_otp_email(user.email, otp)
    return {"message": "Verification OTP sent"}


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first",
        )

    token = create_access_token(user.id)
    return AuthResponse(token=token, user=UserResponse.model_validate(user))
