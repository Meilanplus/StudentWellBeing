from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    ic_number: str
    name: str
    role: str  # role code, e.g. "guru"
    school_id: int
    email: EmailStr
    phone: str
    password: str


class LoginRequest(BaseModel):
    ic_number: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserOut(BaseModel):
    id: int
    ic_number: str
    name: str
    role: str
    school_id: int | None
    school_name: str | None
    email: str
    phone: str
    is_active: bool
    preferred_language_code: str | None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class RoleUpdateRequest(BaseModel):
    role: str


class UpdateLanguagePreferenceRequest(BaseModel):
    language_code: str
