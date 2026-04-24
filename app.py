# --------------------------------------------------
# IMPORTS (FIXED)
# --------------------------------------------------
import os
import json 
import cv2  
import numpy as np 
from datetime import datetime
import requests # Required for Auth backend calls
import streamlit as st
from PIL import Image
import pandas as pd

# Grad-CAM
from src.grad_cam import generate_grad_cam

# PDF + Screening Report
from src.report_utils import create_pdf_report

# ---------------- AUTH + SESSION INIT ----------------
if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.role = None

from datetime import timedelta

if "login_time" not in st.session_state:
    st.session_state.login_time = None

if "patient_info" not in st.session_state:
    st.session_state.patient_info = None

if "patient_id" not in st.session_state:
    st.session_state.patient_id = None

if "prediction_done" not in st.session_state:
    st.session_state.prediction_done = False

if "result" not in st.session_state:
    st.session_state.result = None


SESSION_TIMEOUT_MINUTES = 30

# --------------------------------------------------
# NEW FEATURE LOGIC (UTILITIES)
# --------------------------------------------------



# -------- AUDIT LOGGING --------
def log_action(action, extra=None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user_role": st.session_state.role,
        "patient_id": st.session_state.patient_info.get("patient_id"),
        "action": action,
        "extra": extra,
    }
    with open("audit_log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")

if "history" not in st.session_state:
    st.session_state.history = []

def image_quality_check(pil_img):
    gray = np.array(pil_img.convert("L"))
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = gray.mean()
    issues = []
    if blur < 60: issues.append("Blurry image")
    if brightness < 40: issues.append("Low brightness")
    return issues

def generate_lesion_map(heatmap_img):
    heat = np.array(heatmap_img.convert("L"))
    _, mask = cv2.threshold(heat, 160, 255, cv2.THRESH_BINARY)
    return Image.fromarray(mask)


# -------- PROBABILITY SANITIZER --------
def sanitize_probabilities(probs_dict):
    clean_probs = {}

    for k, v in probs_dict.items():
        try:
            v = float(v)
            if np.isnan(v) or np.isinf(v):
                v = 0.0
        except:
            v = 0.0
        clean_probs[k] = v

    total = sum(clean_probs.values())

    if total == 0:
        n = len(clean_probs)
        return {k: 1.0 / n for k in clean_probs}

    return {k: v / total for k, v in clean_probs.items()}



# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="RetinexAI – Fundus Screening",
    page_icon="👁️",
    layout="wide",
)

# ✅ BACKEND URL (FIX #1)
from src.report_utils import create_pdf_report
from src.report import build_screening_report

BACKEND_URL = "http://127.0.0.1:8000"



# --------------------------------------------------
# LOGIN PAGE (THEME MATCHED)
# --------------------------------------------------
if st.session_state.token is None:

    st.markdown("""
    <style>

    /* BACKGROUND (ONLY FOR LOGIN PAGE) */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top left, #0AA1DD, #0C4B8E, #000000);
    }

    /* REMOVE DEFAULT BLOCK UI */
    [data-testid="stVerticalBlock"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* INPUT */
    input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
        border-radius: 10px !important;
    }

    /* BUTTON */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        padding: 10px;
        font-weight: 500;
        border: none;
        background: linear-gradient(135deg,#3b82f6,#9333ea);
        color: white;
        transition: 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        opacity: 0.9;
    }

    /* CARD */
    .login-card {
        max-width: 420px;
        margin: 3rem auto;
        padding: 2.5rem;
        border-radius: 18px;

        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(14px);

        border: 1px solid rgba(255,255,255,0.1);

        box-shadow:
            0 0 25px rgba(0,195,255,0.25),
            0 0 60px rgba(0,195,255,0.15);
    }

    .login-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
    }

    .login-sub {
        text-align: center;
        font-size: 0.85rem;
        opacity: 0.7;
        margin-bottom: 1.5rem;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-card">
        <div class="login-title">🔐 RetinexAI</div>
        <div class="login-sub">Secure Clinical Screening Platform</div>
    """, unsafe_allow_html=True)

    username = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        resp = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json={"email": username, "password": password},
        )

        if resp.status_code == 200:
            data = resp.json()
            st.session_state.token = data["access_token"]
            st.session_state.role = data["role"]
            st.session_state.login_time = datetime.now()
            st.session_state.email = username
            st.session_state.patient_id = data.get("patient_id")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# --------------------------------------------------
