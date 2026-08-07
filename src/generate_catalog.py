import json
import random
from datetime import date, timedelta
from pathlib import Path


ARTIST_COUNT = 1_000
ALBUM_COUNT = 3_000
TRACK_COUNT = 10_000
RANDOM_SEED = 42

GENRES = [
    "Pop",
    "Rock",
    "Hip-Hop",
    "Electronic",
    "Jazz",
    "Classical",
    "R&B",
    "Indie",
]

COUNTRIES = [
    "GR",
    "US",
    "UK",
    "DE",
    "FR",
    "IT",
]


def save_json(data: list[dict], output_file: Path) -> None:
    """Save data to a JSON file."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def generate_artists() -> list[dict]:
    """Generate reproducible artist reference data."""

    artists = []

    for artist_id in range(1, ARTIST_COUNT + 1):
        artists.append(
            {
                "artist_id": artist_id,
                "artist_name": f"Artist {artist_id}",
                "genre": random.choice(GENRES),
                "country": random.choice(COUNTRIES),
            }
        )

    return artists


def generate_albums() -> list[dict]:
    """Generate reproducible album reference data."""

    albums = []

    start_date = date(2000, 1, 1)
    date_range_days = 26 * 365

    for album_id in range(1, ALBUM_COUNT + 1):
        release_date = start_date + timedelta(
            days=random.randint(0, date_range_days)
        )

        albums.append(
            {
                "album_id": album_id,
                "album_name": f"Album {album_id}",
                "release_date": release_date.isoformat(),
            }
        )

    return albums


def generate_tracks() -> list[dict]:
    """Generate reproducible track reference data."""

    tracks = []

    for track_id in range(1, TRACK_COUNT + 1):
        album_id = (
            None
            if random.random() < 0.10
            else random.randint(1, ALBUM_COUNT)
        )

        tracks.append(
            {
                "track_id": track_id,
                "track_name": f"Track {track_id}",
                "album_id": album_id,
                "duration_seconds": random.randint(120, 420),
                "release_date": (
                    date(2000, 1, 1)
                    + timedelta(days=random.randint(0, 26 * 365))
                ).isoformat(),
            }
        )

    return tracks


def generate_track_artists() -> list[dict]:
    """Generate many-to-many relationships between tracks and artists."""

    track_artists = []

    for track_id in range(1, TRACK_COUNT + 1):
        artist_count = random.choices(
            population=[1, 2, 3],
            weights=[85, 13, 2],
            k=1,
        )[0]

        artist_ids = random.sample(
            range(1, ARTIST_COUNT + 1),
            k=artist_count,
        )

        for artist_id in artist_ids:
            track_artists.append(
                {
                    "track_id": track_id,
                    "artist_id": artist_id,
                }
            )

    return track_artists


def main() -> None:
    """Generate and save the full synthetic music catalog."""

    random.seed(RANDOM_SEED)

    artists = generate_artists()
    albums = generate_albums()
    tracks = generate_tracks()
    track_artists = generate_track_artists()

    save_json(
        artists,
        Path("data/raw/artists.json"),
    )

    save_json(
        albums,
        Path("data/raw/albums.json"),
    )

    save_json(
        tracks,
        Path("data/raw/tracks.json"),
    )

    save_json(
        track_artists,
        Path("data/raw/track_artists.json"),
    )

    print(f"Generated {len(artists)} artists")
    print(f"Generated {len(albums)} albums")
    print(f"Generated {len(tracks)} tracks")
    print(f"Generated {len(track_artists)} track-artist relationships")


if __name__ == "__main__":
    main()