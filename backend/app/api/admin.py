from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import io

from app.core.database import get_db
from app.models.screening import Screening
from app.models.user import User
from app.core.dependencies import get_current_admin
from app.models.patient import Patient

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

router = APIRouter(tags=["Admin"])

@router.get("/patient/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    records = db.query(Screening).filter(Screening.patient_id == patient_id).all()

    if not records:
        raise HTTPException(status_code=404, detail="Patient not found")

    first = records[0]

    return {
        "patient_id": patient_id,
        "name": first.name,
        "email": first.email,
        "sex": getattr(first, "sex", None),
        "age": getattr(first, "age", None),
        "records": [
            {
                "id": r.id,
                "filename": r.filename,
                "eye_side": r.eye_side,
                "prediction": r.prediction,
                "confidence": r.confidence,
                "created_at": r.created_at,
            }
            for r in records
        ]
    }

@router.get("/files")
def get_files(search: str = "", db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    query = db.query(Screening)

    if search:
        query = query.filter(Screening.filename.contains(search))

    return {
        "data": [
            {
                "id": s.id,
                "patient_id": s.patient_id,
                "name": s.name,
                "email": s.email,
                "eye_side": s.eye_side,
                "filename": s.filename,
                "prediction": s.prediction,
                "confidence": s.confidence,
                "created_at": s.created_at
            }
            for s in query.order_by(Screening.created_at.desc()).all()
        ]
    }

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return {
        "total_users": db.query(User).filter(User.role == "patient").count(),
        "total_scans": db.query(Screening).count()
    }

@router.get("/activity")
def get_activity(
    patient_id: int = None,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    query = db.query(Screening)

    if patient_id:
        query = query.filter(Screening.patient_id == patient_id)

    logs = query.order_by(Screening.created_at.desc()).all()

    return {
        "data": [
            {
                "id": l.id,
                "patient_id": l.patient_id,
                "prediction": l.prediction,
                "confidence": l.confidence,
                "time": l.created_at
            }
            for l in logs
        ]
    }

@router.get("/active-users")
def active_users(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    result = db.execute(text("""
        SELECT 
            s.user_id,
            MAX(s.login_time) AS login_time,
            MAX(s.last_active) AS last_active
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.status = 'active'
        AND u.role = 'patient'
        GROUP BY s.user_id
    """)).fetchall()

    return {"data": [dict(r._mapping) for r in result]}

@router.get("/users")
def get_users(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    result = db.execute(text("""
        SELECT 
            u.id,
            u.email,
            u.role,
            COALESCE((
                SELECT s.status
                FROM sessions s
                WHERE s.user_id = u.id
                ORDER BY s.last_active DESC
                LIMIT 1
            ), 'inactive') AS status
        FROM users u
    """)).fetchall()

    return [dict(r._mapping) for r in result]

@router.get("/sessions")
def sessions(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    result = db.execute(text("""
        SELECT s.id, s.user_id, u.email, s.login_time, s.last_active, s.status
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE u.role = 'patient'
        ORDER BY s.login_time DESC
    """)).fetchall()

    return {"data": [dict(r._mapping) for r in result]}

@router.get("/report/{id}")
def generate_report(id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    record = db.query(Screening).filter(Screening.id == id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    os.makedirs("reports", exist_ok=True)
    file_path = f"reports/report_{id}.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>RetinexAI - Fundus Screening Report</b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Patient Information</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Patient ID: {record.patient_id}", styles["Normal"]))
    elements.append(Paragraph(f"Name: {record.name}", styles["Normal"]))
    elements.append(Paragraph(f"Email: {record.email}", styles["Normal"]))
    elements.append(Paragraph(f"Eye: {record.eye_side}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {record.created_at}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>AI Summary</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Prediction: {record.prediction}", styles["Normal"]))
    elements.append(Paragraph(f"Confidence: {round(record.confidence * 100, 2)}%", styles["Normal"]))
    elements.append(Spacer(1, 20))

    table = Table([
        ["Condition", "Probability"],
        [record.prediction, f"{round(record.confidence * 100, 2)}%"]
    ])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    fundus_path = f"uploads/{record.filename}"
    gradcam_path = record.gradcam_path
    imgs = []

    if os.path.exists(fundus_path):
        imgs.append(Image(fundus_path, width=2.5 * inch, height=2.5 * inch))

    if gradcam_path and os.path.exists(gradcam_path):
        imgs.append(Image(gradcam_path, width=2.5 * inch, height=2.5 * inch))

    if imgs:
        elements.append(Table([imgs]))

    doc.build(elements)

    return FileResponse(file_path, media_type="application/pdf", filename=f"report_{id}.pdf")

@router.post("/force-logout/{session_id}")
def force_logout(session_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    db.execute(
        text("UPDATE sessions SET status='inactive' WHERE id=:sid"),
        {"sid": session_id}
    )
    db.commit()
    return {"message": "terminated"}

@router.delete("/cleanup/{id}")
def delete_screening(id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    screening = db.query(Screening).filter(Screening.id == id).first()

    if not screening:
        raise HTTPException(status_code=404, detail="Record not found")

    if os.path.exists(f"uploads/{screening.filename}"):
        os.remove(f"uploads/{screening.filename}")

    if screening.gradcam_path and os.path.exists(screening.gradcam_path):
        os.remove(screening.gradcam_path)

    db.delete(screening)
    db.commit()

    return {"message": "Deleted"}