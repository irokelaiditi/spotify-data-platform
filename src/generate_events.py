import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4


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


def generate_event(start_time: datetime) -> dict:
    """Generate one synthetic music listening event."""

    return {
        "event_id": str(uuid4()),
        "user_id": random.randint(1, 1000),
        "track_id": random.randint(1, 500),
        "event_type": random.choice(EVENT_TYPES),
        "timestamp": (
            start_time
            + timedelta(
                seconds=random.randint(0, LOOKBACK_DAYS * 24 * 60 * 60)
            )
        ).isoformat(),
        "device_type": random.choice(DEVICE_TYPES),
        "country": random.choice(COUNTRIES),
        "subscription_type": random.choice(SUBSCRIPTION_TYPES),
        "listening_duration_seconds": random.randint(10, 600),
    }


def save_events(events: list[dict], output_file: Path) -> None:
    """Save generated events to a JSON file."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(events, file, indent=2)


def main() -> None:
    """Generate and save a batch of synthetic listening events."""

    random.seed(42)

    start_time = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)

    events = [
        generate_event(start_time)
        for _ in range(EVENT_COUNT)
    ]

    output_file = Path("data/raw/listening_events.json")
    save_events(events, output_file)

    print(f"Generated {len(events)} events")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()