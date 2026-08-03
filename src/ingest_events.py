import json
from pathlib import Path
import psycopg


RAW_DATA_DIR = Path("data/raw")


def find_latest_batch() -> Path:
    """Return the most recently modified listening-events batch."""

    batch_files = list(
        RAW_DATA_DIR.glob("listening_events_*.json")
    )

    if not batch_files:
        raise FileNotFoundError(
            "No listening-events batch files were found."
        )

    return max(
        batch_files,
        key=lambda file_path: file_path.stat().st_mtime,
    )


def load_events(file_path: Path) -> list[dict]:
    """Load events from a JSON batch file."""

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)

def insert_events(events: list[dict]) -> int:
    """Insert listening events into the Bronze PostgreSQL table."""

    connection_string = (
        "host=localhost "
        "port=5432 "
        "dbname=spotify "
        "user=spotify_user "
        "password=spotify_password"
    )

    insert_query = """
        INSERT INTO bronze.listening_events (
            event_id,
            batch_id,
            user_id,
            track_id,
            event_type,
            timestamp,
            device_type,
            country,
            subscription_type,
            listening_duration_seconds
        )
        VALUES (
            %(event_id)s,
            %(batch_id)s,
            %(user_id)s,
            %(track_id)s,
            %(event_type)s,
            %(timestamp)s,
            %(device_type)s,
            %(country)s,
            %(subscription_type)s,
            %(listening_duration_seconds)s
        )
        ON CONFLICT (event_id) DO NOTHING;
    """

    with psycopg.connect(connection_string) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(insert_query, events)

    return len(events)

def main() -> None:
    """Find and load the latest raw event batch."""

    latest_batch = find_latest_batch()
    events = load_events(latest_batch)

    processed_count = insert_events(events)
    print(f"Latest batch: {latest_batch}")
    print(f"Processed {processed_count} events")


if __name__ == "__main__":
    main()