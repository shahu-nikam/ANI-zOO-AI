# ANI-zOO AI

A Flask web app that identifies animals in an uploaded image using a
MobileNetV2-based Keras model. Users register/log in, upload images, get
predictions, and can teach the model new animal names when it's not
confident — every prediction is saved to that user's history in SQLite.

## What's new in this version

- **Login system** — register, log in, log out (passwords hashed with
  Werkzeug, sessions via Flask).
- **SQLite database** (`instance/app.db`, auto-created on first run) with:
  - `users` table — id, username, email, password_hash, created_at
  - `predictions` table — every image a user uploads, the predicted
    animal, confidence, whether it was "unknown", and the label the user
    taught it (if any)
- **History page** (`/history`) — a user's past uploads and predictions.
- **New-image pipeline** — every uploaded image is saved under
  `app/static/uploads/`, and if the user labels an "unknown" prediction,
  that image is copied into `dataset/animal/<label>/` so it can be used
  to retrain the model later.
- Project reorganized into a standard Flask **app-factory + blueprints**
  layout (see structure below) instead of one flat folder.

## Project structure

```
gitpush/
├── run.py                  # entry point: `python run.py`
├── config.py                # app configuration (paths, thresholds, secret key)
├── requirements.txt
├── app/
│   ├── __init__.py          # create_app() factory
│   ├── db.py                 # SQLite connection + init-db
│   ├── auth.py               # /auth/register, /auth/login, /auth/logout
│   ├── main.py                # / (upload + predict), /history
│   ├── ml_utils.py            # model loading, prediction, dataset saving
│   ├── static/
│   │   ├── style.css
│   │   └── uploads/           # user-uploaded images (gitignored contents)
│   └── templates/
│       ├── login.html
│       ├── register.html
│       ├── index.html
│       └── history.html
├── database/
│   └── schema.sql            # users + predictions table definitions
├── instance/
│   └── app.db                  # SQLite database file (auto-created)
├── ml_models/
│   ├── ani_model.keras
│   ├── best_ani_model.keras
│   └── ani_classes.pkl
├── dataset/
│   └── animal/                 # <animal_name>/*.jpg — grows as users label "unknown" images
└── training/
    └── train_model.py         # retrain the model from dataset/animal/
```

## Requirements

- Python 3.10–3.11 recommended (TensorFlow compatibility)
- See `requirements.txt`

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app (the SQLite database is created automatically on first run)
python run.py
```

Open `http://127.0.0.1:5000`, register an account, log in, and start
uploading images.

## Resetting the database

If you ever want a completely fresh database:

```bash
flask --app app init-db
```

This drops and recreates the `users` and `predictions` tables — all
accounts and history will be lost.

## Retraining the model

1. Grow `dataset/animal/<animal_name>/` with images (this happens
   automatically as users label "unknown" predictions in the app, or you
   can add images manually).
2. Run:
   ```bash
   python training/train_model.py
   ```
   This saves an updated `ani_model.keras`, `best_ani_model.keras`, and
   `ani_classes.pkl` into `ml_models/`.
3. Restart the app to pick up the new model.

## Notes

- `CONFIDENCE_THRESHOLD` (default 50%) in `config.py` controls when a
  prediction is treated as "Unknown Animal" and the user is prompted to
  label it.
- Set a real `SECRET_KEY` environment variable before deploying — the
  default in `config.py` is for local development only.
