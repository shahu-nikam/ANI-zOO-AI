import os
import sqlite3

import click
from flask import current_app, g


def get_db():
    """Open a new database connection for the current request (cached in g)."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the users/predictions tables from database/schema.sql."""
    db = get_db()
    project_root = os.path.dirname(current_app.root_path)
    schema_path = os.path.join(project_root, "database", "schema.sql")
    with open(schema_path, "r") as f:
        db.executescript(f.read())


@click.command("init-db")
def init_db_command():
    """CLI command: `flask --app app init-db` resets the database."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    # Auto-create the database + tables the first time the app runs, so a
    # fresh clone works out of the box without a manual init-db step.
    if not os.path.exists(app.config["DATABASE"]):
        with app.app_context():
            init_db()
