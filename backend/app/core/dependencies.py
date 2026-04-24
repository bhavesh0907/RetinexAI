# ======================================================
# IMPORTS
# ======================================================
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

# ======================================================
# SECURITY SCHEME
# ======================================================
security = HTTPBearer()


# ======================================================
# GET CURRENT USER (AUTHENTICATION)
# ======================================================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    email = payload.get("sub")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# ======================================================
# 🔥 ADMIN ROLE CHECK (RBAC)
# ======================================================
def get_current_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return current_user


# ======================================================
# (OPTIONAL BACKWARD COMPATIBILITY)
# If you were using get_admin_user earlier
# ======================================================
def get_admin_user(
    current_user: User = Depends(get_current_user)
):
    return get_current_admin(current_user)