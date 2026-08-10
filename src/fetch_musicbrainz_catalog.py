import json
import os
import random
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()


BASE_URL = "https://musicbrainz.org/ws/2"

ARTIST_TARGETS = {
    "GR": 200,
    "US": 300,
    "GB": 250,
    "DE": 100,
    "FR": 100,
    "IT": 50,
}

TRACK_TARGET = 10_000
RECORDINGS_PER_ARTIST = 25

PAGE_SIZE = 100
REQUEST_DELAY_SECONDS = 1.1
MAX_RETRIES = 5
RANDOM_SEED = 42

CONTACT_EMAIL = os.getenv(
    "MUSICBRAINZ_CONTACT_EMAIL",
    "contact@example.com",
)

HEADERS = {
    "User-Agent": (
        f"spotify-data-platform/1.0 "
        f"({CONTACT_EMAIL})"
    )
}


def request_json(url: str, params: dict) -> dict:
    """Send a MusicBrainz request with retries and rate limiting."""

    for attempt in range(MAX_RETRIES):
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=30,
        )

        if response.status_code == 200:
            time.sleep(REQUEST_DELAY_SECONDS)
            return response.json()

        if response.status_code in {
            429,
            500,
            502,
            503,
            504,
        }:
            wait_seconds = 2 ** attempt

            print(
                f"MusicBrainz returned {response.status_code}. "
                f"Retrying in {wait_seconds}s..."
            )

            time.sleep(wait_seconds)
            continue

        response.raise_for_status()

    raise RuntimeError(
        "MusicBrainz request failed after multiple retries."
    )


def normalize_date(
    date_value: str | None,
) -> str | None:
    """Normalize MusicBrainz partial dates to YYYY-MM-DD."""

    if not date_value:
        return None

    if len(date_value) == 4:
        return f"{date_value}-01-01"

    if len(date_value) == 7:
        return f"{date_value}-01"

    return date_value


def normalize_country(
    country: str | None,
) -> str | None:
    """Normalize country codes used by the project."""

    if country == "GB":
        return "UK"

    return country


def fetch_artists(
    country: str,
    target_count: int,
) -> list[dict]:
    """Fetch artists for one country."""

    artists = []
    offset = 0

    while len(artists) < target_count:
        limit = min(
            PAGE_SIZE,
            target_count - len(artists),
        )

        data = request_json(
            f"{BASE_URL}/artist/",
            {
                "query": f"country:{country}",
                "fmt": "json",
                "limit": limit,
                "offset": offset,
            },
        )

        page = data.get("artists", [])

        if not page:
            break

        artists.extend(page)
        offset += len(page)

        print(
            f"{country}: "
            f"{len(artists)}/{target_count} artists"
        )

    return artists[:target_count]


def transform_artists(
    raw_artists: list[dict],
) -> list[dict]:
    """Transform MusicBrainz artists to the project schema."""

    artists = []

    for artist_id, artist in enumerate(
        raw_artists,
        start=1,
    ):
        genres = artist.get("genres", [])

        genre = (
            genres[0]["name"]
            if genres
            else None
        )

        artists.append(
            {
                "artist_id": artist_id,
                "artist_name": artist["name"],
                "genre": genre,
                "country": normalize_country(
                    artist.get("country")
                ),
                "_musicbrainz_id": artist["id"],
            }
        )

    return artists


def fetch_recordings_for_artist(
    artist_mbid: str,
) -> list[dict]:
    """Fetch recordings credited to one MusicBrainz artist."""

    data = request_json(
        f"{BASE_URL}/recording/",
        {
            "query": f"arid:{artist_mbid}",
            "fmt": "json",
            "limit": RECORDINGS_PER_ARTIST,
        },
    )

    return data.get("recordings", [])


def get_internal_artist_ids(
    recording: dict,
    artist_id_by_mbid: dict[str, int],
) -> set[int]:
    """Return project artist IDs credited on a recording."""

    artist_ids = set()

    for credit in recording.get(
        "artist-credit",
        [],
    ):
        credited_artist = credit.get("artist")

        if not credited_artist:
            continue

        artist_mbid = credited_artist.get("id")

        internal_artist_id = artist_id_by_mbid.get(
            artist_mbid
        )

        if internal_artist_id is not None:
            artist_ids.add(internal_artist_id)

    return artist_ids


def choose_album_release(
    recording: dict,
) -> dict | None:
    """Choose an official album release when available."""

    for release in recording.get(
        "releases",
        [],
    ):
        release_group = release.get(
            "release-group",
            {},
        )

        secondary_types = release_group.get(
            "secondary-types",
            [],
        )

        if (
            release.get("status") == "Official"
            and release_group.get("primary-type")
            == "Album"
            and "Compilation" not in secondary_types
        ):
            return release

    return None


