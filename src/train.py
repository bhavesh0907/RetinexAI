import sys
import os

# ================================
# Add src/ directory to PYTHONPATH
# ================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import argparse
import random
import numpy as np
import tensorflow as tf
import yaml

# 🔥 MIXED PRECISION (MAJOR SPEED BOOST)
from tensorflow.keras import mixed_precision # type: ignore
mixed_precision.set_global_policy('float32')

from data import make_dataset, read_manifest
from models import build_model
from losses import ClassBalancedFocalLoss


def load_config(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


def set_seeds(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def get_class_counts(manifest_csv: str, class_names):
    df = read_manifest(manifest_csv)

    labels = (
        df["label"]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    counts = [(labels == name).sum() for name in class_names]
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/default.yaml")
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--seed", type=int, default=42)

    # 🔥 OPTIONAL SPEED FLAGS
    parser.add_argument("--freeze", action="store_true", help="Freeze backbone")
    parser.add_argument("--fast", action="store_true", help="Fast training mode")

    args = parser.parse_args()

    cfg = load_config(args.config)
    set_seeds(args.seed)

    img_size = int(cfg.get("img_size", 224))
    batch_size = int(cfg.get("batch_size", 16))
    class_names = cfg.get("class_names", [])
    num_classes = int(cfg.get("num_classes", len(class_names)))

    if not class_names or num_classes != len(class_names):
        raise ValueError("Config error: class_names mismatch")

    backbone = args.model if args.model else cfg.get("backbone", "resnet50")

    data_cfg = cfg.get("data", {})
    train_csv = data_cfg.get("manifest_train")
    val_csv = data_cfg.get("manifest_val")

    print("\n=== Training Config ===")
    print("Backbone   :", backbone)
    print("Img size   :", img_size)
    print("Batch size :", batch_size)
    print("=======================\n")

    # ================================
    # 🔥 DATA PIPELINE (OPTIMIZED)
    # ================================
    train_ds, n_train = make_dataset(
        train_csv,
        class_names=class_names,
        img_size=img_size,
        batch_size=batch_size,
        augment=True,
        shuffle=True,
        repeat=True
    )

    val_ds, n_val = make_dataset(
        val_csv,
        class_names=class_names,
        img_size=img_size,
        batch_size=batch_size,
        augment=False,
        shuffle=False,
        repeat=False
    )

    # 🔥 CRITICAL: remove CPU bottleneck
    train_ds = train_ds.cache().prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.cache().prefetch(tf.data.AUTOTUNE)

    steps_per_epoch = n_train // batch_size
    validation_steps = n_val // batch_size

    # 🔥 FAST MODE (optional)
    if args.fast:
        steps_per_epoch = min(100, steps_per_epoch)
        validation_steps = min(50, validation_steps)

    print(f"Train samples: {n_train}, Val samples: {n_val}")

    # ================================
    # LOSS
    # ================================
    class_counts = get_class_counts(train_csv, class_names)

    loss_cfg = cfg.get("loss", {})
    loss_fn = ClassBalancedFocalLoss(
        class_counts=class_counts,
        beta=float(loss_cfg.get("beta", 0.9999)),
        gamma=float(loss_cfg.get("gamma", 2.0)),
        from_logits=False,
    )

    # ================================
    # MODEL
    # ================================
    model = build_model(
        backbone_name=backbone,
        input_shape=(img_size, img_size, 3),
        num_classes=num_classes,
        dropout=0.3,
        pretrained=True,
    )

    # 🔥 FREEZE BACKBONE (HUGE SPEED BOOST)
    if args.freeze:
        for layer in model.layers[:-1]:
            layer.trainable = False

    # 🔥 LEGACY OPTIMIZER (CRITICAL FOR M2)
    optimizer = tf.keras.optimizers.legacy.Adam(
        learning_rate=float(cfg.get("optimizer", {}).get("lr", 1e-4))
    )

    model.compile(
        optimizer=optimizer,
        loss=loss_fn,
        metrics=["sparse_categorical_accuracy"],
    )

    # ================================
    # CALLBACKS
    # ================================
    save_dir = cfg.get("export", {}).get("save_dir", "models")
    os.makedirs(save_dir, exist_ok=True)

    ckpt_path = os.path.join(save_dir, f"{backbone}_best.keras")

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            ckpt_path,
            monitor="val_sparse_categorical_accuracy",
            save_best_only=True,
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_sparse_categorical_accuracy",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_sparse_categorical_accuracy",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    print("\n🚀 Starting training...\n")

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=30,
        steps_per_epoch=steps_per_epoch,
        validation_steps=validation_steps,
        callbacks=callbacks,
    )

    print("\n🎉 Training completed!")
    print("Best model saved to:", ckpt_path)


if __name__ == "__main__":
    main()