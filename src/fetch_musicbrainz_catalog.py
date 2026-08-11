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

RELEASES_PER_ARTIST = 100
MAX_TRACKS_PER_ARTIST = 25

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

EXCLUDED_SECONDARY_TYPES = {
    "Compilation",
    "Demo",
    "DJ-mix",
    "Interview",
    "Live",
    "Mixtape/Street",
    "Remix",
    "Spokenword",
    "Audio drama",
    "Audiobook",
    "Field recording",
}

UNWANTED_TITLE_TERMS = {
    "instrumental",
    "karaoke",
    "a cappella",
    "acapella",
    "vocal stem",
    "drum stem",
    "bass stem",
    "guitar stem",
    "stem mix",
    "multitrack",
    "interview",
    "commentary",
    "spoken word",
    "soundcheck",
    "rehearsal",
    "demo version",
    "rough mix",
    "outtake",
    "alternate take",
    "alternative take",
    "live version",
    "live at ",
    "live from ",
    " remix",
    "remix)",
}

RELEASE_TYPE_PRIORITY = {
    "Single": 0,
    "Album": 1,
    "EP": 2,
}


def request_json(
    url: str,
    params: dict,
) -> dict:
    """Send a MusicBrainz request with retries and rate limiting."""

    for attempt in range(MAX_RETRIES):
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=60,
        )

        if response.status_code == 200:
            time.sleep(
                REQUEST_DELAY_SECONDS
            )

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
                f"MusicBrainz returned "
                f"{response.status_code}. "
                f"Retrying in {wait_seconds}s..."
            )

            time.sleep(
                wait_seconds
            )

            continue

        response.raise_for_status()

    raise RuntimeError(
        "MusicBrainz request failed "
        "after multiple retries."
    )


def normalize_date(
    date_value: str | None,
) -> str | None:
    """Normalize MusicBrainz partial dates to YYYY-MM-DD."""

    if not date_value:
        return None

    if len(date_value) == 4:
        return (
            f"{date_value}-01-01"
        )

    if len(date_value) == 7:
        return (
            f"{date_value}-01"
        )

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
    """Fetch artists from one country."""

    artists = []
    offset = 0

    while len(artists) < target_count:
        limit = min(
            100,
            target_count - len(artists),
        )

        data = request_json(
            f"{BASE_URL}/artist/",
            {
                "query": (
                    f"country:{country}"
                ),
                "fmt": "json",
                "limit": limit,
                "offset": offset,
            },
        )

        page = data.get(
            "artists",
            [],
        )

        if not page:
            break

        artists.extend(
            page
        )

        offset += len(
            page
        )

        print(
            f"{country}: "
            f"{len(artists)}/"
            f"{target_count} artists"
        )

    return artists[
        :target_count
    ]


def transform_artists(
    raw_artists: list[dict],
) -> list[dict]:
    """Transform MusicBrainz artists to the project schema."""

    artists = []

    for artist_id, artist in enumerate(
        raw_artists,
        start=1,
    ):
        genres = artist.get(
            "genres",
            [],
        )

        genre = (
            genres[0]["name"]
            if genres
            else None
        )

        artists.append(
            {
                "artist_id": artist_id,
                "artist_name": (
                    artist["name"]
                ),
                "genre": genre,
                "country": normalize_country(
                    artist.get(
                        "country"
                    )
                ),
                "_musicbrainz_id": (
                    artist["id"]
                ),
            }
        )

    return artists


def fetch_official_releases(
    artist_mbid: str,
) -> list[dict]:
    """
    Fetch official Album, Single and EP releases
    for one artist, including their recordings.
    """

    data = request_json(
        f"{BASE_URL}/release/",
        {
            "artist": artist_mbid,
            "status": "official",
            "type": (
                "album|single|ep"
            ),
            "inc": (
                "recordings"
                "+artist-credits"
                "+release-groups"
                "+isrcs"
            ),
            "fmt": "json",
            "limit": (
                RELEASES_PER_ARTIST
            ),
        },
    )

    return data.get(
        "releases",
        [],
    )