# SESSION CHECK
# --------------------------------------------------
if st.session_state.login_time:
    elapsed = datetime.now() - st.session_state.login_time
    remaining = timedelta(minutes=SESSION_TIMEOUT_MINUTES) - elapsed

    if remaining.total_seconds() <= 0:
        st.warning("Session expired")
        st.session_state.clear()
        st.rerun()

    elif remaining.total_seconds() < 300:
        st.warning("Session expires in less than 5 minutes")


# --------------------------------------------------
# PATIENT REGISTRATION (THEME MATCHED)
# --------------------------------------------------
if "patient_info" not in st.session_state:
    st.session_state.patient_info = None

if st.session_state.patient_info is None:

    st.markdown("""
    <style>

    /* SAME BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top left, #0AA1DD, #0C4B8E, #000000);
    }

    /* REMOVE BLOCK UI */
    [data-testid="stVerticalBlock"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* INPUT */
    input, select {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
        border-radius: 10px !important;
    }

    /* BUTTON */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        padding: 10px;
        font-weight: 500;
        border: none;
        background: linear-gradient(135deg,#3b82f6,#9333ea);
        color: white;
    }

    /* CARD */
    .patient-card {
        max-width: 560px;
        margin: 2rem auto;
        padding: 1.5rem;

        border-radius: 18px;

        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(14px);

        border: 1px solid rgba(255,255,255,0.1);

        box-shadow:
            0 0 25px rgba(0,195,255,0.2),
            0 0 50px rgba(0,195,255,0.1);
    }

    .patient-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: white;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="patient-card">', unsafe_allow_html=True)
    st.markdown('<div class="patient-title">🧾 Patient Registration</div>', unsafe_allow_html=True)

    with st.form("patient_form"):
        name = st.text_input("Patient Name")
        age = str(st.number_input("Age", min_value=0, max_value=120))
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        eye = st.selectbox("Eye", ["Right", "Left"])

        submit = st.form_submit_button("Continue")

    if submit:
        if not name:
            st.error("All fields are mandatory")
        else:
            st.session_state.patient_info = {
                "name": name,
                "age": age,
                "sex": sex,
                "eye_side": eye.lower(),
            }
            st.success("Patient details saved")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --------------------------------------------------
# CUSTOM CSS (Deep Space Retina Glow)
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* Main background */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top left, #0AA1DD, #0C4B8E, #000000);
        color: #F5F7FA;
    }



    /* Reduce max width for nicer layout */
    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }



    /* Top navigation bar */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 1.25rem;
        border-radius: 16px;
        background: rgba(7, 18, 43, 0.9);
        border: 1px solid rgba(0, 195, 255, 0.35);
        box-shadow: 0 0 25px rgba(0, 195, 255, 0.25);
        margin-bottom: 1.2rem;
    }



    .topbar-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }



    .logo-circle {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        background: radial-gradient(circle, #00C3FF, #004F9E);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 25px rgba(0, 195, 255, 0.8);
        color: white;
        font-size: 26px;
        font-weight: bold;
    }



    .top-title {
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }



    .top-caption {
        font-size: 0.80rem;
        opacity: 0.8;
    }



    .topbar-right {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }



    .pill-btn {
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-size: 0.80rem;
        border: 1px solid rgba(0, 195, 255, 0.4);
        background: rgba(14, 26, 56, 0.9);
        color: #F5F7FA;
        text-decoration: none;
    }
    .pill-btn span {
        opacity: 0.85;
    }
    .pill-btn:hover {
        background: rgba(0, 195, 255, 0.12);
        box-shadow: 0 0 15px rgba(0, 195, 255, 0.5);
        border-color: rgba(0, 195, 255, 0.8);
    }



    /* Cards */
    [data-testid="stVerticalBlock"] > div {
        background: rgba(9, 20, 45, 0.85);
        border-radius: 18px;
        padding: 1.2rem 1.3rem 1.0rem 1.3rem;
        border: 1px solid rgba(0, 195, 255, 0.06);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.55);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        margin-bottom: 1.1rem;
    }



    h3, h4 {
        font-weight: 700;
    }



    .section-caption {
        font-size: 0.82rem;
        opacity: 0.8;
    }



    .info-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        font-size: 0.70rem;
        border: 1px solid rgba(0, 195, 255, 0.5);
        background: rgba(0, 195, 255, 0.1);
        margin-bottom: 0.25rem;
    }



    .risk-pill-low {
        background: rgba(46, 204, 113, 0.15);
        border: 1px solid rgba(46, 204, 113, 0.65);
        color: #2ecc71;
        padding: 0.1rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
    }
    .risk-pill-medium {
        background: rgba(241, 196, 15, 0.15);
        border: 1px solid rgba(241, 196, 15, 0.75);
        color: #f1c40f;
        padding: 0.1rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
    }
    .risk-pill-high {
        background: rgba(231, 76, 60, 0.15);
        border: 1px solid rgba(231, 76, 60, 0.8);
        color: #e74c3c;
        padding: 0.1rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
    }



    .pdf-btn {
        border-radius: 999px;
    }



    table {
        color: #F5F7FA;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)




# --------------------------------------------------
# TOP BAR
# --------------------------------------------------
st.markdown(
    """
    <div class="topbar">
        <div class="topbar-left">
            <div class="logo-circle">👁️</div>
            <div>
                <div class="top-title">RetinexAI</div>
                <div class="top-caption">
                    An Automated Fundus Image Screening With Grad-CAM Explainability
                </div>
            </div>
        </div>
        <div class="topbar-right">
            <a class="pill-btn" href="#screening-section"><span>Screening</span></a>
            <a class="pill-btn" href="#report-section"><span>Report</span></a>
            <a class="pill-btn" href="#about-section"><span>About Project</span></a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)



