# ======================================================
# IMPORTS
# ======================================================
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
import os
import hashlib
from datetime import datetime


from app.core.database import get_db
from app.models.screening import Screening
from app.models.patient import Patient
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.predict import predict_image
from app.utils.timezone import get_ist_time


# ======================================================
# ROUTER
# ======================================================
router = APIRouter(tags=["Screening"])


# ======================================================
# CONFIG
# ======================================================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ======================================================
# SCREEN IMAGE
# ======================================================
@router.post("/screen")
async def screen_image(
    name: str = Form(...),
    email: str = Form(...),
    sex: str = Form(...),
    age: int = Form(...),
    eye_side: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        print("🔥 SCREEN API CALLED")


        # =========================
        # 1. GET PATIENT FROM AUTH USER
        # =========================
        patient = db.query(Patient).filter(
            Patient.user_id == current_user.id
        ).first()


        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")


        patient_id = patient.patient_id


        if eye_side not in ["left", "right"]:
            raise HTTPException(
                status_code=400,
                detail="eye_side must be left or right"
            )


        # =========================
        # 2. SAFE FILE SAVE WITH HASH
        # =========================
        file_bytes = await file.read()
        file_hash = hashlib.md5(file_bytes).hexdigest()
        ext = file.filename.split(".")[-1]
        filename = f"{file_hash}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)


        if not os.path.exists(file_path):
            with open(file_path, "wb") as buffer:
                buffer.write(file_bytes)


        print("📁 Saved file:", file_path)


        # =========================
        # 3. DUPLICATE CHECK
        # =========================
        existing = db.query(Screening).filter(
            Screening.patient_id == patient_id,
            Screening.filename == filename
        ).first()


        if existing:
            print("⚠️ Duplicate detected, skipping insert")
            return {
                "success": True,
                "message": "Duplicate upload ignored",
                "prediction": existing.prediction,
                "confidence": existing.confidence,
                "probabilities": {}
            }


        # =========================
        # 4. RUN MODEL
        # =========================
        result = predict_image(file_path)


        print("🧠 Prediction Result:", result)


        prediction_label = str(result.get("label", "Unknown"))
        confidence = float(result.get("confidence", 0.0))


        # =========================
        # 5. SAVE TO DB
        # =========================
        new_screening = Screening(
            patient_id=patient_id,
            name=name,
            email=email,
            sex=sex,
            age=age,
            eye_side=eye_side,
            filename=filename,
            gradcam_path=None,
            prediction=prediction_label,
            confidence=confidence,
            created_at=get_ist_time(),
        )


        db.add(new_screening)
        db.commit()
        db.refresh(new_screening)


        # =========================
        # 6. RESPONSE
        # =========================
        return {
            "success": True,
            "message": "Screening completed",
            "prediction": prediction_label,
            "confidence": confidence,
            "probabilities": result.get("probabilities", {}),
        }


    except Exception as e:
        print("❌ ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))