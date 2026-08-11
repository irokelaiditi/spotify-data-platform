-- =========================================
-- Silver Catalog Transformation
-- =========================================

DROP TABLE IF EXISTS silver.track_artists;
DROP TABLE IF EXISTS silver.tracks;
DROP TABLE IF EXISTS silver.albums;
DROP TABLE IF EXISTS silver.artists;

-- Rebuild Silver artists table.


CREATE TABLE silver.artists AS
SELECT
    artist_id,
    artist_name,
    genre,
    country
FROM bronze.artists;

ALTER TABLE silver.artists
ADD CONSTRAINT pk_silver_artists
PRIMARY KEY (artist_id);

ALTER TABLE silver.artists
ALTER COLUMN artist_name SET NOT NULL;

-- Rebuild Silver albums table.


CREATE TABLE silver.albums AS
SELECT
    album_id,
    album_name,
    release_date
FROM bronze.albums;

ALTER TABLE silver.albums
ADD CONSTRAINT pk_silver_albums
PRIMARY KEY (album_id);

ALTER TABLE silver.albums
ALTER COLUMN album_name SET NOT NULL;

-- Rebuild Silver tracks table.


CREATE TABLE silver.tracks AS
SELECT
    track_id,
    track_name,
    album_id,
    duration_seconds,
    release_date
FROM bronze.tracks;

ALTER TABLE silver.tracks
ADD CONSTRAINT pk_silver_tracks
PRIMARY KEY (track_id);

ALTER TABLE silver.tracks
ALTER COLUMN track_name SET NOT NULL;

ALTER TABLE silver.tracks
ALTER COLUMN duration_seconds SET NOT NULL;

ALTER TABLE silver.tracks
ADD CONSTRAINT chk_silver_track_duration
CHECK (duration_seconds > 0);

ALTER TABLE silver.tracks
ADD CONSTRAINT fk_silver_tracks_album
FOREIGN KEY (album_id)
REFERENCES silver.albums(album_id);

-- Rebuild Silver track-artists junction table.


CREATE TABLE silver.track_artists AS
SELECT
    track_id,
    artist_id
FROM bronze.track_artists;

ALTER TABLE silver.track_artists
ADD CONSTRAINT pk_silver_track_artists
PRIMARY KEY (track_id, artist_id);

ALTER TABLE silver.track_artists
ADD CONSTRAINT fk_silver_track_artists_track
FOREIGN KEY (track_id)
REFERENCES silver.tracks(track_id);

ALTER TABLE silver.track_artists
ADD CONSTRAINT fk_silver_track_artists_artist
FOREIGN KEY (artist_id)
REFERENCES silver.artists(artist_id);

SELECT COUNT(*)
FROM silver.track_artists;

SELECT
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'silver'
  AND table_name = 'track_artists';


