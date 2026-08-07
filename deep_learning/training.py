"""
PneumoVision AI - Deep Learning Model Training Script
Transfer Learning with EfficientNetB0 for Pneumonia Detection
"""

import os
import logging
import datetime
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, applications, optimizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ReduceLROnPlateau,
    ModelCheckpoint,
    TensorBoard,
    CSVLogger,
)
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
)
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "input_size": (224, 224),
    "batch_size": 32,
    "epochs": 50,
    "learning_rate": 1e-4,
    "num_classes": 1,  # Binary classification
    "train_dir": "dataset/train",
    "val_dir": "dataset/val",
    "test_dir": "dataset/test",
    "model_save_path": "model.keras",
    "log_dir": "logs",
}


def create_data_generators(config: dict) -> tuple:
    """
    Create data generators with augmentation for training, validation, and testing.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Tuple of (train_generator, val_generator, test_generator)
    """
    # Training data augmentation
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode="nearest",
        brightness_range=[0.8, 1.2],
    )

    # Validation/Test data - only rescaling
    val_test_datagen = ImageDataGenerator(rescale=1.0 / 255)

    # Create generators
    train_generator = train_datagen.flow_from_directory(
        config["train_dir"],
        target_size=config["input_size"],
        batch_size=config["batch_size"],
        class_mode="binary",
        shuffle=True,
        seed=42,
    )

    val_generator = val_test_datagen.flow_from_directory(
        config["val_dir"],
        target_size=config["input_size"],
        batch_size=config["batch_size"],
        class_mode="binary",
        shuffle=False,
    )

    test_generator = val_test_datagen.flow_from_directory(
        config["test_dir"],
        target_size=config["input_size"],
        batch_size=config["batch_size"],
        class_mode="binary",
        shuffle=False,
    )

    logger.info(
        f"Data generators created:\n"
        f"  Train: {train_generator.samples} samples\n"
        f"  Validation: {val_generator.samples} samples\n"
        f"  Test: {test_generator.samples} samples\n"
        f"  Classes: {train_generator.class_indices}"
    )

    return train_generator, val_generator, test_generator


def build_model(config: dict) -> keras.Model:
    """
    Build EfficientNetB0 transfer learning model.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Compiled Keras model
    """
    # Load base model with pretrained weights
    base_model = applications.EfficientNetB0(
        weights="imagenet",
        include_top=False,
        input_shape=(*config["input_size"], 3),
    )

    # Freeze base model layers
    base_model.trainable = False

    # Add custom classification head
    inputs = keras.Input(shape=(*config["input_size"], 3))
    
    # Data augmentation layer
    x = layers.RandomRotation(0.1)(inputs)
    x = layers.RandomFlip("horizontal")(x)
    x = layers.RandomZoom(0.1)(x)
    
    # Base model
    x = base_model(x, training=False)
    
    # Global pooling
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    
    # Dense layers
    x = layers.Dense(256, activation="relu", name="dense_256")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    
    x = layers.Dense(128, activation="relu", name="dense_128")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    
    # Output layer
    outputs = layers.Dense(
        config["num_classes"],
        activation="sigmoid",
        name="top_activation",
    )(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="PneumoVisionAI")

    # Compile model
    model.compile(
        optimizer=optimizers.Adam(learning_rate=config["learning_rate"]),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
            keras.metrics.AUC(name="auc"),
        ],
    )

    logger.info(f"Model built successfully:\n{model.summary()}")
    
    return model


def setup_callbacks(config: dict) -> list:
    """
    Setup training callbacks for model optimization.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        List of Keras callbacks
    """
    os.makedirs(config["log_dir"], exist_ok=True)
    
    callbacks = [
        # Early stopping to prevent overfitting
        EarlyStopping(
            monitor="val_loss",
            patience=10,
            restore_best_weights=True,
            verbose=1,
        ),
        
        # Reduce learning rate when plateau
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.2,
            patience=5,
            min_lr=1e-7,
            verbose=1,
        ),
        
        # Save best model
        ModelCheckpoint(
            filepath=config["model_save_path"],
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
            verbose=1,
        ),
        
        # TensorBoard logging
        TensorBoard(
            log_dir=os.path.join(config["log_dir"], datetime.datetime.now().strftime("%Y%m%d-%H%M%S")),
            histogram_freq=1,
            write_graph=True,
        ),
        
        # CSV logging
        CSVLogger(
            filename=os.path.join(config["log_dir"], "training_log.csv"),
            separator=",",
            append=False,
        ),
    ]
    
    return callbacks


