-- Users table: stores each registered user with a hashed password.
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions table: stores every image a user uploads, along with the
-- AI's prediction/confidence, and (if the model was unsure) the label the
-- user supplied to teach it.
CREATE TABLE IF NOT EXISTS predictions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    image_filename      TEXT NOT NULL,
    predicted_animal    TEXT,
    confidence          REAL,
    is_unknown          INTEGER DEFAULT 0,
    user_provided_label TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
