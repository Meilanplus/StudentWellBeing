import secrets
from datetime import datetime, timedelta, timezone

import aiosmtplib
from email.message import EmailMessage
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.security import hash_password, verify_password, create_access_token, get_current_user
from app.permissions import require_manager, check_can_register_role, is_school_scoped_manager
from app.models.user import User
from app.models.rbac import Role
from app.models.geography import School
from app.models.i18n import Language
from app.constants import ALL_ROLES
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    UserOut,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RoleUpdateRequest,
    UpdateLanguagePreferenceRequest,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _user_to_out(user: User, db: Session) -> UserOut:
    school_name = None
    if user.school_id:
        school = db.query(School).filter(School.id == user.school_id).first()
        school_name = school.name if school else None
    lang_code = None
    if user.preferred_language_id:
        lang = db.query(Language).filter(Language.id == user.preferred_language_id).first()
        lang_code = lang.code if lang else None
    return UserOut(
        id=user.id,
        ic_number=user.ic_number,
        name=user.name,
        role=user.role.code,
        school_id=user.school_id,
        school_name=school_name,
        email=user.email,
        phone=user.phone,
        is_active=user.is_active,
        preferred_language_code=lang_code,
    )


@router.post("/register", status_code=201)
def register(req: RegisterRequest, requester: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.role not in ALL_ROLES:
        raise HTTPException(status_code=400, detail=f"Unknown role '{req.role}'.")

    school = db.query(School).filter(School.id == req.school_id).first()
    if not school:
        raise HTTPException(status_code=400, detail="Unknown school_id.")

    check_can_register_role(requester, req.role, req.school_id, db)

    ic_clean = req.ic_number.replace("-", "").strip()
    if db.query(User).filter(User.ic_number == ic_clean).first():
        raise HTTPException(status_code=409, detail="A user with this IC number already exists.")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=409, detail="A user with this email already exists.")

    role = db.query(Role).filter(Role.code == req.role).first()
    user = User(
        ic_number=ic_clean,
        name=req.name,
        role_id=role.id,
        school_id=req.school_id,
        email=req.email,
        phone=req.phone,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    return {"message": f"User '{req.name}' registered with role '{req.role}'."}


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    ic_clean = req.ic_number.replace("-", "").strip()
    user = db.query(User).filter(User.ic_number == ic_clean).first()
    if not user or not user.is_active or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid IC number or password.")

    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token(ic_number=user.ic_number, role_code=user.role.code, school_id=user.school_id)
    return LoginResponse(access_token=token, user=_user_to_out(user, db))


@router.get("/users", response_model=list[UserOut])
def list_users(requester: User = Depends(require_manager), db: Session = Depends(get_db)):
    query = db.query(User)
    if is_school_scoped_manager(requester.role_id, db):
        query = query.filter(User.school_id == requester.school_id)
    return [_user_to_out(u, db) for u in query.all()]


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    req: RoleUpdateRequest,
    requester: User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    if req.role not in ALL_ROLES:
        raise HTTPException(status_code=400, detail=f"Unknown role '{req.role}'.")
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")

    check_can_register_role(requester, req.role, target.school_id, db)

    role = db.query(Role).filter(Role.code == req.role).first()
    target.role_id = role.id
    db.commit()
    return {"message": f"Role updated.", "user_id": user_id, "role": req.role}


@router.patch("/me/language")
def update_my_language(
    req: UpdateLanguagePreferenceRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lang = db.query(Language).filter(Language.code == req.language_code, Language.is_active.is_(True)).first()
    if not lang:
        raise HTTPException(status_code=400, detail="Unknown or inactive language code.")
    user.preferred_language_id = lang.id
    db.commit()
    return {"message": "Language preference updated.", "language_code": lang.code}


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if user and user.is_active:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        reset_link = f"{settings.app_base_url}/reset-password?token={token}"
        await _send_reset_email(user.email, user.name, reset_link)
    # Always return a generic message — never leak whether the email exists.
    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == req.token).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset link.")
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    user.hashed_password = hash_password(req.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    return {"message": "Password has been reset. You may now log in."}


async def _send_reset_email(to_email: str, name: str, reset_link: str) -> None:
    if not settings.smtp_user or not settings.smtp_pass:
        print(f"[dev] Password reset link for {to_email}: {reset_link}")
        return

    message = EmailMessage()
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_user}>"
    message["To"] = to_email
    message["Subject"] = "Password Reset — Student Well-Being System"
    message.set_content(
        f"Hi {name},\n\nA password reset was requested for your account. "
        f"Click the link below to set a new password (valid for 1 hour):\n\n{reset_link}\n\n"
        f"If you did not request this, you can ignore this email."
    )
    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_pass,
        start_tls=True,
    )
