
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "predictions.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_type TEXT NOT NULL,
                student_input TEXT NOT NULL,
                prediction_result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def save_prediction(prediction_type, student_input, prediction_result):
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO predictions (
                prediction_type,
                student_input,
                prediction_result,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            prediction_type,
            json.dumps(student_input),
            json.dumps(prediction_result),
            datetime.now(timezone.utc).isoformat()
        ))

        return cursor.lastrowid



def get_prediction_history():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, prediction_type, student_input,
                   prediction_result, created_at
            FROM predictions
            ORDER BY id DESC
        """).fetchall()

        return [
            {
                "id": row["id"],
                "prediction_type": row["prediction_type"],
                "student_input": json.loads(row["student_input"]),
                "prediction_result": json.loads(row["prediction_result"]),
                "created_at": row["created_at"]
            }
            for row in rows
        ]
