from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.screening import Screening
from app.models.user import User

router = APIRouter(tags=["Dashboard"])

@router.get("")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_email = current_user.email

    user_records = db.query(Screening).filter(
        Screening.email == user_email   # ✅ FIXED
    ).all()

    total_scans = len(user_records)

    disease_counts = {}
    for record in user_records:
        label = record.prediction   # ✅ FIXED
        disease_counts[label] = disease_counts.get(label, 0) + 1

    return {
        "success": True,
        "message": "Dashboard fetched",
        "data": {
            "user_email": user_email,
            "total_scans": total_scans,
            "disease_distribution": disease_counts,
            "recent_records": [
                {
                    "id": r.id,
                    "filename": r.filename,
                    "prediction": r.prediction,   # ✅ FIXED
                    "confidence": r.confidence,
                    "created_at": r.created_at
                }
                for r in user_records[-5:]
            ]
        }
    }