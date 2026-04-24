import os
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split

VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def collect_images(root_dir):
    """
    Walks data/raw/main_dataset/<class_name> and collects image paths + labels.
    Returns a pandas DataFrame with columns: image_path, label, patient_id, eye, source
    """
    rows = []
    root_dir = os.path.abspath(root_dir)

    for label_name in sorted(os.listdir(root_dir)):
        class_dir = os.path.join(root_dir, label_name)
        if not os.path.isdir(class_dir):
            continue

        for fname in os.listdir(class_dir):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in VALID_EXTS:
                continue
            fpath = os.path.join(class_dir, fname)
            rows.append(
                {
                    "image_path": fpath,
                    "label": label_name,
                    "patient_id": os.path.splitext(fname)[0],  # simple placeholder
                    "eye": "",  # unknown for now
                    "source": "main_dataset",
                }
            )

    df = pd.DataFrame(rows)
    return df


def make_splits(df, train_size=0.7, val_size=0.15, test_size=0.15, random_state=42):
    assert abs(train_size + val_size + test_size - 1.0) < 1e-6, "Splits must sum to 1."

    # First split train vs temp
    df_train, df_temp = train_test_split(
        df, train_size=train_size, stratify=df["label"], random_state=random_state
    )

    # Remaining temp -> val & test
    val_ratio = val_size / (val_size + test_size)  # fraction of temp that goes to val
    df_val, df_test = train_test_split(
        df_temp,
        train_size=val_ratio,
        stratify=df_temp["label"],
        random_state=random_state,
    )

    return df_train, df_val, df_test


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root_dir",
        type=str,
        default="data/raw/main_dataset",
        help="Root folder containing class subfolders (Normal, Cataract, etc.)",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="data/manifests",
        help="Directory to save manifest / split CSVs",
    )
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    print(f"Scanning images in: {args.root_dir}")
    df = collect_images(args.root_dir)
    print(f"Found {len(df)} images.")
    print(df["label"].value_counts())

    manifest_path = os.path.join(args.out_dir, "manifest.csv")
    df.to_csv(manifest_path, index=False)
    print(f"Saved manifest to {manifest_path}")

    df_train, df_val, df_test = make_splits(df)

    train_path = os.path.join(args.out_dir, "train.csv")
    val_path = os.path.join(args.out_dir, "val.csv")
    test_path = os.path.join(args.out_dir, "test.csv")

    df_train.to_csv(train_path, index=False)
    df_val.to_csv(val_path, index=False)
    df_test.to_csv(test_path, index=False)

    print("Saved splits:")
    print(" Train:", train_path, len(df_train))
    print(" Val  :", val_path, len(df_val))
    print(" Test :", test_path, len(df_test))


if __name__ == "__main__":
    main()