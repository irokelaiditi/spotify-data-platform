import json
from pathlib import Path

import psycopg


RAW_DATA_FILE = Path(
    "data/raw/listening_events.json"
)


def load_events(file_path: Path) -> list[dict]:
    """Load events from the reproducible JSON dataset."""

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def insert_events(events: list[dict]) -> int:
    """Insert events into the Bronze PostgreSQL table."""

    connection_string = (
        "host=localhost "
        "port=5432 "
        "dbname=music_streaming "
        "user=music_streaming_user "
        "password=music_streaming_password"
    )

    insert_query = """
        INSERT INTO bronze.listening_events (
            event_id,
            user_id,
            track_id,
            event_type,
            event_timestamp,
            device_type,
            country,
            subscription_type,
            listening_duration_seconds
        )
        VALUES (
            %(event_id)s,
            %(user_id)s,
            %(track_id)s,
            %(event_type)s,
            %(event_timestamp)s,
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
    """Load the reproducible dataset into PostgreSQL."""

    events = load_events(RAW_DATA_FILE)
    processed_count = insert_events(events)

    print(f"Loaded dataset: {RAW_DATA_FILE}")
    print(f"Processed {processed_count} events")


if __name__ == "__main__":
    main()