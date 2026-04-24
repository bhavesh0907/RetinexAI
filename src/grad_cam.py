import numpy as np
import tensorflow as tf
from PIL import Image
import yaml
import cv2
import os


# --------- CONFIG HELPERS ---------


def _load_config(config_path: str = "configs/default.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def _get_img_size(cfg: dict) -> int:
    # img_size is at the top level of default.yaml
    return int(cfg.get("img_size", 224))


# --------- MODEL CACHE ---------

_model_cache = {}

from tensorflow.keras.layers import InputLayer # type: ignore

def custom_input_layer(**config):
    if "batch_shape" in config:
        config["batch_input_shape"] = config.pop("batch_shape")
    return InputLayer(**config)

def custom_dtype_policy(*args, **kwargs):
    return tf.float32


def _load_model(model_path: str = "models/resnet50_best.keras") -> tf.keras.Model:
    global _model_cache

    if model_path in _model_cache:
        return _model_cache[model_path]

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = tf.keras.models.load_model(
        model_path,
        compile=False,
        custom_objects={
            "InputLayer": custom_input_layer,
            "DTypePolicy": custom_dtype_policy,
        },
        safe_mode=False
    )

    _model_cache[model_path] = model
    return model

# --------- GRAD-CAM CORE ---------


def generate_grad_cam(
    pil_image: Image.Image, model_path: str = "models/resnet50_best.keras"
) -> Image.Image:
    """
    Generate a Grad-CAM heatmap overlaid on the original fundus image.
    Returns a PIL.Image.
    """
    cfg = _load_config()
    img_size = _get_img_size(cfg)
    model = _load_model(model_path)

    # 1) Preprocess image (same size as model input)
    img = pil_image.resize((img_size, img_size))
    img_arr = np.array(img).astype("float32")

    # Ensure 3 channels
    if img_arr.ndim == 2:
        img_arr = np.stack([img_arr] * 3, axis=-1)
    elif img_arr.shape[2] == 4:  # RGBA -> RGB
        img_arr = img_arr[:, :, :3]

    img_arr_norm = img_arr / 255.0
    input_tensor = np.expand_dims(img_arr_norm, axis=0)  # (1, H, W, 3)

    # 2) Find last Conv2D layer
    last_conv_layer = None
    for layer in reversed(model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            last_conv_layer = layer
            break

    if last_conv_layer is None:
        raise RuntimeError("Could not find a 4D Conv2D layer for Grad-CAM.")

    grad_model = tf.keras.models.Model(
        [model.inputs], [last_conv_layer.output, model.output]
    )

    # 3) Compute gradients with respect to predicted class
    with tf.GradientTape() as tape:
        conv_outputs, preds = grad_model(input_tensor)
        class_idx = tf.argmax(preds[0])
        loss = preds[:, class_idx]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = tf.tensordot(conv_outputs, pooled_grads, axes=(2, 0))
    heatmap = tf.maximum(heatmap, 0)
    max_val = tf.reduce_max(heatmap) + 1e-8
    heatmap = heatmap / max_val
    heatmap = heatmap.numpy()

    # 4) Resize heatmap and apply colormap
    heatmap = cv2.resize(heatmap, (img_size, img_size))
    heatmap_uint8 = np.uint8(255 * heatmap)
    heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    # 5) Mask out black background (keep retina only)
    img_rgb = img_arr.astype("uint8")
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

    # Pixels brighter than 10 are retina, the rest is background
    mask = gray > 10
    mask_3c = np.repeat(mask[:, :, np.newaxis], 3, axis=2)

    # Zero-out heatmap on background
    heatmap_color_masked = heatmap_color * mask_3c

    # 6) Overlay masked heatmap on original image
    overlay = cv2.addWeighted(img_rgb, 0.6, heatmap_color_masked, 0.4, 0)

    return Image.fromarray(overlay)