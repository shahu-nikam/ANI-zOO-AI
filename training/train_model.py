"""
Trains the animal classifier from images in dataset/animal/<class_name>/*.jpg
and saves the result into ml_models/.

Run from the project root:
    python training/train_model.py
"""

import os

import joblib
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "dataset", "animal")
MODEL_OUT_DIR = os.path.join(BASE_DIR, "ml_models")

os.makedirs(MODEL_OUT_DIR, exist_ok=True)

file_paths = []
labels = []

for label in os.listdir(DATASET_DIR):
    label_path = os.path.join(DATASET_DIR, label)

    if os.path.isdir(label_path):
        for file in os.listdir(label_path):
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                file_paths.append(os.path.join(label_path, file))
                labels.append(label)

if not file_paths:
    raise SystemExit(
        f"No training images found in {DATASET_DIR}. "
        "Add images under dataset/animal/<class_name>/ first."
    )

df = pd.DataFrame({"image_path": file_paths, "label": labels})
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

train_df, val_df = train_test_split(
    df, test_size=0.2, random_state=42, stratify=df["label"]
)

train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=25,
    width_shift_range=0.2,
    height_shift_range=0.2,
    zoom_range=0.2,
    shear_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],
)

val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

train_generator = train_datagen.flow_from_dataframe(
    dataframe=train_df,
    x_col="image_path",
    y_col="label",
    target_size=(224, 224),
    batch_size=64,
    class_mode="categorical",
    shuffle=True,
    seed=42,
)

val_generator = val_datagen.flow_from_dataframe(
    dataframe=val_df,
    x_col="image_path",
    y_col="label",
    target_size=(224, 224),
    batch_size=64,
    class_mode="categorical",
    shuffle=False,
)

num_classes = len(train_generator.class_indices)
print("Total Classes:", num_classes)

base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

model = models.Sequential(
    [
        layers.Input(shape=(224, 224, 3)),
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dense(512, activation="relu"),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation="softmax"),
    ]
)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

early_stopping = EarlyStopping(monitor="val_accuracy", patience=5, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.2, patience=2, min_lr=0.000001, verbose=1)
checkpoint = ModelCheckpoint(
    os.path.join(MODEL_OUT_DIR, "best_ani_model.keras"),
    monitor="val_accuracy",
    save_best_only=True,
    mode="max",
)

print("\nStarting Feature Extraction Training...\n")

history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=5,
    callbacks=[early_stopping, reduce_lr, checkpoint],
)

print("\nStarting Fine-Tuning...\n")

base_model.trainable = True
for layer in base_model.layers[:-10]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.00001),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

fine_tune_history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=5,
    callbacks=[early_stopping, reduce_lr, checkpoint],
)

model.save(os.path.join(MODEL_OUT_DIR, "ani_model.keras"))

class_names = list(train_generator.class_indices.keys())
joblib.dump(class_names, os.path.join(MODEL_OUT_DIR, "ani_classes.pkl"))

print("\nTraining Completed Successfully!")
print("Model saved as: ml_models/ani_model.keras")
print("Classes saved as: ml_models/ani_classes.pkl")
print("Total Classes:", num_classes)
