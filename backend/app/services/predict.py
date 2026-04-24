import numpy as np
import tensorflow as tf
from PIL import Image
import os

# ======================================================
# CONFIG
# ======================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "models", "resnet50_best.h5")

# ⚠️ IMPORTANT — UPDATE BASED ON YOUR TRAINING DATASET
# If you used flow_from_directory → alphabetical order
CLASSES = ["cataract", "diabetic_retinopathy", "glaucoma", "normal"]

_model = None


# ======================================================
# LOAD MODEL
# ======================================================
def load_model():
    global _model

    if _model is None:
        print("📦 Loading model:", MODEL_PATH)

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

        _model = tf.keras.models.load_model(MODEL_PATH, compile=False)

        print("✅ Model loaded successfully")

    return _model


# ======================================================
# PREPROCESS (MATCH TRAINING)
# ======================================================
def preprocess_image(image_path: str):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((224, 224))

    arr = np.array(img) / 255.0   # ✅ IMPORTANT (same as training)
    arr = np.expand_dims(arr, axis=0)

    return arr


# ======================================================
# PREDICT
# ======================================================
def predict_image(image_path: str):
    model = load_model()

    input_tensor = preprocess_image(image_path)

    preds = model.predict(input_tensor)[0]

    # 🔥 DEBUG — CHECK THIS OUTPUT
    print("🧠 RAW PREDICTIONS:", preds)
    print("📊 CLASS ORDER:", CLASSES)

    probs = dict(zip(CLASSES, preds.tolist()))

    predicted_class = CLASSES[np.argmax(preds)]
    confidence = float(np.max(preds))

    return {
        "label": predicted_class,
        "confidence": confidence,
        "probabilities": probs,
    }