import os
import numpy as np
import tensorflow as tf
import yaml
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import confusion_matrix, classification_report
from data import make_dataset


# -----------------------------
# LOAD CONFIG
# -----------------------------
CONFIG_PATH = "configs/default.yaml"

with open(CONFIG_PATH, "r") as f:
    cfg = yaml.safe_load(f)

img_size = int(cfg.get("img_size", 224))
batch_size = int(cfg.get("batch_size", 16))
class_names = cfg.get("class_names", [])
num_classes = len(class_names)

val_csv = cfg["data"]["manifest_val"]

# -----------------------------
# LOAD DATASET (NO SHUFFLE)
# -----------------------------
val_ds, n_val = make_dataset(
    val_csv,
    class_names=class_names,
    img_size=img_size,
    batch_size=batch_size,
    augment=False,
    shuffle=False,
    repeat=False
)

steps = n_val // batch_size

# -----------------------------
# LOAD MODEL
# -----------------------------
MODEL_PATH = f"models/{cfg.get('backbone','resnet50')}_best.keras"

model = tf.keras.models.load_model(
    MODEL_PATH,
    compile=False,
    safe_mode=False
)
print(f"\nLoaded model: {MODEL_PATH}")

# -----------------------------
# GET TRUE + PRED LABELS
# -----------------------------
y_true = []
y_pred = []

for images, labels in val_ds.take(steps):
    preds = model.predict(images, verbose=0)
    y_pred.extend(np.argmax(preds, axis=1))
    y_true.extend(labels.numpy())

y_true = np.array(y_true)
y_pred = np.array(y_pred)

# -----------------------------
# CLASSIFICATION REPORT
# -----------------------------
print("\n=== Classification Report ===")
print(classification_report(y_true, y_pred, target_names=class_names))

# -----------------------------
# CONFUSION MATRIX
# -----------------------------
cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=class_names,
            yticklabels=class_names)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

# -----------------------------
# NORMALIZED CONFUSION MATRIX
# -----------------------------
cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

plt.figure(figsize=(8, 6))
sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Greens",
            xticklabels=class_names,
            yticklabels=class_names)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Normalized Confusion Matrix")
plt.show()