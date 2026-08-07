CREATE TABLE IF NOT EXISTS bronze.artists (
    artist_id INTEGER PRIMARY KEY,
    artist_name TEXT NOT NULL,
    genre TEXT,
    country TEXT
);