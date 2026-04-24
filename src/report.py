import datetime
import random

# -------------------------------------------------------
# PATIENT ID
# -------------------------------------------------------
def generate_patient_id():
    year = datetime.datetime.now().year
    num = random.randint(1000, 9999)
    return f"P-{year}-{num}"

# -------------------------------------------------------
# RISK LEVEL (MATCH APP.PY EXACTLY)
# -------------------------------------------------------
def compute_risk_level(confidence):
    if confidence >= 90:
        return "critical"
    elif confidence >= 75:
        return "high"
    elif confidence >= 60:
        return "moderate"
    elif confidence >= 40:
        return "low"
    else:
        return "very_low"

# -------------------------------------------------------
# RECOMMENDATION ENGINE (ALIGNED WITH APP.PY)
# -------------------------------------------------------
def recommended_steps(pred_class, confidence, sex="Unknown"):
    pred_class = pred_class.strip().lower().replace(" ", "_")
    level = compute_risk_level(confidence)

    base_steps = []
    sex_steps = []

    # ---------------------------------------------------
    # DIABETIC RETINOPATHY
    # ---------------------------------------------------
    if pred_class == "diabetic_retinopathy":

        if level == "critical":
            base_steps = [
                "Immediate retina specialist referral within 24–48 hours is recommended. ",
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
                "Early retina specialist consultation within one week is advised. ",
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
                "Follow-up evaluation within 1–3 months is recommended. ",
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
                "Annual retinal screening is recommended. ",
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
                "Routine retinal examination every 1–2 years is sufficient. ",
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

    # ---------------------------------------------------
    # GLAUCOMA
    # ---------------------------------------------------
    elif pred_class == "glaucoma":

        if level == "critical":
            base_steps = [
                "Immediate ophthalmology evaluation is required. ",
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
                "Specialist consultation within two weeks is recommended. ",
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
                "Follow-up every 3–6 months is advised. ",
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
                "Annual glaucoma screening is recommended. ",
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
                "Routine eye examination every 1–2 years is sufficient. ",
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

    # ---------------------------------------------------
    # CATARACT
    # ---------------------------------------------------
    elif pred_class == "cataract":

        if level == "critical":
            base_steps = [
                "Immediate cataract surgical evaluation is recommended. ",
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
                "Ophthalmology consultation is advised. ",
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
                "Follow-up every 6 months is recommended. ",
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
                "Annual monitoring is sufficient. ",
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
                "No immediate intervention is required. ",
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

    # ---------------------------------------------------
    # NORMAL
    # ---------------------------------------------------
    elif pred_class == "normal":

        if level == "critical":
            base_steps = [
                "No retinal abnormality is detected. ",
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
                "Low clinical risk is observed. ",
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
                "Routine preventive eye screening is recommended. ",
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
                "Eye health appears stable. ",
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
                "No action required. ",
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

    return base_steps + sex_steps

# -------------------------------------------------------
# MAIN REPORT BUILDER
# -------------------------------------------------------
def build_screening_report(pred_class, confidence, probs, sex="Unknown"):
    report = {}

    report["patient_id"] = generate_patient_id()
    report["screening_date"] = datetime.datetime.now().strftime("%d %b %Y  %I:%M %p")
    report["prediction"] = pred_class
    report["confidence"] = confidence
    report["probabilities"] = probs

    report["risk"] = compute_risk_level(confidence)
    report["next_steps"] = recommended_steps(pred_class, confidence, sex)

    if confidence >= 90:
        report["uncertainty"] = "Low"
    elif confidence >= 50:
        report["uncertainty"] = "Moderate"
    else:
        report["uncertainty"] = "High"

    return report