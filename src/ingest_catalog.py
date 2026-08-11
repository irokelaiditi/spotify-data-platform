import json
from pathlib import Path

import psycopg


RAW_DATA_DIR = Path("data/raw")

CONNECTION_STRING = (
    "host=localhost "
    "port=5432 "
    "dbname=music_streaming "
    "user=music_streaming_user "
    "password=music_streaming_password"
)

def load_json(file_name: str) -> list[dict]:
    """Load records from a raw JSON file."""

    file_path = RAW_DATA_DIR / file_name

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def ingest_artists(connection) -> None:
    """Load artists into the Bronze layer."""

    artists = load_json("artists.json")

    query = """
        INSERT INTO bronze.artists (
            artist_id,
            artist_name,
            genre,
            country
        )
        VALUES (
            %(artist_id)s,
            %(artist_name)s,
            %(genre)s,
            %(country)s
        )
        ON CONFLICT (artist_id) DO NOTHING;
    """

    with connection.cursor() as cursor:
        cursor.executemany(query, artists)

    print(f"Processed {len(artists)} artists")


def ingest_albums(connection) -> None:
    """Load albums into the Bronze layer."""

    albums = load_json("albums.json")

    query = """
        INSERT INTO bronze.albums (
            album_id,
            album_name,
            release_date
        )
        VALUES (
            %(album_id)s,
            %(album_name)s,
            %(release_date)s
        )
        ON CONFLICT (album_id) DO NOTHING;
    """

    with connection.cursor() as cursor:
        cursor.executemany(query, albums)

    print(f"Processed {len(albums)} albums")


def ingest_tracks(connection) -> None:
    """Load tracks into the Bronze layer."""

    tracks = load_json("tracks.json")

    query = """
        INSERT INTO bronze.tracks (
            track_id,
            track_name,
            album_id,
            duration_seconds,
            release_date
        )
        VALUES (
            %(track_id)s,
            %(track_name)s,
            %(album_id)s,
            %(duration_seconds)s,
            %(release_date)s
        )
        ON CONFLICT (track_id) DO NOTHING;
    """

    with connection.cursor() as cursor:
        cursor.executemany(query, tracks)

    print(f"Processed {len(tracks)} tracks")


def ingest_track_artists(connection) -> None:
    """Load track-to-artist relationships into the Bronze layer."""

    track_artists = load_json("track_artists.json")

    query = """
        INSERT INTO bronze.track_artists (
            track_id,
            artist_id
        )
        VALUES (
            %(track_id)s,
            %(artist_id)s
        )
        ON CONFLICT (track_id, artist_id) DO NOTHING;
    """

    with connection.cursor() as cursor:
        cursor.executemany(query, track_artists)

    print(f"Processed {len(track_artists)} track-artist relationships")


def main() -> None:
    """Load the generated music catalog into PostgreSQL."""

    with psycopg.connect(CONNECTION_STRING) as connection:
        ingest_artists(connection)
        ingest_albums(connection)
        ingest_tracks(connection)
        ingest_track_artists(connection)


if __name__ == "__main__":
    main()