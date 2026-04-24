from typing import Optional, Dict
from datetime import datetime

from app.core.security import (
    verify_password,
    hash_password,
    create_access_token
)

# --------------------------------------------------
# TEMP USER STORE (RESEARCH / PROTOTYPE)
# --------------------------------------------------

fake_users_db = {
    "patient1": {
        "username": "patient1",
        "full_name": "Test Patient",
        "role": "patient",
        "hashed_password": hash_password("patient123"),
    },
    "doctor1": {
        "username": "doctor1",
        "full_name": "Dr. Retina",
        "role": "doctor",
        "hashed_password": hash_password("doctor123"),
    },
}

# --------------------------------------------------
# ACTIVE SESSION STORE (ADMIN FEATURE)
# --------------------------------------------------
# username -> session metadata
active_sessions = {}

# --------------------------------------------------
# AUTH LOGIC
# --------------------------------------------------

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Verify username & password.
    Returns user dict if valid, else None.
    """
    user = fake_users_db.get(username)

    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        return None

    return user


def login_user(username: str, password: str) -> Dict:
    """
    Authenticate user and return JWT token.
    """

    user = authenticate_user(username, password)
    if not user:
        raise ValueError("Invalid username or password")

    token_data = {
        "sub": user["username"],
        "role": user["role"],
    }

    access_token = create_access_token(token_data)

    # --------------------------------------------------
    # STORE ACTIVE SESSION (FOR ADMIN DASHBOARD)
    # --------------------------------------------------
    active_sessions[user["username"]] = {
        "role": user["role"],
        "login_time": datetime.now().isoformat()
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"],
    }


# --------------------------------------------------
# ADMIN HELPERS
# --------------------------------------------------

def get_active_sessions():
    return active_sessions