# -------- TOP RIGHT LOGOUT --------
profile_col1, profile_col2 = st.columns([0.85, 0.15])



with profile_col2:
    if st.button("👤", key="profile_icon"):
        st.session_state.show_profile = not st.session_state.get("show_profile", False)



    if st.session_state.get("show_profile", False):
        st.info(st.session_state.patient_info["name"])



        if st.button("Logout", key="profile_logout"):
            st.session_state.clear()
            st.rerun()



# 🧑‍⚕️ STEP 4 — Role-based access Info
if st.session_state.role == "doctor":
    st.info("Doctor access enabled")
elif st.session_state.role == "patient":
    st.info("Patient access enabled")




st.markdown(
    """
    <span class="section-caption">
    Upload a retinal fundus photograph to obtain an AI-generated screening summary for  
    <b>Normal, Cataract, Glaucoma, Diabetic Retinopathy</b>.  
    This tool is for research and educational use only.
    </span>
    """,
    unsafe_allow_html=True,
)



st.markdown('<a id="screening-section"></a>', unsafe_allow_html=True)



# --------------------------------------------------
# INPUT COLUMNS
# --------------------------------------------------
col_left, col_right = st.columns([0.42, 0.58])



# ---------------- LEFT SIDE ----------------
with col_left:
    st.markdown("### 1. Upload Fundus Image and Patient Info")



    uploaded_file = st.file_uploader(
        "Upload a color fundus photograph (JPG / JPEG / PNG)",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file:
        st.session_state.prediction_done = False
        st.session_state.result = None




# ---------------- RIGHT SIDE ----------------
pred_result = None
probs = {}
heatmap_img = None



with col_right:
    st.markdown("### 2. Image Quality and Model Attention")



    if uploaded_file is None:
        st.info("Upload a fundus image on the left to start screening.")
    else:
        image = Image.open(uploaded_file).convert("RGB")



        # FEATURE ADDED: Image Quality Check
        quality_issues = image_quality_check(image)



        if quality_issues:
            st.session_state.patient_info["image_quality"] = "Poor"
            for issue in quality_issues:
                st.warning(f"⚠ {issue}")
        else:
            st.session_state.patient_info["image_quality"] = "Good"
            st.success("✅ Image quality acceptable")



        img_col1, img_col2 = st.columns(2)
        with img_col1:
            st.caption("Original Fundus Image")
            st.image(image, use_container_width=True)



        with img_col2:
            st.caption("Grad-CAM Heatmap (Model Attention)")
            try:
                heatmap_img = generate_grad_cam(image)
                st.image(heatmap_img, use_container_width=True)
            except Exception as e:
                heatmap_img = None
                st.warning(f"Grad-CAM not available: {e}")



        with st.spinner("Running AI model..."):

            if not st.session_state.prediction_done:
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")
                }



                data = {
                    "name": st.session_state.patient_info["name"],
                    "email": st.session_state.email,
                    "eye_side": st.session_state.patient_info["eye_side"].lower(),
                    "sex": st.session_state.patient_info["sex"],
                    "age": int(st.session_state.patient_info["age"])
                }



                headers = {
                    "Authorization": f"Bearer {st.session_state.token}"
                }



                response = requests.post(
                    f"{BACKEND_URL}/api/v1/screening/screen",
                    files=files,
                    data=data,
                    headers=headers
                )



                if response.status_code != 200:
                    st.error(response.text)
                    st.stop()



                st.session_state.result = response.json()
                st.session_state.prediction_done = True



            result = st.session_state.result



            pred_class = result.get("prediction")
            confidence = result.get("confidence", 0)



            classes = ["diabetic_retinopathy", "glaucoma", "cataract", "normal"]



            probabilities = {}
            for cls in classes:
                if cls == pred_class:
                    probabilities[cls] = confidence
                else:
                    probabilities[cls] = (1 - confidence) / (len(classes) - 1)



            pred_result = {
                "predicted_class": pred_class,
                "confidence": confidence,
                "probabilities": probabilities
            }



            probs = pred_result["probabilities"]




