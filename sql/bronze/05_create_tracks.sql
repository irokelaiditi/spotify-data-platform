CREATE TABLE IF NOT EXISTS bronze.tracks (
    track_id INTEGER PRIMARY KEY,
    track_name TEXT NOT NULL,
    album_id INTEGER,
    duration_seconds INTEGER NOT NULL,
    release_date DATE,

    CONSTRAINT fk_tracks_album
        FOREIGN KEY (album_id)
        REFERENCES bronze.albums(album_id)
);