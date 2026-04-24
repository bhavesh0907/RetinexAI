import tensorflow as tf
import numpy as np


def class_balanced_weights(class_counts, beta=0.9999):
    """
    Compute class-balanced weights using the 'Effective Number of Samples' formula.
    """
    class_counts = np.array(class_counts, dtype=np.float32)
    effective_num = 1.0 - np.power(beta, class_counts)
    weights = (1.0 - beta) / (effective_num + 1e-12)
    weights = weights / np.sum(weights) * len(class_counts)
    return weights.astype(np.float32)


class ClassBalancedFocalLoss(tf.keras.losses.Loss):
    """
    Class-Balanced Focal Loss:
    - Class-balanced weights (Cui et al.)
    - Focal loss component
    """

    def __init__(
        self,
        class_counts,
        beta=0.9999,
        gamma=2.0,
        from_logits=False,
        name="cb_focal_loss",
    ):
        super().__init__(name=name)

        self.gamma = gamma
        self.beta = beta
        self.from_logits = from_logits
        self.class_counts = np.array(class_counts, dtype=np.float32)

        # Precomputed class weights
        self.class_weights = class_balanced_weights(self.class_counts, beta=self.beta)

    def call(self, y_true, y_pred):
        """
        y_true: integer labels (batch,)
        y_pred: class probabilities or logits (batch, num_classes)
        """
        y_true = tf.cast(tf.squeeze(y_true), tf.int32)

        # Convert logits -> probabilities if needed
        if self.from_logits:
            probs = tf.nn.softmax(y_pred)
        else:
            probs = tf.clip_by_value(y_pred, 1e-7, 1.0)

        num_classes = tf.shape(probs)[-1]
        y_onehot = tf.one_hot(y_true, depth=num_classes)

        # Probability of the true class
        p_t = tf.reduce_sum(y_onehot * probs, axis=-1)

        # Cross entropy loss
        ce_loss = -tf.reduce_sum(y_onehot * tf.math.log(probs), axis=-1)

        # Focal factor
        focal_factor = tf.pow(1.0 - p_t, self.gamma)

        # Apply class-balanced weights
        weights = tf.gather(self.class_weights, y_true)

        # Final weighted loss
        loss = weights * focal_factor * ce_loss

        return tf.reduce_mean(loss)