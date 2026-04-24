# src/clinical_engine.py

def interpret_predictions(result: dict) -> dict:
    """
    Clinical interpretation layer.
    Expects a single result dict from predict.py
    """

    predicted_class = result["predicted_class"]
    confidence = result["confidence"]

    # Default outputs
    risk = "Low"
    next_steps = []

    if predicted_class == "Normal":
        risk = "Low"
        next_steps = ["Routine screening recommended."]
    else:
        if confidence >= 80:
            risk = "High"
        elif confidence >= 50:
            risk = "Moderate"
        else:
            risk = "Low"

        if predicted_class == "Diabetic Retinopathy":
            next_steps = [
                "Urgent referral to ophthalmologist.",
                "Optimize blood sugar and blood pressure.",
                "Consider fundus photography and OCT.",
            ]
        else:
            next_steps = [
                "Ophthalmology consultation recommended.",
                "Further retinal imaging advised.",
            ]

    return {
        "risk": risk,
        "next_steps": next_steps,
    }
