import csv
from datetime import datetime, timezone
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent / "logs"


def _append(filename, row):
    LOG_DIR.mkdir(exist_ok=True)

    path = LOG_DIR / filename
    has_header = path.exists() and path.stat().st_size > 0

    with path.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(row),
        )

        if not has_header:
            writer.writeheader()

        writer.writerow(row)


def log_interaction(result):
    _append(
        "interactions.csv",
        {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "question": result["user_question"],
            "matched_faq": result["question"],
            "answer": result["answer"],
            "score": result["score"],
            "mode": result["mode"],
        },
    )


def log_feedback(result, helpful):
    _append(
        "feedback.csv",
        {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "question": result["user_question"],
            "helpful": int(helpful),
        },
    )
