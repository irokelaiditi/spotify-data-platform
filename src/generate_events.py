
print("Spotify event generator started")

import json
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone
from uuid import uuid4

random.seed(42)

event_types = [
    "track_played",
    "track_paused",
    "track_skipped",
    "track_completed",
]

device_types = [
    "mobile",
    "desktop",
    "tablet",
]

countries = [
    "GR",
    "UK",
    "DE",
    "FR",
    "IT",
]

subscription_types = [
    "free",
    "premium",
]

event = {
    "user_id": random.randint(1, 1000),
    "track_id": random.randint(1, 500),
    "event_type": random.choice(event_types),
}

print(event)

events = []
start_time = datetime.now(timezone.utc) - timedelta(days=30)

for _ in range(10_000):
    event = {
        "event_id": str(uuid4()),
        "user_id": random.randint(1, 1000),
        "track_id": random.randint(1, 500),
        "event_type": random.choice(event_types),
        "timestamp": (
        start_time + timedelta(seconds=random.randint(0, 30 * 24 * 60 * 60))).isoformat(),
        "device_type": random.choice(device_types),
        "country": random.choice(countries),
        "subscription_type": random.choice(subscription_types),
        "listening_duration_seconds": random.randint(10, 600),
    }

    events.append(event)

print(len(events))
print(events[:3])

output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "listening_events.json"

with output_file.open("w", encoding="utf-8") as file:
    json.dump(events, file, indent=2)

print(f"Generated {len(events)} events")
print(f"Saved to {output_file}")