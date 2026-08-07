CREATE TABLE IF NOT EXISTS bronze.track_artists (
    track_id INTEGER NOT NULL,
    artist_id INTEGER NOT NULL,

    CONSTRAINT pk_track_artists
        PRIMARY KEY (track_id, artist_id),

    CONSTRAINT fk_track_artists_track
        FOREIGN KEY (track_id)
        REFERENCES bronze.tracks(track_id),

    CONSTRAINT fk_track_artists_artist
        FOREIGN KEY (artist_id)
        REFERENCES bronze.artists(artist_id)
);