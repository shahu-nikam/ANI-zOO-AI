import os

from flask import Blueprint, current_app, g, render_template, request, url_for

from app.auth import login_required
from app.db import get_db
from app.ml_utils import allowed_file, predict_image, save_to_dataset, save_upload

bp = Blueprint("main", __name__)


@bp.route("/", methods=("GET", "POST"))
@login_required
def home():
    prediction = confidence = image_url = uploaded_filename = None
    unknown = False
    saved_message = error = None

    if request.method == "POST":
        file = request.files.get("image")
        user_animal_name = request.form.get("animal_name", "")
        labelling_filename = request.form.get("uploaded_filename", "").strip()

        if labelling_filename and user_animal_name.strip():
            # User is teaching the model the name of a previously "unknown" image.
            existing_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], labelling_filename
            )

            if not os.path.exists(existing_path):
                error = "Original image not found. Please upload it again."
            else:
                clean_name = save_to_dataset(
                    existing_path, labelling_filename, user_animal_name
                )

                db = get_db()
                db.execute(
                    "UPDATE predictions SET user_provided_label = ? "
                    "WHERE image_filename = ? AND user_id = ?",
                    (clean_name, labelling_filename, g.user["id"]),
                )
                db.commit()

                saved_message = f"Image added to the dataset under '{clean_name}'."
                image_url = url_for("static", filename=f"uploads/{labelling_filename}")
                uploaded_filename = labelling_filename

        elif not file or file.filename == "":
            error = "Please select an image."

        elif not allowed_file(file.filename):
            error = "Only JPG, JPEG, PNG and WEBP images are allowed."

        else:
            filename, saved_path = save_upload(file)
            image_url = url_for("static", filename=f"uploads/{filename}")
            uploaded_filename = filename

            prediction, confidence, unknown = predict_image(saved_path)

            db = get_db()
            db.execute(
                "INSERT INTO predictions "
                "(user_id, image_filename, predicted_animal, confidence, is_unknown) "
                "VALUES (?, ?, ?, ?, ?)",
                (g.user["id"], filename, prediction, confidence, int(unknown)),
            )
            db.commit()

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=confidence,
        image_path=image_url,
        unknown=unknown,
        saved_message=saved_message,
        error=error,
        uploaded_filename=uploaded_filename,
    )


@bp.route("/history")
@login_required
def history():
    db = get_db()
    records = db.execute(
        "SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC",
        (g.user["id"],),
    ).fetchall()
    return render_template("history.html", records=records)