def plot_training_history(history: keras.callbacks.History, config: dict):
    """
    Plot and save training history graphs.
    
    Args:
        history: Training history object
        config: Configuration dictionary
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Accuracy
    axes[0, 0].plot(history.history["accuracy"], label="Train Accuracy", linewidth=2)
    axes[0, 0].plot(history.history["val_accuracy"], label="Val Accuracy", linewidth=2)
    axes[0, 0].set_title("Model Accuracy", fontsize=14, fontweight="bold")
    axes[0, 0].set_xlabel("Epoch")
    axes[0, 0].set_ylabel("Accuracy")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Loss
    axes[0, 1].plot(history.history["loss"], label="Train Loss", linewidth=2)
    axes[0, 1].plot(history.history["val_loss"], label="Val Loss", linewidth=2)
    axes[0, 1].set_title("Model Loss", fontsize=14, fontweight="bold")
    axes[0, 1].set_xlabel("Epoch")
    axes[0, 1].set_ylabel("Loss")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Precision
    if "precision" in history.history:
        axes[1, 0].plot(history.history["precision"], label="Train Precision", linewidth=2)
        axes[1, 0].plot(history.history["val_precision"], label="Val Precision", linewidth=2)
        axes[1, 0].set_title("Model Precision", fontsize=14, fontweight="bold")
        axes[1, 0].set_xlabel("Epoch")
        axes[1, 0].set_ylabel("Precision")
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    # AUC
    if "auc" in history.history:
        axes[1, 1].plot(history.history["auc"], label="Train AUC", linewidth=2)
        axes[1, 1].plot(history.history["val_auc"], label="Val AUC", linewidth=2)
        axes[1, 1].set_title("Model AUC", fontsize=14, fontweight="bold")
        axes[1, 1].set_xlabel("Epoch")
        axes[1, 1].set_ylabel("AUC")
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(config["log_dir"], "training_history.png"), dpi=150, bbox_inches="tight")
    plt.close()
    
    logger.info(f"Training history plot saved to {config['log_dir']}/training_history.png")


def evaluate_model(
    model: keras.Model,
    test_generator,
    config: dict,
):
    """
    Comprehensive model evaluation with metrics and visualizations.
    
    Args:
        model: Trained Keras model
        test_generator: Test data generator
        config: Configuration dictionary
    """
    logger.info("Evaluating model on test set...")
    
    # Get predictions
    y_pred_prob = model.predict(test_generator, verbose=1)
    y_pred = (y_pred_prob > 0.5).astype(int).flatten()
    y_true = test_generator.classes
    
    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    # ROC and AUC
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_prob)
    roc_auc = auc(fpr, tpr)
    
    logger.info(
        f"\n{'='*50}\n"
        f"TEST SET EVALUATION RESULTS\n"
        f"{'='*50}\n"
        f"Accuracy:  {accuracy:.4f}\n"
        f"Precision: {precision:.4f}\n"
        f"Recall:    {recall:.4f}\n"
        f"F1 Score:  {f1:.4f}\n"
        f"AUC:       {roc_auc:.4f}\n"
        f"{'='*50}"
    )
    
    # Classification report
    report = classification_report(
        y_true, y_pred,
        target_names=["Normal", "Pneumonia"],
    )
    logger.info(f"\nClassification Report:\n{report}")
    
    # Save classification report
    with open(os.path.join(config["log_dir"], "classification_report.txt"), "w") as f:
        f.write(report)
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Normal", "Pneumonia"],
        yticklabels=["Normal", "Pneumonia"],
    )
    plt.title("Confusion Matrix", fontsize=14, fontweight="bold")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    plt.savefig(
        os.path.join(config["log_dir"], "confusion_matrix.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()
    logger.info("Confusion matrix saved")
    
    # ROC Curve
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC curve (AUC = {roc_auc:.4f})")
    plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--", label="Random")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate", fontsize=12)
    plt.ylabel("True Positive Rate", fontsize=12)
    plt.title("Receiver Operating Characteristic (ROC) Curve", fontsize=14, fontweight="bold")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(config["log_dir"], "roc_curve.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()
    logger.info("ROC curve saved")
    
    # Save metrics to file
    metrics = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "auc": float(roc_auc),
        "true_negative": int(cm[0, 0]),
        "false_positive": int(cm[0, 1]),
        "false_negative": int(cm[1, 0]),
        "true_positive": int(cm[1, 1]),
    }
    
    import json
    with open(os.path.join(config["log_dir"], "test_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)
    
    logger.info("Test metrics saved to JSON")


def fine_tune_model(
    model: keras.Model,
    train_generator,
    val_generator,
    config: dict,
):
    """
    Fine-tune the model by unfreezing some base model layers.
    
    Args:
        model: Pre-trained model
        train_generator: Training data generator
        val_generator: Validation data generator
        config: Configuration dictionary
    """
    logger.info("Starting fine-tuning...")
    
    # Unfreeze top layers of base model
    base_model = model.layers[3]  # EfficientNetB0 is the 4th layer
    base_model.trainable = True
    
    # Freeze first 100 layers, unfreeze the rest
    for layer in base_model.layers[:100]:
        layer.trainable = False
    for layer in base_model.layers[100:]:
        layer.trainable = True
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=optimizers.Adam(learning_rate=config["learning_rate"] / 10),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
            keras.metrics.AUC(name="auc"),
        ],
    )
    
    # Fine-tune callbacks
    fine_tune_callbacks = [
        EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-8, verbose=1),
        ModelCheckpoint(
            filepath=config["model_save_path"].replace(".keras", "_finetuned.keras"),
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
            verbose=1,
        ),
    ]
    
    # Fine-tune
    history = model.fit(
        train_generator,
        epochs=config["epochs"] // 2,
        validation_data=val_generator,
        callbacks=fine_tune_callbacks,
        verbose=1,
    )
    
    logger.info("Fine-tuning completed")
    return history


def main():
    """Main training pipeline."""
    logger.info("=" * 60)
    logger.info("PNEUMOVISION AI - MODEL TRAINING")
    logger.info("=" * 60)
    
    # Check TensorFlow version and GPU
    logger.info(f"TensorFlow version: {tf.__version__}")
    gpus = tf.config.list_physical_devices("GPU")
    logger.info(f"GPUs Available: {len(gpus)}")
    if gpus:
        for gpu in gpus:
            logger.info(f"  - {gpu.name}")
    else:
        logger.warning("No GPU found. Training will use CPU (may be slow).")
    
    # Create data generators
    train_gen, val_gen, test_gen = create_data_generators(CONFIG)
    
    # Build model
    model = build_model(CONFIG)
    
    # Setup callbacks
    callbacks = setup_callbacks(CONFIG)
    
    # Train model
    logger.info(f"Starting initial training for {CONFIG['epochs']} epochs...")
    history = model.fit(
        train_gen,
        epochs=CONFIG["epochs"],
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1,
    )
    
    # Plot training history
    plot_training_history(history, CONFIG)
    
    # Evaluate model
    evaluate_model(model, test_gen, CONFIG)
    
    # Fine-tune if desired
    try:
        fine_tune_model(model, train_gen, val_gen, CONFIG)
        logger.info("Fine-tuning completed successfully")
    except Exception as e:
        logger.warning(f"Fine-tuning skipped: {str(e)}")
    
    # Save final model
    final_path = CONFIG["model_save_path"]
    model.save(final_path)
    logger.info(f"Final model saved to: {final_path}")
    
    # Convert to TFLite (for mobile/web deployment)
    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()
        tflite_path = final_path.replace(".keras", ".tflite")
        with open(tflite_path, "wb") as f:
            f.write(tflite_model)
        logger.info(f"TFLite model saved to: {tflite_path}")
    except Exception as e:
        logger.warning(f"TFLite conversion skipped: {str(e)}")
    
    logger.info("=" * 60)
    logger.info("TRAINING COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

