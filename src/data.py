import tensorflow as tf
import pandas as pd

AUTOTUNE = tf.data.AUTOTUNE


def read_manifest(csv_path):
    return pd.read_csv(csv_path)


def get_class_map(class_names):
    return {name: idx for idx, name in enumerate(class_names)}


def decode_and_preprocess(path, img_size=(224, 224), augment=False):
    image = tf.io.read_file(path)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.convert_image_dtype(image, tf.float32)

    shape = tf.shape(image)
    h, w = shape[0], shape[1]
    side = tf.minimum(h, w)

    offset_h = (h - side) // 2
    offset_w = (w - side) // 2

    image = tf.image.crop_to_bounding_box(image, offset_h, offset_w, side, side)
    image = tf.image.resize(image, img_size)

    if augment:
        image = augment_image(image)

    return tf.clip_by_value(image, 0.0, 1.0)


def augment_image(image):
    image = tf.image.random_flip_left_right(image)

    k = tf.random.uniform([], 0, 4, dtype=tf.int32)
    image = tf.image.rot90(image, k)

    image = tf.image.random_brightness(image, 0.1)
    image = tf.image.random_contrast(image, 0.9, 1.1)

    return image


def make_dataset(
    manifest_csv,
    class_names,
    img_size=224,
    batch_size=16,
    augment=False,
    shuffle=True,
    repeat=False   # ✅ CRITICAL FIX
):
    df = read_manifest(manifest_csv)

    # 🔥 FORCE label consistency
    df["label"] = df["label"].str.lower().str.strip()

    class_map = get_class_map(class_names)

    paths = df["image_path"].astype(str).tolist()
    labels = [class_map[lbl] for lbl in df["label"].tolist()]

    paths_ds = tf.data.Dataset.from_tensor_slices(paths)
    labels_ds = tf.data.Dataset.from_tensor_slices(tf.cast(labels, tf.int32))

    ds = tf.data.Dataset.zip((paths_ds, labels_ds))

    if shuffle:
        ds = ds.shuffle(buffer_size=len(paths))

    def _parse(path, label):
        img = decode_and_preprocess(path, (img_size, img_size), augment)
        return img, label

    ds = ds.map(_parse, num_parallel_calls=AUTOTUNE)

    # ✅ FIX: repeat ONLY for training
    if repeat:
        ds = ds.repeat()

    ds = ds.batch(batch_size)
    ds = ds.prefetch(AUTOTUNE)

    return ds, len(df)