def build_catalog(
    artists: list[dict],
) -> tuple[
    list[dict],
    list[dict],
    list[dict],
]:
    """Build tracks, albums, and track-artist relationships."""

    artist_id_by_mbid = {
        artist["_musicbrainz_id"]: artist["artist_id"]
        for artist in artists
    }

    raw_recordings = {}

    for index, artist in enumerate(
        artists,
        start=1,
    ):
        recordings = fetch_recordings_for_artist(
            artist["_musicbrainz_id"]
        )

        for recording in recordings:
            length_ms = recording.get("length")

            # Ignore recordings without a valid duration.
            if length_ms is None:
                continue
            duration_seconds = round(length_ms / 1000)

            if duration_seconds <= 0:
                continue

            # The recording must reference at least one
            # artist contained in our selected catalog.
            credited_artist_ids = (
                get_internal_artist_ids(
                    recording,
                    artist_id_by_mbid,
                )
            )

            if not credited_artist_ids:
                continue

            recording_mbid = recording["id"]

            # Avoid duplicate MusicBrainz recordings.
            if recording_mbid not in raw_recordings:
                raw_recordings[
                    recording_mbid
                ] = recording

        print(
            f"Artists processed: "
            f"{index}/{len(artists)} | "
            f"Valid unique recordings: "
            f"{len(raw_recordings)}"
        )

    if len(raw_recordings) < TRACK_TARGET:
        raise RuntimeError(
            f"Only {len(raw_recordings)} valid recordings "
            f"were found. Need {TRACK_TARGET}."
        )

    # Select tracks reproducibly without favoring
    # the countries/artists processed first.
    rng = random.Random(RANDOM_SEED)

    selected_recordings = rng.sample(
        list(raw_recordings.values()),
        TRACK_TARGET,
    )

    albums = []
    tracks = []
    track_artists = []

    album_id_by_mbid = {}

    for track_id, recording in enumerate(
        selected_recordings,
        start=1,
    ):
        duration_seconds = round(
            recording["length"] / 1000
        )

        album_release = choose_album_release(
            recording
        )

        album_id = None

        if album_release is not None:
            release_group = album_release.get(
                "release-group",
                {},
            )

            album_mbid = release_group.get("id")

            if album_mbid:
                if album_mbid not in album_id_by_mbid:
                    new_album_id = (
                        len(album_id_by_mbid) + 1
                    )

                    album_id_by_mbid[
                        album_mbid
                    ] = new_album_id

                    albums.append(
                        {
                            "album_id": new_album_id,
                            "album_name": album_release[
                                "title"
                            ],
                            "release_date": normalize_date(
                                album_release.get(
                                    "date"
                                )
                            ),
                        }
                    )

                album_id = album_id_by_mbid[
                    album_mbid
                ]

        tracks.append(
            {
                "track_id": track_id,
                "track_name": recording["title"],
                "album_id": album_id,
                "duration_seconds": duration_seconds,
                "release_date": normalize_date(
                    recording.get(
                        "first-release-date"
                    )
                ),
            }
        )

        credited_artist_ids = (
            get_internal_artist_ids(
                recording,
                artist_id_by_mbid,
            )
        )

        for artist_id in sorted(
            credited_artist_ids
        ):
            track_artists.append(
                {
                    "track_id": track_id,
                    "artist_id": artist_id,
                }
            )

    return albums, tracks, track_artists


def save_json(
    data: list[dict],
    output_file: Path,
) -> None:
    """Save data to a JSON file."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def main() -> None:
    """Fetch and build the real MusicBrainz catalog."""

    raw_artists = []

    for country, target_count in (
        ARTIST_TARGETS.items()
    ):
        country_artists = fetch_artists(
            country,
            target_count,
        )

        raw_artists.extend(
            country_artists
        )

    # Protect against duplicate artists returned
    # by different searches.
    unique_raw_artists = {
        artist["id"]: artist
        for artist in raw_artists
    }

    raw_artists = list(
        unique_raw_artists.values()
    )

    print(
        f"\nUnique artists fetched: "
        f"{len(raw_artists)}"
    )

    artists = transform_artists(
        raw_artists
    )

    albums, tracks, track_artists = (
        build_catalog(artists)
    )

    # Only publish artists that are actually used
    # by at least one selected track.
    used_artist_ids = {
        relationship["artist_id"]
        for relationship in track_artists
    }

    public_artists = [
        {
            "artist_id": artist["artist_id"],
            "artist_name": artist["artist_name"],
            "genre": artist["genre"],
            "country": artist["country"],
        }
        for artist in artists
        if artist["artist_id"] in used_artist_ids
    ]

    save_json(
        public_artists,
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

    print("\nCatalog complete")
    print(
        f"Artists: {len(public_artists)}"
    )
    print(
        f"Albums: {len(albums)}"
    )
    print(
        f"Tracks: {len(tracks)}"
    )
    print(
        "Track-artist relationships: "
        f"{len(track_artists)}"
    )


if __name__ == "__main__":
    main()