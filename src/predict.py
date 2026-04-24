# ======================================================
# IMPORTS
# ======================================================
import os
import numpy as np
import tensorflow as tf
import yaml
from PIL import Image

# ======================================================
# CONFIG LOAD
# ======================================================
CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../configs/default.yaml")
)

with open(CONFIG_PATH, "r") as f:
    cfg = yaml.safe_load(f)

IMG_SIZE = int(cfg.get("img_size", 224))
CLASS_NAMES = cfg.get("class_names", [])

# ======================================================
# MODEL PATH
# ======================================================
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../models/resnet50_best.keras")
)

# ======================================================
# 🔥 CUSTOM FIXES (CRITICAL)
# ======================================================
from tensorflow.keras.layers import InputLayer # type: ignore

# Fix 1: batch_shape → batch_input_shape
def custom_input_layer(**config):
    if "batch_shape" in config:
        config["batch_input_shape"] = config.pop("batch_shape")
    return InputLayer(**config)

# Fix 2: DTypePolicy → force float32
def custom_dtype_policy(*args, **kwargs):
    return tf.float32

# Fix 3: Generic fallback for unknown objects
def dummy_object(*args, **kwargs):
    return None

# ======================================================
# LOAD MODEL (FULL COMPAT MODE)
# ======================================================
try:
    model = tf.keras.models.load_model(
        MODEL_PATH,
        compile=False,
        custom_objects={
            "InputLayer": custom_input_layer,
            "DTypePolicy": custom_dtype_policy,
        },
        safe_mode=False   # 🔥 critical for legacy models
    )
    print(f"✅ Model loaded: {MODEL_PATH}")

except Exception as e:
    print("❌ Model loading failed:", e)
    raise e

# ======================================================
# PREPROCESS FUNCTION
# ======================================================
def preprocess_image(image):

    if isinstance(image, str):
        img = Image.open(image).convert("RGB")
    else:
        img = image.convert("RGB")

    img = img.resize((IMG_SIZE, IMG_SIZE))

    img = np.array(img).astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)

    return img

# ======================================================
# PREDICT FUNCTION
# ======================================================
def predict_image(image):
    img = preprocess_image(image)

    preds = model.predict(img, verbose=0)[0]

    predicted_class = CLASS_NAMES[np.argmax(preds)]
    confidence = float(np.max(preds))

    prob_dict = {
        CLASS_NAMES[i]: float(preds[i])
        for i in range(len(CLASS_NAMES))
    }

    return {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "probabilities": prob_dict,
    }

# ======================================================
# CLI TEST
# ======================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, required=True)
    args = parser.parse_args()

    result = predict_image(args.image)

    print("\n=== Prediction Result ===")
    print("Class:", result["predicted_class"])
    print("Confidence:", round(result["confidence"], 4))