def has_excluded_release_type(
    release: dict,
) -> bool:
    """Check whether the release belongs to an unwanted release category."""

    release_group = release.get(
        "release-group",
        {},
    )

    secondary_types = set(
        release_group.get(
            "secondary-types",
            [],
        )
    )

    return bool(
        secondary_types
        & EXCLUDED_SECONDARY_TYPES
    )


def is_suspicious_title(
    title: str,
) -> bool:
    """Identify obvious non-standard or low-quality recording titles."""

    cleaned = title.strip()

    if not cleaned:
        return True

    if len(cleaned) > 120:
        return True

    lowered = cleaned.lower()

    for term in (
        UNWANTED_TITLE_TERMS
    ):
        if term in lowered:
            return True

    letter_count = sum(
        character.isalpha()
        for character in cleaned
    )

    if letter_count < 2:
        return True

    visible_characters = [
        character
        for character in cleaned
        if not character.isspace()
    ]

    if not visible_characters:
        return True

    non_letter_count = sum(
        not character.isalpha()
        for character
        in visible_characters
    )

    non_letter_ratio = (
        non_letter_count
        / len(
            visible_characters
        )
    )

    if (
        len(visible_characters) >= 8
        and non_letter_ratio > 0.55
    ):
        return True

    return False


def get_release_type(
    release: dict,
) -> str | None:
    """Return the primary release-group type."""

    release_group = release.get(
        "release-group",
        {},
    )

    return release_group.get(
        "primary-type"
    )


def get_recording_artist_ids(
    track: dict,
    artist_id_by_mbid: dict[str, int],
) -> set[int]:
    """Return project artist IDs credited on a release track."""

    artist_ids = set()

    artist_credit = track.get(
        "artist-credit",
        [],
    )

    recording = track.get(
        "recording",
        {},
    )

    if not artist_credit:
        artist_credit = recording.get(
            "artist-credit",
            [],
        )

    for credit in artist_credit:
        artist = credit.get(
            "artist"
        )

        if not artist:
            continue

        artist_mbid = artist.get(
            "id"
        )

        internal_artist_id = (
            artist_id_by_mbid.get(
                artist_mbid
            )
        )

        if (
            internal_artist_id
            is not None
        ):
            artist_ids.add(
                internal_artist_id
            )

    return artist_ids


def candidate_score(
    candidate: dict,
) -> tuple:
    """
    Rank track candidates.

    Preference is given to recordings with an ISRC,
    singles, releases with barcodes and earlier track
    positions within the release.
    """

    has_isrc = bool(
        candidate[
            "recording"
        ].get(
            "isrcs",
            [],
        )
    )

    release_type = candidate[
        "release_type"
    ]

    release_type_priority = (
        RELEASE_TYPE_PRIORITY.get(
            release_type,
            99,
        )
    )

    has_barcode = bool(
        candidate[
            "release"
        ].get(
            "barcode"
        )
    )

    track_position = candidate.get(
        "track_position",
        999,
    )

    return (
        0 if has_isrc else 1,
        release_type_priority,
        0 if has_barcode else 1,
        track_position,
    )


