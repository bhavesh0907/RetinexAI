from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import RegisterRequest, LoginRequest
from app.core.security import verify_password, hash_password, create_access_token
from app.core.dependencies import get_current_user
from app.models.patient import Patient


router = APIRouter(tags=["Auth"])


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    if request.role == "admin":
        raise HTTPException(status_code=403, detail="Admin cannot be registered")

    role = "patient"

    new_user = User(
        email=request.email,
        password=hash_password(request.password),
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    last_patient = db.query(Patient).order_by(Patient.patient_id.desc()).first()
    new_patient_id = 1001 if not last_patient else last_patient.patient_id + 1

    if new_patient_id > 9999:
        raise HTTPException(status_code=400, detail="Patient ID limit reached")

    patient = Patient(
        patient_id=new_patient_id,
        user_id=new_user.id
    )

    db.add(patient)
    db.commit()

    return {
        "message": "User registered successfully",
        "patient_id": new_patient_id
    }


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db.execute(
        text("""
            UPDATE sessions 
            SET status='inactive' 
            WHERE user_id = :uid
        """),
        {"uid": user.id}
    )

    db.execute(
        text("""
            INSERT INTO sessions (user_id, login_time, last_active, status)
            VALUES (:uid, NOW(), NOW(), 'active')
        """),
        {"uid": user.id}
    )
    db.commit()

    patient_id = None

    if user.role == "patient":
        patient = db.query(Patient).filter(
            Patient.user_id == user.id
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        patient_id = patient.patient_id

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "patient_id": patient_id
    }


@router.post("/logout")
def logout(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    db.execute(
        text("UPDATE sessions SET status='inactive' WHERE user_id=:uid"),
        {"uid": current_user.id}
    )
    db.commit()
    return {"message": "Logged out"}


@router.post("/heartbeat")
def heartbeat(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    db.execute(
        text("""
            UPDATE sessions 
            SET last_active = NOW() 
            WHERE user_id=:uid AND status='active'
        """),
        {"uid": current_user.id}
    )
    db.commit()
    return {"message": "alive"}