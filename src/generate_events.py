
print("Spotify event generator started")

import json
import random
from pathlib import Path

event_types = [
    "track_played",
    "track_paused",
    "track_skipped",
    "track_completed",
]

event = {
    "user_id": random.randint(1, 1000),
    "track_id": random.randint(1, 500),
    "event_type": random.choice(event_types),
}

print(event)

events = []

for _ in range(10_000):
    event = {
        "user_id": random.randint(1, 1000),
        "track_id": random.randint(1, 500),
        "event_type": random.choice(event_types),
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