def collect_artist_candidates(
    artist: dict,
    artist_id_by_mbid: dict[str, int],
) -> list[dict]:
    """Collect curated commercial track candidates for one artist."""

    releases = fetch_official_releases(
        artist[
            "_musicbrainz_id"
        ]
    )

    candidates_by_recording = {}

    for release in releases:
        if has_excluded_release_type(
            release
        ):
            continue

        release_type = (
            get_release_type(
                release
            )
        )

        if release_type not in {
            "Album",
            "Single",
            "EP",
        }:
            continue

        for medium in release.get(
            "media",
            [],
        ):
            for track in medium.get(
                "tracks",
                [],
            ):
                recording = track.get(
                    "recording"
                )

                if not recording:
                    continue

                recording_mbid = (
                    recording.get(
                        "id"
                    )
                )

                title = (
                    recording.get(
                        "title"
                    )
                    or track.get(
                        "title"
                    )
                )

                length_ms = (
                    recording.get(
                        "length"
                    )
                    or track.get(
                        "length"
                    )
                )

                if (
                    not recording_mbid
                    or not title
                    or length_ms is None
                ):
                    continue

                duration_seconds = round(
                    length_ms
                    / 1000
                )

                if (
                    duration_seconds
                    <= 0
                ):
                    continue

                if is_suspicious_title(
                    title
                ):
                    continue

                credited_artist_ids = (
                    get_recording_artist_ids(
                        track,
                        artist_id_by_mbid,
                    )
                )

                if not credited_artist_ids:
                    continue

                candidate = {
                    "recording": recording,
                    "recording_mbid": (
                        recording_mbid
                    ),
                    "track_title": title,
                    "duration_seconds": (
                        duration_seconds
                    ),
                    "release": release,
                    "release_type": (
                        release_type
                    ),
                    "track_position": (
                        track.get(
                            "position",
                            999,
                        )
                    ),
                    "credited_artist_ids": (
                        credited_artist_ids
                    ),
                }

                existing = (
                    candidates_by_recording.get(
                        recording_mbid
                    )
                )

                if (
                    existing is None
                    or candidate_score(
                        candidate
                    )
                    < candidate_score(
                        existing
                    )
                ):
                    candidates_by_recording[
                        recording_mbid
                    ] = candidate

    candidates = list(
        candidates_by_recording.values()
    )

    candidates.sort(
        key=candidate_score
    )

    return candidates[
        :MAX_TRACKS_PER_ARTIST
    ]


