import os
import numpy as np
from tensorflow.keras.models import load_model # type: ignore
from PIL import Image

# ✅ FIXED PATH (match your actual file)
MODEL_PATH = "models/resnet50_best.h5"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

model = load_model(MODEL_PATH, compile=False)

CLASS_NAMES = [
    "No_DR",
    "Mild",
    "Moderate",
    "Severe",
    "Proliferative_DR"
]


def preprocess_image(image_path: str):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((224, 224))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image