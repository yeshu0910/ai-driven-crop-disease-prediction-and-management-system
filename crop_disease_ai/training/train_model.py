"""
Model training script for crop disease classification.
Trains a CNN on the PlantVillage dataset or creates a demo model.
"""

import logging
import sys
from pathlib import Path

import numpy as np
from tensorflow import keras
from tensorflow.keras import applications, layers, models
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.config import (
    BATCH_SIZE,
    DATA_DIR,
    DISEASE_CLASSES,
    EPOCHS,
    IMG_SIZE,
    LEARNING_RATE,
    MODELS_DIR,
    TARGET_ACCURACY,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_demo_training_data(data_dir, num_samples_per_class=20):
    """Create small demo dataset when PlantVillage is not available."""
    logger.info("Creating demo training data...")
    logger.warning("=" * 60)
    logger.warning("WARNING: Generating synthetic random-noise training data.")
    logger.warning("Models trained on this data will produce RANDOM predictions.")
    logger.warning("Replace with real PlantVillage dataset for meaningful results.")
    logger.warning("=" * 60)
    data_dir = Path(data_dir)
    classes = list(DISEASE_CLASSES.keys())

    for cls in classes:
        cls_dir = data_dir / "train" / cls
        cls_dir.mkdir(parents=True, exist_ok=True)
        for i in range(num_samples_per_class):
            img = np.random.randint(0, 256, (IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
            img_path = cls_dir / f"sample_{i}.jpg"
            if not img_path.exists():
                import cv2

                cv2.imwrite(str(img_path), img)

    logger.info(
        f"Created demo data with {len(classes)} classes, {num_samples_per_class} samples each"
    )
    return data_dir


def build_model(num_classes):
    """Build CNN model with transfer learning support."""
    base_model = applications.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights="imagenet"
    )
    base_model.trainable = False

    inputs = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(512, activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs=inputs, outputs=outputs)

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model, base_model


def train_model():
    """Main training function."""
    data_dir = Path(DATA_DIR)
    train_dir = data_dir / "train"
    val_dir = data_dir / "val"

    if not train_dir.exists() or len(list(train_dir.iterdir())) == 0:
        logger.info("PlantVillage dataset not found. Creating demo data for testing...")
        create_demo_training_data(data_dir)
        train_dir = data_dir / "train"
        val_dir = data_dir / "val"
        if not val_dir.exists():
            import shutil

            val_dir.mkdir(parents=True, exist_ok=True)
            for cls in train_dir.iterdir():
                if cls.is_dir():
                    (val_dir / cls.name).mkdir(exist_ok=True)
                    files = list(cls.iterdir())
                    val_files = files[: max(1, len(files) // 5)]
                    for f in val_files:
                        shutil.copy(str(f), str(val_dir / cls.name / f.name))

    num_classes = len(list(train_dir.iterdir()))
    logger.info(f"Found {num_classes} classes for training")

    model, base_model = build_model(num_classes)

    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode="nearest",
    )

    val_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_generator = train_datagen.flow_from_directory(
        str(train_dir),
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=True,
        interpolation="bilinear",
    )

    val_generator = val_datagen.flow_from_directory(
        str(val_dir),
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False,
        interpolation="bilinear",
    )

    callbacks = [
        ModelCheckpoint(
            str(MODELS_DIR / "plant_disease_model.h5"),
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
            verbose=1,
        ),
        EarlyStopping(
            monitor="val_loss", patience=7, restore_best_weights=True, verbose=1
        ),
        ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=1
        ),
    ]

    steps_per_epoch = max(1, train_generator.samples // BATCH_SIZE)
    validation_steps = max(1, val_generator.samples // BATCH_SIZE)

    logger.info("Starting training phase 1 (feature extraction)...")
    history = model.fit(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs=EPOCHS,
        validation_data=val_generator,
        validation_steps=validation_steps,
        callbacks=callbacks,
        verbose=1,
    )

    base_model.trainable = True
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE * 0.1),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    logger.info("Starting training phase 2 (fine-tuning)...")
    history_fine = model.fit(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs=EPOCHS // 2,
        validation_data=val_generator,
        validation_steps=validation_steps,
        callbacks=callbacks,
        verbose=1,
    )

    class_indices = train_generator.class_indices
    np.save(str(MODELS_DIR / "class_indices.npy"), class_indices)
    logger.info(f"Class indices saved. Classes: {len(class_indices)}")

    final_accuracy = max(
        history.history["val_accuracy"] + history_fine.history["val_accuracy"]
    )
    logger.info(f"Training complete. Best validation accuracy: {final_accuracy:.4f}")

    if final_accuracy >= TARGET_ACCURACY:
        logger.info(f"Target accuracy of {TARGET_ACCURACY * 100}% achieved!")
    else:
        logger.warning(
            f"Accuracy {final_accuracy * 100:.2f}% below target {TARGET_ACCURACY * 100}%"
        )

    return model, history


def create_dummy_model():
    """Create a simple dummy model for testing when no dataset is available."""
    logger.warning("=" * 60)
    logger.warning("WARNING: Creating dummy model with RANDOM WEIGHTS.")
    logger.warning("This model is trained on synthetic noise data (not real plants).")
    logger.warning("Predictions will be essentially RANDOM (~1/num_classes accuracy).")
    logger.warning("Train on a real dataset (PlantVillage) for meaningful results.")
    logger.warning("=" * 60)
    logger.info("Creating dummy model for testing...")
    num_classes = len(DISEASE_CLASSES)

    model = models.Sequential(
        [
            layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3)),
            layers.Conv2D(32, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

    dummy_data = np.random.rand(10, IMG_SIZE, IMG_SIZE, 3)
    dummy_labels = np.random.rand(10, num_classes)
    model.fit(dummy_data, dummy_labels, epochs=1, verbose=0)

    model.save(str(MODELS_DIR / "plant_disease_model.h5"))

    indices = {
        name: i for i, name in enumerate(list(DISEASE_CLASSES.keys())[:num_classes])
    }
    np.save(str(MODELS_DIR / "class_indices.npy"), indices)
    logger.info(f"Dummy model saved to {MODELS_DIR / 'plant_disease_model.h5'}")
    return model


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("CROP DISEASE AI - MODEL TRAINING")
    logger.info("=" * 50)

    try:
        model, history = train_model()
    except Exception as e:
        logger.error(f"Training failed: {e}")
        logger.info("Creating dummy model for testing...")
        model = create_dummy_model()

    logger.info("Training complete!")
