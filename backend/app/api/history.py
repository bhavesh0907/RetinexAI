# ======================================================
# IMPORTS
# ======================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.screening import Screening
from app.core.dependencies import get_current_user
from app.models.user import User

# ======================================================
# ROUTER
# ======================================================
router = APIRouter(tags=["History"])

# ======================================================
# GET HISTORY
# ======================================================
@router.get("/")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        email = current_user.email

        records = (
            db.query(Screening)
            .filter(Screening.email == email)
            .order_by(Screening.created_at.desc())
            .all()
        )

        return {
            "success": True,
            "data": [
                {
                    "id": r.id,
                    "patient_id": r.patient_id,
                    "name": r.name,
                    "email": r.email,
                    "eye_side": r.eye_side,
                    "filename": r.filename,
                    "prediction": r.prediction,   # ✅ FIXED
                    "confidence": r.confidence,
                    "created_at": r.created_at
                }
                for r in records
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# GET SINGLE RECORD
# ======================================================
@router.get("/{id}")
def get_history_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        email = current_user.email

        record = (
            db.query(Screening)
            .filter(
                Screening.id == id,
                Screening.email == email
            )
            .first()
        )

        if not record:
            raise HTTPException(status_code=404, detail="Record not found")

        return {
            "success": True,
            "data": {
                "id": record.id,
                "patient_id": record.patient_id,
                "name": record.name,
                "email": record.email,
                "eye_side": record.eye_side,
                "filename": record.filename,
                "prediction": record.prediction,  # ✅ FIXED
                "confidence": record.confidence,
                "created_at": record.created_at
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))