"""
Model evaluation script for crop disease classification.
"""

import sys
from pathlib import Path

import numpy as np
import tensorflow as tf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging

from utils.config import DATA_DIR, DISEASE_CLASSES, IMG_SIZE, MODELS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def evaluate_model():
    """Evaluate trained model performance."""
    model_path = MODELS_DIR / "plant_disease_model.h5"
    class_indices_path = MODELS_DIR / "class_indices.npy"

    if not model_path.exists():
        logger.error(f"Model not found at {model_path}")
        logger.info("Run train_model.py first to train a model.")
        return None

    logger.info(f"Loading model from {model_path}")
    model = tf.keras.models.load_model(str(model_path))
    logger.info("Model loaded successfully")

    if class_indices_path.exists():
        class_indices = np.load(str(class_indices_path), allow_pickle=True).item()
        class_names = {v: k for k, v in class_indices.items()}
        logger.info(f"Loaded {len(class_indices)} class indices")
    else:
        class_indices = None
        class_names = None
        logger.warning("Class indices not found")

    val_dir = DATA_DIR / "val"
    if val_dir.exists() and len(list(val_dir.iterdir())) > 0:
        from tensorflow.keras.preprocessing.image import ImageDataGenerator

        val_datagen = ImageDataGenerator(rescale=1.0 / 255)
        val_generator = val_datagen.flow_from_directory(
            str(val_dir),
            target_size=(IMG_SIZE, IMG_SIZE),
            batch_size=32,
            class_mode="categorical",
            shuffle=False,
        )
        logger.info(f"Evaluating on {val_generator.samples} validation samples...")
        results = model.evaluate(val_generator, verbose=1)
        metrics = {
            "loss": float(results[0]),
            "accuracy": float(results[1]),
            "val_samples": val_generator.samples,
        }
        logger.info(f"Validation Loss: {results[0]:.4f}")
        logger.info(f"Validation Accuracy: {results[1]:.4f}")

        from sklearn.metrics import classification_report, confusion_matrix

        y_pred = model.predict(val_generator, verbose=1)
        y_pred_classes = np.argmax(y_pred, axis=1)
        y_true = val_generator.classes

        if class_names:
            target_names = [
                class_names.get(i, f"Class_{i}") for i in range(len(class_names))
            ]
            report = classification_report(
                y_true, y_pred_classes, target_names=target_names, zero_division=0
            )
            logger.info(f"\nClassification Report:\n{report}")
            metrics["classification_report"] = report

            # Disease-wise accuracy
            cm = confusion_matrix(y_true, y_pred_classes)
            disease_accuracy = {}
            for i, name in enumerate(target_names):
                if i < cm.shape[0] and cm[i].sum() > 0:
                    acc = cm[i, i] / cm[i].sum() * 100
                    disease_accuracy[name] = round(acc, 2)
            logger.info("\nDisease-wise Accuracy:")
            for name, acc in sorted(disease_accuracy.items(), key=lambda x: x[1]):
                logger.info(f"  {name}: {acc:.2f}%")
            metrics["disease_accuracy"] = disease_accuracy
    else:
        logger.warning("Validation directory not found. Running basic evaluation...")
        dummy_data = np.random.rand(32, IMG_SIZE, IMG_SIZE, 3)
        dummy_labels = (
            np.eye(len(DISEASE_CLASSES))[:32]
            if len(DISEASE_CLASSES) >= 32
            else np.eye(len(DISEASE_CLASSES))[: len(DISEASE_CLASSES)]
        )
        if len(dummy_labels) < 32:
            reps = 32 // len(dummy_labels) + 1
            dummy_labels = np.tile(dummy_labels, (reps, 1))[:32]
        results = model.evaluate(dummy_data, dummy_labels, verbose=0)
        metrics = {
            "loss": float(results[0]),
            "accuracy": float(results[1]),
            "note": "Evaluated on dummy data - no validation set found",
        }
        logger.info(f"Model loss (dummy): {results[0]:.4f}")
        logger.info(f"Model accuracy (dummy): {results[1]:.4f}")

    model_summary = []
    model.summary(print_fn=lambda x: model_summary.append(x))
    metrics["model_summary"] = "\n".join(model_summary)
    metrics["model_layers"] = len(model.layers)
    metrics["trainable_params"] = int(
        sum(np.prod(v.shape) for v in model.trainable_weights)
    )

    logger.info(f"Total layers: {metrics['model_layers']}")
    logger.info(f"Trainable parameters: {metrics['trainable_params']:,}")

    return metrics


def predict_single_image(image_path):
    """Predict disease for a single image."""
    import cv2

    model_path = MODELS_DIR / "plant_disease_model.h5"
    class_indices_path = MODELS_DIR / "class_indices.npy"

    if not model_path.exists():
        logger.error("Model not found")
        return None

    model = tf.keras.models.load_model(str(model_path))

    if class_indices_path.exists():
        class_indices = np.load(str(class_indices_path), allow_pickle=True).item()
        class_names = {v: k for k, v in class_indices.items()}
    else:
        class_names = None

    img = cv2.imread(str(image_path))
    if img is None:
        logger.error(f"Could not read image: {image_path}")
        return None

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    predictions = model.predict(img, verbose=0)
    predicted_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_idx])

    if class_names:
        class_name = class_names.get(predicted_idx, f"Class_{predicted_idx}")
        disease_name = DISEASE_CLASSES.get(class_name, class_name)
    else:
        disease_name = f"Disease_{predicted_idx}"

    return {
        "disease_name": disease_name,
        "confidence": confidence,
        "class_index": int(predicted_idx),
    }


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("CROP DISEASE AI - MODEL EVALUATION")
    logger.info("=" * 50)

    metrics = evaluate_model()
    if metrics:
        logger.info(f"\nFinal Accuracy: {metrics['accuracy'] * 100:.2f}%")
    else:
        logger.warning("Evaluation failed.")
