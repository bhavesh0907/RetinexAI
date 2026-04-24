from typing import Dict, Optional
from datetime import datetime
import tempfile
import os

from fpdf import FPDF
from PIL import Image as PILImage


def _save_temp_image(pil_img: PILImage.Image) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    pil_img.save(tmp, format="JPEG")
    tmp.close()
    return tmp.name


def create_pdf_report(
    patient_info: Dict[str, str],
    screening_report: Dict,
    original_img: PILImage.Image,
    heatmap_img: Optional[PILImage.Image] = None,
    user_role: str = "unknown",
) -> bytes:

    # ---------------- PATIENT INFO ----------------
    name = (patient_info.get("name") or "").strip() or "Not provided"
    patient_id = str(patient_info.get("patient_id") or "").strip() or "Not provided"
    age = str(patient_info.get("age") or "").strip() or "Not provided"
    sex = (patient_info.get("sex") or "").strip() or "Not provided"
    eye_side = (patient_info.get("eye_side") or "").strip() or "Not specified"
    image_quality = (patient_info.get("image_quality") or "").strip() or "Not recorded"

    # ---------------- SCREENING INFO ----------------
    pred_class = (
        screening_report.get("prediction")
        or screening_report.get("predicted_condition")
        or screening_report.get("predicted_class")
    )

    probs = screening_report.get("probabilities", {}) or {}

    # fallback from probabilities
    if not pred_class or pred_class == "Unknown":
        if probs:
            pred_class = max(probs, key=probs.get)
        else:
            pred_class = "Unknown"

    confidence = screening_report.get("confidence", 0.0)

    if isinstance(confidence, str):
        confidence = float(confidence.replace("%", ""))

    risk = screening_report.get("risk", "Unknown")
    uncertainty = screening_report.get("uncertainty", "Unknown")
    next_steps = screening_report.get("next_steps", []) or []

    # ---------------- TEMP IMAGES ----------------
    orig_path = _save_temp_image(original_img)
    heatmap_path = _save_temp_image(heatmap_img) if heatmap_img else None

    # ---------------- PDF INIT ----------------
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    page_width = pdf.w
    left_margin = 10
    content_width = page_width - 20

    # ---------------- HEADER ----------------
    pdf.set_fill_color(12, 75, 142)
    pdf.rect(0, 0, page_width, 25, "F")

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(left_margin, 7)
    pdf.cell(0, 8, "RetinexAI - Fundus Screening Report", ln=1)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(left_margin)
    pdf.cell(
        0,
        6,
        "Research prototype - Automated Retinal Fundus Image Screening (Not a Diagnosis)",
        ln=1,
    )

    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # ---------------- PATIENT INFO ----------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Patient Information", ln=1)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"Patient ID: {patient_id}", ln=1)
    pdf.cell(0, 5, f"Name: {name}", ln=1)
    pdf.cell(0, 5, f"Age: {age}    Sex: {sex}", ln=1)
    pdf.cell(0, 5, f"Eye screened: {eye_side}", ln=1)
    pdf.cell(0, 5, f"Image quality: {image_quality}", ln=1)
    pdf.cell(
        0,
        5,
        f"Screening time: {datetime.now().strftime('%d %b %Y  %I:%M %p')}",
        ln=1,
    )

    pdf.ln(4)

    # ---------------- AI SUMMARY ----------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "AI Screening Summary", ln=1)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"Predicted condition: {pred_class}", ln=1)
    pdf.cell(0, 5, f"Model confidence: {confidence:.2f}% ({uncertainty})", ln=1)
    pdf.cell(0, 5, f"Estimated risk level: {risk}", ln=1)

    pdf.ln(4)

    # ---------------- NEXT STEPS ----------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Recommended next steps for patient", ln=1)

    pdf.set_font("Helvetica", "", 10)

    if next_steps:
        pdf.ln(2)

        for step in next_steps:
            safe_text = str(step).strip().replace("–", "-").replace("—", "-")

            x_start = pdf.get_x()

            # bullet + text
            pdf.multi_cell(content_width, 5, f"- {safe_text}")

            # reset X after multicell (CRITICAL FIX)
            pdf.set_x(x_start)

            pdf.ln(1)

    else:
        pdf.multi_cell(
            content_width,
            5,
            "Please consult a qualified eye specialist to interpret and confirm this result.",
        )

    pdf.ln(3)

    # ---------------- PROBABILITY TABLE ----------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Class probabilities", ln=1)

    pdf.set_font("Helvetica", "", 10)

    if probs:

        pdf.set_fill_color(220, 230, 245)
        pdf.cell(80, 7, "Condition", border=1, fill=True)
        pdf.cell(40, 7, "Probability", border=1, fill=True)
        pdf.cell(40, 7, "Percentage", border=1, ln=1, fill=True)

        sorted_items = sorted(probs.items(), key=lambda x: x[1], reverse=True)

        percentages = [round(p * 100, 2) for _, p in sorted_items]

        # fix rounding drift
        diff = 100.0 - sum(percentages)
        if percentages:
            percentages[0] += diff

        for (cond, p), pct in zip(sorted_items, percentages):
            pdf.cell(80, 7, cond, border=1)
            pdf.cell(40, 7, f"{p:.4f}", border=1)
            pdf.cell(40, 7, f"{pct:.2f}%", border=1, ln=1)

    else:
        pdf.cell(0, 5, "No probability breakdown available from model.", ln=1)

    pdf.ln(4)

    # ---------------- IMAGES ----------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Fundus image and Grad-CAM heatmap", ln=1)

    # Ensure enough space
    required_space = 100
    if pdf.get_y() + required_space > pdf.h - 15:
        pdf.add_page()

    y = pdf.get_y() + 3

    # Draw images
    pdf.image(orig_path, x=left_margin, y=y, w=80, h=80)

    if heatmap_path:
        pdf.image(heatmap_path, x=left_margin + 90, y=y, w=80, h=80)

    # Move BELOW images properly
    caption_y = y + 85   # 🔥 CRITICAL FIX (was too small before)

    pdf.set_font("Helvetica", "", 9)

    # LEFT CAPTION
    pdf.set_xy(left_margin, caption_y)
    pdf.multi_cell(
        80,
        4,
        "Left: uploaded fundus photograph."
    )

    # RIGHT CAPTION (aligned with same Y)
    pdf.set_xy(left_margin + 90, caption_y)
    pdf.multi_cell(
        80,
        4,
        "Right: Grad-CAM heatmap showing the regions that contributed most to the model's prediction."
)

    # Move cursor below captions safely
    pdf.set_y(caption_y + 12)
    pdf.ln(4)

    # ---------------- DISCLAIMER ----------------
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Important limitations", ln=1)

    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(
    0,
    5,
    "- This is a screening tool and not a definitive medical diagnosis.\n"
    "- Results depend on image quality and may be unreliable for poor-quality images.\n"
    "- The model may not generalize across different devices, populations, or settings.\n"
    "- The system is limited to four conditions and cannot detect other ocular diseases.\n"
    "- If the patient has pain, sudden vision loss, flashes, or floaters, urgent ophthalmic evaluation is required regardless of this report."
)   
    
    pdf.ln(6)

    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(80, 80, 80)

    pdf.multi_cell(
        0,
        4,
        "* This result is generated by a convolutional neural network trained on retinal fundus images. "
        "It should be interpreted only as a screening output and not as a final medical diagnosis. "
        "Please correlate with clinical examination.",
    )

    pdf.set_text_color(0, 0, 0)

    # ---------------- FOOTER ----------------
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(120, 120, 120)

    pdf.cell(
        0,
        4,
        f"AI RetinoCare | Research Use Only | Role: {user_role} | Patient ID: {patient_id} | "
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ln=1,
    )

    pdf.set_text_color(0, 0, 0)

    # ---------------- OUTPUT ----------------
    pdf_str = pdf.output(dest="S")

    if isinstance(pdf_str, bytearray):
        pdf_bytes = bytes(pdf_str)
    elif isinstance(pdf_str, bytes):
        pdf_bytes = pdf_str
    else:
        pdf_bytes = pdf_str.encode("latin-1", errors="ignore")

    try:
        os.remove(orig_path)
        if heatmap_path:
            os.remove(heatmap_path)
    except OSError:
        pass

    return pdf_bytes