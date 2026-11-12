import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.models.review import (
    InterventionReview,
    InterventionReviewRequest,
)


BACKEND_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BACKEND_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "sitepulse_reviews.db"


def get_connection():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialise_review_store():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS intervention_reviews (
                assessment_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                reviewer_name TEXT NOT NULL,
                comment TEXT NOT NULL DEFAULT '',
                reviewed_at TEXT NOT NULL
            )
            """
        )


def save_review(
    assessment_id: str,
    review: InterventionReviewRequest,
) -> InterventionReview:
    reviewed_at = datetime.now(timezone.utc)

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO intervention_reviews (
                assessment_id,
                status,
                reviewer_name,
                comment,
                reviewed_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(assessment_id)
            DO UPDATE SET
                status = excluded.status,
                reviewer_name = excluded.reviewer_name,
                comment = excluded.comment,
                reviewed_at = excluded.reviewed_at
            """,
            (
                assessment_id,
                review.status,
                review.reviewer_name.strip(),
                review.comment.strip(),
                reviewed_at.isoformat(),
            ),
        )

    return InterventionReview(
        assessment_id=assessment_id,
        status=review.status,
        reviewer_name=review.reviewer_name.strip(),
        comment=review.comment.strip(),
        reviewed_at=reviewed_at,
    )


def get_reviews() -> list[InterventionReview]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                assessment_id,
                status,
                reviewer_name,
                comment,
                reviewed_at
            FROM intervention_reviews
            ORDER BY reviewed_at DESC
            """
        ).fetchall()

    return [
        InterventionReview(
            assessment_id=row["assessment_id"],
            status=row["status"],
            reviewer_name=row["reviewer_name"],
            comment=row["comment"],
            reviewed_at=datetime.fromisoformat(row["reviewed_at"]),
        )
        for row in rows
    ]


def get_review(assessment_id: str) -> InterventionReview | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                assessment_id,
                status,
                reviewer_name,
                comment,
                reviewed_at
            FROM intervention_reviews
            WHERE assessment_id = ?
            """,
            (assessment_id,),
        ).fetchone()

    if row is None:
        return None

    return InterventionReview(
        assessment_id=row["assessment_id"],
        status=row["status"],
        reviewer_name=row["reviewer_name"],
        comment=row["comment"],
        reviewed_at=datetime.fromisoformat(row["reviewed_at"]),
    )