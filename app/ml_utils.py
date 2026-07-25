"""Helpers for loading the trained model and running predictions.

The TensorFlow/Keras model is loaded lazily (on first use, not at import
time) so that `flask --app app init-db` and other lightweight commands
don't pay the cost of loading a 20MB+ model.
"""

import os
import shutil
import uuid

import joblib
import numpy as np
from flask import current_app

_model = None
_class_names = None


def _load_ml_assets():
    global _model, _class_names
    if _model is None:
        from tensorflow.keras.models import load_model

        _model = load_model(current_app.config["MODEL_PATH"])
        _class_names = joblib.load(current_app.config["CLASS_PATH"])
    return _model, _class_names


def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def save_upload(file):
    """Save an uploaded FileStorage under a random name. Returns (filename, full_path)."""
    ext = os.path.splitext(file.filename)[1].lower()
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    return filename, path


def predict_image(image_path):
    """Run the model on an image. Returns (label, confidence_pct, is_unknown)."""
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    from tensorflow.keras.preprocessing import image as keras_image

    model, class_names = _load_ml_assets()

    img = keras_image.load_img(image_path, target_size=(224, 224))
    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    predictions = model.predict(img_array, verbose=0)[0]
    predicted_index = int(np.argmax(predictions))
    confidence = float(predictions[predicted_index] * 100)
    label = class_names[predicted_index]

    is_unknown = confidence < current_app.config["CONFIDENCE_THRESHOLD"]
    if is_unknown:
        label = "Unknown Animal"

    return label, round(confidence, 2), is_unknown


def save_to_dataset(image_path, filename, animal_name):
    """Copy an image into dataset/animal/<clean_name>/ for future retraining."""
    invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    clean_name = animal_name.strip().lower()
    for ch in invalid_chars:
        clean_name = clean_name.replace(ch, "")

    folder = os.path.join(current_app.config["DATASET_FOLDER"], clean_name)
    os.makedirs(folder, exist_ok=True)

    dest = os.path.join(folder, filename)
    shutil.copy(image_path, dest)
    return clean_name
