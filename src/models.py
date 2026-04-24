import tensorflow as tf


def build_model(
    backbone_name: str = "resnet50",
    input_shape=(224, 224, 3),
    num_classes: int = 4,
    dropout: float = 0.3,
    pretrained: bool = True,
):
    """
    Build a classification model with backbone:
      - resnet50
      - resnet101
      - densenet121
    """
    backbone_name = backbone_name.lower()
    weights = "imagenet" if pretrained else None

    # -------- SELECT BACKBONE --------
    if backbone_name == "resnet50":
        base = tf.keras.applications.ResNet50(
            include_top=False,
            weights=weights,
            input_shape=input_shape,
        )
    elif backbone_name == "resnet101":
        base = tf.keras.applications.ResNet101(
            include_top=False,
            weights=weights,
            input_shape=input_shape,
        )
    elif backbone_name == "densenet121":
        base = tf.keras.applications.DenseNet121(
            include_top=False,
            weights=weights,
            input_shape=input_shape,
        )
    else:
        raise ValueError(f"Unknown backbone: {backbone_name}")

    # -------- CLASSIFICATION HEAD --------
    x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
    x = tf.keras.layers.Dropout(dropout)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs=base.input, outputs=outputs, name=backbone_name)
    return model