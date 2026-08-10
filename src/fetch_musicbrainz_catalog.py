import time
import requests
import json
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_URL = "https://musicbrainz.org/ws/2"

ARTIST_COUNTRIES = [
    "GR",
    "US",
    "GB",
    "DE",
    "FR",
    "IT",
]

ARTIST_TARGETS = {
    "GR": 200,
    "US": 300,
    "GB": 250,
    "DE": 100,
    "FR": 100,
    "IT": 50,
}

PAGE_SIZE = 100

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


def fetch_artists(country: str, target_count: int) -> list[dict]:
    """Fetch a target number of artists from MusicBrainz for one country."""

    artists = []
    offset = 0

    while len(artists) < target_count:
        limit = min(PAGE_SIZE, target_count - len(artists))

        for attempt in range(5):
            response = requests.get(
                f"{BASE_URL}/artist/",
                params={
                    "query": f"country:{country}",
                    "fmt": "json",
                    "limit": limit,
                    "offset": offset,
                },
                headers=HEADERS,
                timeout=30,
            )

            if response.status_code == 200:
                break

            if response.status_code == 503:
                wait_seconds = 2 ** attempt
                print(
                    f"MusicBrainz unavailable for {country}. "
                    f"Retrying in {wait_seconds}s..."
                )
                time.sleep(wait_seconds)
                continue

            response.raise_for_status()
        else:
            raise RuntimeError(
                f"Failed to fetch artists for {country} after retries."
            )

        page = response.json()["artists"]

        if not page:
            break

        artists.extend(page)
        offset += len(page)

        print(
            f"{country}: fetched {len(artists)}/{target_count} artists"
        )

        time.sleep(1.1)

    return artists[:target_count]

def transform_artists(raw_artists: list[dict]) -> list[dict]:
    """Transform MusicBrainz artists to the project schema."""

    artists = []

    for artist_id, artist in enumerate(raw_artists, start=1):
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
                "country": artist.get("country"),
            }
        )

    return artists

def save_json(data: list[dict], path: Path) -> None:
    """Save data to a JSON file."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def main() -> None:
    """Fetch, transform, and save the target artist catalog."""

    all_artists = []

    for country, target_count in ARTIST_TARGETS.items():
        artists = fetch_artists(country, target_count)
        all_artists.extend(artists)

    print(f"\nTotal artists fetched: {len(all_artists)}")

    transformed_artists = transform_artists(all_artists)

    save_json(
        transformed_artists,
        Path("data/raw/artists.json"),
    )

    print(f"Saved {len(transformed_artists)} artists")


if __name__ == "__main__":
    main()