# --------------------------------------------------
# AI SCREENING REPORT
# --------------------------------------------------
st.markdown('<a id="report-section"></a>', unsafe_allow_html=True)
st.markdown("### 3. AI Screening Report")



if uploaded_file is None or pred_result is None:
    st.info("Upload an image to view the AI screening report.")



else:



    pred_class_raw = pred_result.get("predicted_class", "unknown")



    pred_class = (
        pred_class_raw
        .strip()
        .lower()
        .replace(" ", "_")
    )



    # ✅ ADD THIS
    display_map = {
        "diabetic_retinopathy": "Diabetic Retinopathy",
        "glaucoma": "Glaucoma",
        "cataract": "Cataract",
        "normal": "Normal"
    }



    display_class = display_map.get(pred_class, pred_class)
    confidence_raw = float(pred_result.get("confidence", 0.0))



    # Fix scaling issue (0–1 → 0–100)
    if confidence_raw <= 1:
        confidence_pct = confidence_raw * 100
    else:
        confidence_pct = confidence_raw
    sex = st.session_state.patient_info.get("sex", "Unknown")



    if confidence_pct >= 90:
        level = "critical"
    elif confidence_pct >= 75:
        level = "high"
    elif confidence_pct >= 60:
        level = "moderate"
    elif confidence_pct >= 40:
        level = "low"
    else:
        level = "very_low"




    # -------------------------------
    # Recommendation Logic
    # -------------------------------



    base_steps = []
    sex_steps = []



    if pred_class == "diabetic_retinopathy":



        if level == "critical":
            base_steps = [
                "Immediate retina specialist referral within 24–48 hours is recommended. " ,
                "Perform optical coherence tomography (OCT) to evaluate macular edema and fundus fluorescein angiography (FFA) to assess retinal ischemia, microaneurysms, and neovascularization for accurate disease staging."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should undergo detailed evaluation for pregnancy-associated progression and increased risk of macular edema."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be assessed for aggressive proliferative changes and extent of retinal microvascular damage."
                ]



        elif level == "high":
            base_steps = [
                    "Early retina specialist consultation within one week is advised. " , 
                    "Perform baseline OCT imaging and fundus photography to document microaneurysms, hemorrhages, and early neovascular changes for classification of disease severity."
                ]



            if sex == "Female":
                    sex_steps = [
                        "Female patients should be monitored for increased susceptibility to retinal fluid accumulation and macular thickening."
                    ]
            elif sex == "Male":
                    sex_steps = [
                        "Male patients should be evaluated for early proliferative retinopathy indicators and ischemic retinal areas."
                    ]



        elif level == "moderate":  
            base_steps = [
                    "Follow-up evaluation within 1–3 months is recommended. " ,
                    "Repeat OCT and fundus imaging to monitor progression of microaneurysms, intraretinal hemorrhages, and lipid exudates."
                ]



            if sex == "Female":
                    sex_steps = [
                        "Female patients should be assessed for progression of macular edema and subtle retinal thickening."
                    ]
            elif sex == "Male":
                    sex_steps = [
                        "Male patients should be monitored for progression of vascular leakage and capillary non-perfusion."
                    ]



        elif level == "low":
            base_steps = [
                "Annual retinal screening is recommended. " , 
                "Perform fundus photography and, if indicated, OCT imaging to detect early diabetic retinal changes and vascular abnormalities."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for early macular changes and fluid accumulation."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for early microvascular irregularities."
                ]



        else:
            base_steps = [
                "Routine retinal examination every 1–2 years is sufficient. " , 
                "Standard fundus evaluation is recommended to ensure absence of diabetic retinal pathology."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for subtle macular changes and early fluid accumulation."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for early microvascular irregularities in retinal layers."
                ]




    elif pred_class == "glaucoma":



        if level == "critical":
            base_steps = [
                "Immediate ophthalmology evaluation is required. " , 
                "Perform intraocular pressure (IOP) measurement, optic nerve OCT imaging to assess retinal nerve fiber layer thickness, and standard visual field testing to detect functional vision loss."
            ]



            if sex == "Female":
                sex_steps = [
                "Female patients should be evaluated for optic nerve susceptibility to pressure fluctuations and normal-tension glaucoma patterns."
            ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be assessed for rapid optic nerve cupping progression and elevated intraocular pressure trends."
                ]



        elif level == "high":
            base_steps = [
                "Specialist consultation within two weeks is recommended. " , 
                "Perform serial IOP monitoring, optic disc imaging, and baseline visual field assessment to establish disease progression trends."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for normal-tension glaucoma and subtle nerve fiber layer thinning."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for high-pressure glaucoma progression and optic nerve structural changes."
                ]



        elif level == "moderate":
            base_steps = [
                "Follow-up every 3–6 months is advised. " , 
                "Conduct optic nerve head evaluation using OCT and repeat visual field testing to detect early glaucomatous damage."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be assessed for early retinal nerve fiber layer thinning."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be monitored for early peripheral visual field defects."
                ]



        elif level == "low":
            base_steps = [
                "Annual glaucoma screening is recommended. " , 
                "Perform intraocular pressure measurement and optic disc examination to detect early abnormalities."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for early structural optic nerve changes."
            ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for intraocular pressure variability."
                ]



        else:
            base_steps = [
                "Routine eye examination every 1–2 years is sufficient. " , 
                "Basic intraocular pressure measurement and optic disc evaluation are recommended."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for early optic nerve susceptibility and subtle structural changes."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for intraocular pressure variation and optic nerve baseline changes."
                ]
 


    elif pred_class == "cataract":



        if level == "critical":
            base_steps = [
                "Immediate cataract surgical evaluation is recommended. " , 
                "Perform slit-lamp examination to assess lens opacity severity, visual acuity testing, and intraocular lens (IOL) power calculation for surgical planning."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for dense nuclear cataract progression and glare sensitivity."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for functional vision impairment affecting daily activities."
                ]



        elif level == "high":
            base_steps = [
                "Ophthalmology consultation is advised. " , 
                "Perform slit-lamp examination and visual acuity assessment to determine cataract severity and need for surgical intervention."
            ] 



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for cortical cataract progression."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be assessed for posterior subcapsular cataract impact on vision."
                ]



        elif level == "moderate":
            base_steps = [
                "Follow-up every 6 months is recommended. " , 
                "Perform visual acuity testing and slit-lamp examination to monitor progression of lens opacity."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be evaluated for progression speed and glare sensitivity."
               ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be monitored for contrast sensitivity reduction."
                ]



        elif level == "low":
            base_steps = [
                "Annual monitoring is sufficient. " , 
                "Perform routine visual acuity assessment and basic slit-lamp examination."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for early lens opacity changes."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for functional vision changes."
                ]



        else:
            base_steps = [
                "No immediate intervention is required. " , 
                "Routine eye examinations are sufficient to monitor lens clarity."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for early lens opacity progression and glare sensitivity."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for early functional vision changes related to lens clarity."
                ]




    elif pred_class == "normal":



        if level == "critical":
            base_steps = [
                "No retinal abnormality is detected. " , 
                "Perform routine comprehensive eye examination annually including fundus evaluation and optic disc assessment to maintain baseline ocular health."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for subtle retinal structural variations."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for baseline optic disc characteristics."
                ]



        elif level == "high":
            base_steps = [
                "Low clinical risk is observed. " , 
                "Annual eye examination with retinal imaging is recommended to ensure continued ocular health."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for minor retinal variations."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for optic disc baseline stability."
                ]



        elif level == "moderate":
            base_steps = [
                "Routine preventive eye screening is recommended. " , 
                "Periodic retinal and optic nerve evaluation should be performed."
        ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for subtle retinal baseline variations."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for optic nerve baseline consistency."
                ]



        elif level == "low":
            base_steps = [
                "Eye health appears stable. " ,
                "Follow-up eye examination every 1–2 years is recommended."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should be monitored for subtle ocular surface and retinal baseline variations."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should be evaluated for optic disc baseline consistency and early structural changes."
                ]



        else:
            base_steps = [
                "No action required. " , 
                "Maintain routine preventive eye care schedule."
            ]



            if sex == "Female":
                sex_steps = [
                    "Female patients should undergo periodic baseline retinal evaluation to detect subtle structural variations."
                ]
            elif sex == "Male":
                sex_steps = [
                    "Male patients should maintain baseline optic nerve assessment during routine examinations."
                ]
        
    else:
        base_steps = ["Consult an ophthalmologist for further clinical evaluation."]
        sex_steps = []



    # -------------------------------
    # Build Screening Report
    # -------------------------------
    screening_report = build_screening_report(
            display_class,
            confidence_pct,
            probs,
            sex
        )



    risk = level



    if risk in ["very_low", "low"]:
        risk_html = '<span class="risk-pill-low">Low risk</span>'
    elif risk == "moderate":
        risk_html = '<span class="risk-pill-medium">Moderate risk</span>'
    else:
        risk_html = '<span class="risk-pill-high">High risk</span>'
    next_steps = base_steps + sex_steps




    s_col1, s_col2 = st.columns([0.5, 0.5]) 



    with s_col1:



        st.write("**Predicted condition:** ", f"`{display_class}`")



        st.write(
            f"**Model confidence:** {confidence_pct:.2f}% "
            f"({screening_report.get('uncertainty','Unknown')} uncertainty)"
        )



        st.markdown(f"**Risk estimate:** {risk_html}", unsafe_allow_html=True)



    with s_col2:



        st.markdown("**Recommended next steps (for patient):**")



        for step in next_steps:
            st.markdown(f"- {step}")



    # -------------------------------
    # Class Probabilities
    # -------------------------------
    st.markdown("#### 📊 Class Probabilities")



    if probs:
        probs_df = pd.DataFrame({
            "Condition": [display_map.get(k, k) for k in probs.keys()],
            "Probability": list(probs.values())
        }).sort_values("Probability", ascending=False)



        st.bar_chart(probs_df.set_index("Condition"))
        st.dataframe(probs_df, use_container_width=True)



    else:
        st.info("No probability breakdown available.")



    # -------------------------------
    # Lesion Highlight Map
    # -------------------------------
    if heatmap_img:
        st.markdown("#### 👁️ AI-Highlighted Lesion-Suspect Regions")
        lesion_mask = generate_lesion_map(heatmap_img)
        st.image(lesion_mask, caption="AI Attention Mask")



    # -------------------------------
    # Doctor Feedback
    # -------------------------------
    if st.session_state.role == "doctor":



        st.markdown("#### 🩺 Doctor Feedback (Exclusive)")



        fb_col1, fb_col2 = st.columns(2)



        with fb_col1:
            feedback = st.radio(
                "Do you agree with AI prediction?",
                ["Agree", "Disagree"],
                horizontal=True
            )



        with fb_col2:
            corrected_label = pred_class



            if feedback == "Disagree":
                corrected_label = st.selectbox(
                    "Select correct diagnosis",
                    ["normal", "cataract", "glaucoma", "diabetic_retinopathy"]
                )



            if st.button("Save Feedback"):
                fb_entry = {
                    "ts": str(datetime.now()),
                    "ai": pred_class,
                    "doctor": corrected_label
                }



                with open("doctor_feedback.json", "a") as f:
                    f.write(json.dumps(fb_entry) + "\n")



                st.success("Feedback saved.")



    # -------------------------------
    # Session History
    # -------------------------------
    st.session_state.history.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "prediction": display_class,
        "confidence": f"{confidence_pct:.2f}%"
    })



    patient_info = st.session_state.patient_info
    patient_info["patient_id"] = st.session_state.get("patient_id", "Unknown")



    st.markdown("#### 🕒 Patient Image History (Current Session)")
    st.table(pd.DataFrame(st.session_state.history).drop_duplicates())



    # -------------------------------
    # PDF REPORT GENERATION
    # -------------------------------
    st.markdown("#### 📄 Download Screening Report (PDF)")



    screening_report = build_screening_report(
        display_class,
        confidence_pct,
        probs,
        sex
    )



    # override only what you need from UI logic
    screening_report["next_steps"] = base_steps + sex_steps
    screening_report["probabilities"] = probs



    pdf_bytes = create_pdf_report(
        patient_info=patient_info,
        screening_report=screening_report,
        original_img=image,
        heatmap_img=heatmap_img,
        user_role=st.session_state.role
    )



    patient_id = patient_info.get("patient_id", "UnknownID")
    patient_name = patient_info.get("name", "UnknownName").replace(" ", "_")



    file_name = f"{patient_id}_{patient_name}.pdf"



    st.download_button(
        label="Download PDF Screening Report",
        data=pdf_bytes,
        file_name=file_name,
        mime="application/pdf"
    )



    # --------------------------------------------------
    # ABOUT SECTION
    # --------------------------------------------------
    st.markdown('<a id="about-section"></a>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🔍 About This Project")



    st.markdown(
        """
        **RetinexAI** is a research prototype for automated retinal fundus disease screening.



        Key components:
        - ResNet50-based CNN classifier
        - Grad-CAM explainability
        - PDF report generation
        - Streamlit UI



        """
    )
