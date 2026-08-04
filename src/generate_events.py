import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5


EVENT_TYPES = [
    "track_played",
    "track_paused",
    "track_skipped",
    "track_completed",
]

DEVICE_TYPES = [
    "mobile",
    "desktop",
    "tablet",
]

COUNTRIES = [
    "GR",
    "UK",
    "DE",
    "FR",
    "IT",
]

SUBSCRIPTION_TYPES = [
    "free",
    "premium",
]

EVENT_COUNT = 10_000
LOOKBACK_DAYS = 30
DIRTY_RATE = 0.05
RANDOM_SEED = 42

FIXED_REFERENCE_TIME = datetime(
    2026,
    8,
    1,
    0,
    0,
    tzinfo=timezone.utc,
)


def add_data_quality_issue(event: dict) -> None:
    """Add one controlled data-quality issue to an event."""

    issue_type = random.choice(
        [
            "missing_country",
            "missing_device",
            "invalid_event_type",
            "negative_duration",
            "inconsistent_subscription",
        ]
    )

    if issue_type == "missing_country":
        event["country"] = None
    elif issue_type == "missing_device":
        event["device_type"] = None
    elif issue_type == "invalid_event_type":
        event["event_type"] = "unknown_event"
    elif issue_type == "negative_duration":
        event["listening_duration_seconds"] = -1
    elif issue_type == "inconsistent_subscription":
        event["subscription_type"] = "PREMIUM"


def generate_event(
    start_time: datetime,
    event_number: int,
) -> dict:
    """Generate one reproducible synthetic listening event."""

    event = {
        "event_id": str(
            uuid5(
                NAMESPACE_URL,
                f"spotify-event-{event_number}",
            )
        ),
        "user_id": random.randint(1, 1000),
        "track_id": random.randint(1, 500),
        "event_type": random.choice(EVENT_TYPES),
        "event_timestamp": (
            start_time
            + timedelta(
                seconds=random.randint(
                    0,
                    LOOKBACK_DAYS * 24 * 60 * 60,
                )
            )
        ).isoformat(),
        "device_type": random.choice(DEVICE_TYPES),
        "country": random.choice(COUNTRIES),
        "subscription_type": random.choice(SUBSCRIPTION_TYPES),
        "listening_duration_seconds": random.randint(10, 600),
    }

    if random.random() < DIRTY_RATE:
        add_data_quality_issue(event)

    return event


def save_events(events: list[dict], output_file: Path) -> None:
    """Save generated events to a JSON file."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(events, file, indent=2)


def main() -> None:
    """Generate and save the reproducible synthetic dataset."""

    random.seed(RANDOM_SEED)

    start_time = FIXED_REFERENCE_TIME - timedelta(
        days=LOOKBACK_DAYS
    )

    events = [
        generate_event(start_time, event_number)
        for event_number in range(EVENT_COUNT)
    ]

    output_file = Path(
        "data/raw/listening_events.json"
    )

    save_events(events, output_file)

    print(f"Generated {len(events)} events")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()