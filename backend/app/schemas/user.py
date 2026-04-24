from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "user"   # ✅ supports admin

class LoginRequest(BaseModel):
    email: EmailStr
    password: str