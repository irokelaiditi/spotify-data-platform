import bisect
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

DEVICE_WEIGHTS = [
    0.70,
    0.25,
    0.05,
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

EVENT_COUNT = 500_000
USER_COUNT = 15_000
TRACK_COUNT = 10_000

LOOKBACK_DAYS = 30
DIRTY_RATE = 0.05
RANDOM_SEED = 42

TRACK_POPULARITY_ALPHA = 0.8

TRACKS_FILE = Path("data/raw/tracks.json")
OUTPUT_FILE = Path("data/raw/listening_events.json")

FIXED_REFERENCE_TIME = datetime(
    2026,
    8,
    1,
    0,
    0,
    tzinfo=timezone.utc,
)


def generate_user_profiles() -> dict[int, dict]:
    """Assign stable attributes to each synthetic user."""

    return {
        user_id: {
            "country": random.choice(COUNTRIES),
            "subscription_type": random.choice(
                SUBSCRIPTION_TYPES
            ),
        }
        for user_id in range(1, USER_COUNT + 1)
    }


def load_track_durations() -> dict[int, int]:
    """Load track durations from the MusicBrainz catalog."""

    with TRACKS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        tracks = json.load(file)

    track_durations = {
        track["track_id"]: track["duration_seconds"]
        for track in tracks
        if track.get("duration_seconds") is not None
        and track["duration_seconds"] > 0
    }

    expected_track_ids = set(
        range(1, TRACK_COUNT + 1)
    )

    actual_track_ids = set(
        track_durations.keys()
    )

    if actual_track_ids != expected_track_ids:
        raise RuntimeError(
            "Track catalog must contain exactly "
            f"track IDs 1 through {TRACK_COUNT} "
            "with valid positive durations."
        )

    return track_durations


def build_track_popularity_distribution(
    track_ids: list[int],
) -> tuple[list[float], float]:
    """
    Build a reproducible long-tail popularity distribution.

    Tracks receive different popularity ranks so that a small
    number of tracks generate many events while most tracks
    receive fewer plays.
    """

    popularity_rng = random.Random(
        RANDOM_SEED + 1
    )

    ranked_track_ids = track_ids.copy()

    popularity_rng.shuffle(
        ranked_track_ids
    )

    weight_by_track = {}

    for rank, track_id in enumerate(
        ranked_track_ids,
        start=1,
    ):
        weight_by_track[track_id] = (
            1 / (rank ** TRACK_POPULARITY_ALPHA)
        )

    cumulative_weights = []
    total_weight = 0.0

    for track_id in track_ids:
        total_weight += weight_by_track[
            track_id
        ]

        cumulative_weights.append(
            total_weight
        )

    return cumulative_weights, total_weight


def choose_track(
    track_ids: list[int],
    cumulative_weights: list[float],
    total_weight: float,
) -> int:
    """Choose a track using the popularity distribution."""

    random_value = (
        random.random() * total_weight
    )

    index = bisect.bisect_left(
        cumulative_weights,
        random_value,
    )

    return track_ids[index]


def generate_listening_duration(
    track_duration: int,
    event_type: str,
) -> int:
    """Generate listening time consistent with track duration."""

    if event_type == "track_completed":
        return track_duration

    if event_type == "track_skipped":
        maximum_skip_duration = min(
            track_duration,
            60,
        )

        return random.randint(
            1,
            maximum_skip_duration,
        )

    return random.randint(
        1,
        track_duration,
    )


def add_data_quality_issue(
    event: dict,
) -> None:
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
        if event["subscription_type"] == "premium":
            event["subscription_type"] = "PREMIUM"
        else:
            event["subscription_type"] = "FREE"


def generate_event(
    start_time: datetime,
    event_number: int,
    user_profiles: dict[int, dict],
    track_durations: dict[int, int],
    track_ids: list[int],
    cumulative_weights: list[float],
    total_weight: float,
) -> dict:
    """Generate one reproducible synthetic listening event."""

    user_id = random.randint(
        1,
        USER_COUNT,
    )

    user_profile = user_profiles[
        user_id
    ]

    track_id = choose_track(
        track_ids,
        cumulative_weights,
        total_weight,
    )

    event_type = random.choice(
        EVENT_TYPES
    )

    listening_duration = (
        generate_listening_duration(
            track_durations[track_id],
            event_type,
        )
    )

    event = {
        "event_id": str(
            uuid5(
                NAMESPACE_URL,
                f"spotify-event-{event_number}",
            )
        ),
        "user_id": user_id,
        "track_id": track_id,
        "event_type": event_type,
        "event_timestamp": (
            start_time
            + timedelta(
                seconds=random.randint(
                    0,
                    LOOKBACK_DAYS
                    * 24
                    * 60
                    * 60,
                )
            )
        ).isoformat(),
        "device_type": random.choices(
            DEVICE_TYPES,
            weights=DEVICE_WEIGHTS,
            k=1,
        )[0],
        "country": user_profile[
            "country"
        ],
        "subscription_type": user_profile[
            "subscription_type"
        ],
        "listening_duration_seconds": (
            listening_duration
        ),
    }

    if random.random() < DIRTY_RATE:
        add_data_quality_issue(event)

    return event


def save_events(
    events: list[dict],
    output_file: Path,
) -> None:
    """Save generated events to a JSON file."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            events,
            file,
            indent=2,
        )


def main() -> None:
    """Generate and save the reproducible synthetic dataset."""

    random.seed(
        RANDOM_SEED
    )

    user_profiles = (
        generate_user_profiles()
    )

    track_durations = (
        load_track_durations()
    )

    track_ids = sorted(
        track_durations.keys()
    )

    (
        cumulative_weights,
        total_weight,
    ) = build_track_popularity_distribution(
        track_ids
    )

    start_time = (
        FIXED_REFERENCE_TIME
        - timedelta(
            days=LOOKBACK_DAYS
        )
    )

    events = [
        generate_event(
            start_time,
            event_number,
            user_profiles,
            track_durations,
            track_ids,
            cumulative_weights,
            total_weight,
        )
        for event_number in range(
            EVENT_COUNT
        )
    ]

    save_events(
        events,
        OUTPUT_FILE,
    )

    print(
        f"Generated {len(events)} events"
    )

    print(
        f"Saved to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()