def build_catalog(
    artists: list[dict],
) -> tuple[
    list[dict],
    list[dict],
    list[dict],
]:
    """Build curated tracks, albums and track-artist relationships."""

    artist_id_by_mbid = {
        artist[
            "_musicbrainz_id"
        ]: artist[
            "artist_id"
        ]
        for artist in artists
    }

    catalog_candidates = {}
    album_release_by_recording = {}

    for index, artist in enumerate(
        artists,
        start=1,
    ):
        artist_candidates = (
            collect_artist_candidates(
                artist,
                artist_id_by_mbid,
            )
        )

        for candidate in (
            artist_candidates
        ):
            recording_mbid = (
                candidate[
                    "recording_mbid"
                ]
            )

            existing = (
                catalog_candidates.get(
                    recording_mbid
                )
            )

            if (
                existing is None
                or candidate_score(
                    candidate
                )
                < candidate_score(
                    existing
                )
            ):
                catalog_candidates[
                    recording_mbid
                ] = candidate

            if (
                candidate[
                    "release_type"
                ]
                == "Album"
            ):
                album_release_by_recording[
                    recording_mbid
                ] = candidate[
                    "release"
                ]

        print(
            f"Artists processed: "
            f"{index}/{len(artists)} | "
            f"Curated recordings: "
            f"{len(catalog_candidates)}"
        )

    if (
        len(catalog_candidates)
        < TRACK_TARGET
    ):
        raise RuntimeError(
            f"Only "
            f"{len(catalog_candidates)} "
            f"curated recordings were "
            f"found. Need "
            f"{TRACK_TARGET}."
        )

    candidates = list(
        catalog_candidates.values()
    )

    candidates.sort(
        key=candidate_score
    )

    #
    # We keep the catalog reproducible while
    # avoiding a catalog made only of the
    # highest-ranked candidate type.
    #
    # First select a high-quality pool and then
    # deterministically sample the final tracks.
    #
    quality_pool_size = min(
        len(candidates),
        max(
            TRACK_TARGET,
            int(
                TRACK_TARGET
                * 1.5
            ),
        ),
    )

    quality_pool = candidates[
        :quality_pool_size
    ]

    rng = random.Random(
        RANDOM_SEED
    )

    if (
        len(quality_pool)
        == TRACK_TARGET
    ):
        selected_candidates = (
            quality_pool
        )
    else:
        selected_candidates = (
            rng.sample(
                quality_pool,
                TRACK_TARGET,
            )
        )

    albums = []
    tracks = []
    track_artists = []

    album_id_by_release_group = {}

    for track_id, candidate in enumerate(
        selected_candidates,
        start=1,
    ):
        recording_mbid = candidate[
            "recording_mbid"
        ]

        album_release = (
            album_release_by_recording.get(
                recording_mbid
            )
        )

        album_id = None

        if album_release is not None:
            release_group = (
                album_release.get(
                    "release-group",
                    {},
                )
            )

            release_group_mbid = (
                release_group.get(
                    "id"
                )
            )

            if release_group_mbid:
                if (
                    release_group_mbid
                    not in
                    album_id_by_release_group
                ):
                    new_album_id = (
                        len(
                            album_id_by_release_group
                        )
                        + 1
                    )

                    album_id_by_release_group[
                        release_group_mbid
                    ] = new_album_id

                    albums.append(
                        {
                            "album_id": (
                                new_album_id
                            ),
                            "album_name": (
                                release_group.get(
                                    "title"
                                )
                                or album_release.get(
                                    "title"
                                )
                            ),
                            "release_date": (
                                normalize_date(
                                    album_release.get(
                                        "date"
                                    )
                                )
                            ),
                        }
                    )

                album_id = (
                    album_id_by_release_group[
                        release_group_mbid
                    ]
                )

        release_date = normalize_date(
            candidate[
                "release"
            ].get(
                "date"
            )
        )

        tracks.append(
            {
                "track_id": track_id,
                "track_name": (
                    candidate[
                        "track_title"
                    ]
                ),
                "album_id": album_id,
                "duration_seconds": (
                    candidate[
                        "duration_seconds"
                    ]
                ),
                "release_date": (
                    release_date
                ),
            }
        )

        for artist_id in sorted(
            candidate[
                "credited_artist_ids"
            ]
        ):
            track_artists.append(
                {
                    "track_id": (
                        track_id
                    ),
                    "artist_id": (
                        artist_id
                    ),
                }
            )

    return (
        albums,
        tracks,
        track_artists,
    )


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
    """Fetch and build the curated MusicBrainz catalog."""

    raw_artists = []

    for (
        country,
        target_count,
    ) in ARTIST_TARGETS.items():
        country_artists = (
            fetch_artists(
                country,
                target_count,
            )
        )

        raw_artists.extend(
            country_artists
        )

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

    (
        albums,
        tracks,
        track_artists,
    ) = build_catalog(
        artists
    )

    used_artist_ids = {
        relationship[
            "artist_id"
        ]
        for relationship
        in track_artists
    }

    public_artists = [
        {
            "artist_id": (
                artist[
                    "artist_id"
                ]
            ),
            "artist_name": (
                artist[
                    "artist_name"
                ]
            ),
            "genre": (
                artist[
                    "genre"
                ]
            ),
            "country": (
                artist[
                    "country"
                ]
            ),
        }
        for artist in artists
        if (
            artist[
                "artist_id"
            ]
            in used_artist_ids
        )
    ]

    save_json(
        public_artists,
        Path(
            "data/raw/artists.json"
        ),
    )

    save_json(
        albums,
        Path(
            "data/raw/albums.json"
        ),
    )

    save_json(
        tracks,
        Path(
            "data/raw/tracks.json"
        ),
    )

    save_json(
        track_artists,
        Path(
            "data/raw/track_artists.json"
        ),
    )

    print(
        "\nCatalog complete"
    )

    print(
        f"Artists: "
        f"{len(public_artists)}"
    )

    print(
        f"Albums: "
        f"{len(albums)}"
    )

    print(
        f"Tracks: "
        f"{len(tracks)}"
    )

    print(
        "Track-artist "
        "relationships: "
        f"{len(track_artists)}"
    )


if __name__ == "__main__":
    main()