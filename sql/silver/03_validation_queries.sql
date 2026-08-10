-- Silver layer validation queries.
-- These checks confirm that the cleaned listening-events table
-- follows the agreed data-quality rules.

-- =========================================
-- Silver Listening Events Validations
-- =========================================

-- 1. Total number of Silver events.
SELECT COUNT(*) AS total_silver_events
FROM silver.listening_events;


-- 2. Required dimensions must not contain NULL values.
SELECT
    COUNT(*) FILTER (
        WHERE country IS NULL
    ) AS missing_country_count,
    COUNT(*) FILTER (
        WHERE device_type IS NULL
    ) AS missing_device_count
FROM silver.listening_events;


-- 3. Country and device fallback values.
SELECT
    COUNT(*) FILTER (
        WHERE country = 'UNKNOWN'
    ) AS unknown_country_count,
    COUNT(*) FILTER (
        WHERE device_type = 'UNKNOWN'
    ) AS unknown_device_count
FROM silver.listening_events;


-- 4. Only valid event types should exist.
SELECT
    event_type,
    COUNT(*) AS invalid_event_count
FROM silver.listening_events
WHERE event_type NOT IN (
    'track_played',
    'track_paused',
    'track_skipped',
    'track_completed'
)
GROUP BY event_type;


-- 5. Listening duration must not be negative.
SELECT COUNT(*) AS negative_duration_count
FROM silver.listening_events
WHERE listening_duration_seconds < 0;


-- 6. Subscription values must be standardized.
SELECT
    subscription_type,
    COUNT(*) AS invalid_subscription_count
FROM silver.listening_events
WHERE subscription_type NOT IN (
    'free',
    'premium'
)
GROUP BY subscription_type;


-- 7. Check the distribution of standardized subscription values.
SELECT
    subscription_type,
    COUNT(*) AS event_count
FROM silver.listening_events
GROUP BY subscription_type
ORDER BY event_count DESC;


-- 8. Primary key values must be unique.
SELECT
    event_id,
    COUNT(*) AS duplicate_event_id_count
FROM silver.listening_events
GROUP BY event_id
HAVING COUNT(*) > 1;


-- 9. Check for logical duplicate events.
SELECT
    user_id,
    track_id,
    event_type,
    event_timestamp,
    COUNT(*) AS duplicate_count
FROM silver.listening_events
GROUP BY
    user_id,
    track_id,
    event_type,
    event_timestamp
HAVING COUNT(*) > 1;


-- 10. Confirm that required identifier fields are not NULL.
SELECT
    COUNT(*) FILTER (
        WHERE event_id IS NULL
    ) AS missing_event_id_count,
    COUNT(*) FILTER (
        WHERE user_id IS NULL
    ) AS missing_user_id_count,
    COUNT(*) FILTER (
        WHERE track_id IS NULL
    ) AS missing_track_id_count,
    COUNT(*) FILTER (
        WHERE event_timestamp IS NULL
    ) AS missing_event_timestamp_count
FROM silver.listening_events;


-- 11. Compare Bronze and Silver row counts.
-- The difference represents records rejected by Silver filtering.
SELECT
    (SELECT COUNT(*) FROM bronze.listening_events) AS bronze_event_count,
    (SELECT COUNT(*) FROM silver.listening_events) AS silver_event_count,
    (
        SELECT COUNT(*) FROM bronze.listening_events
    ) - (
        SELECT COUNT(*) FROM silver.listening_events
    ) AS rejected_event_count;



-- =========================================
-- Silver Catalog Validations
-- =========================================

-- 1. Validate expected row counts.
SELECT COUNT(*) AS artist_count
FROM silver.artists;

SELECT COUNT(*) AS album_count
FROM silver.albums;

SELECT COUNT(*) AS track_count
FROM silver.tracks;

SELECT COUNT(*) AS track_artist_relationship_count
FROM silver.track_artists;


-- 2. Every non-null album_id must reference an existing Silver album.
SELECT COUNT(*) AS missing_album_count
FROM silver.tracks AS t
LEFT JOIN silver.albums AS a
    ON t.album_id = a.album_id
WHERE t.album_id IS NOT NULL
  AND a.album_id IS NULL;


-- 3. Every track-artist track_id must reference an existing Silver track.
SELECT COUNT(*) AS missing_track_count
FROM silver.track_artists AS ta
LEFT JOIN silver.tracks AS t
    ON ta.track_id = t.track_id
WHERE t.track_id IS NULL;


-- 4. Every track-artist artist_id must reference an existing Silver artist.
SELECT COUNT(*) AS missing_artist_count
FROM silver.track_artists AS ta
LEFT JOIN silver.artists AS a
    ON ta.artist_id = a.artist_id
WHERE a.artist_id IS NULL;


-- 5. Every listening-event track must exist in the Silver catalog.
SELECT COUNT(*) AS missing_listening_event_track_count
FROM silver.listening_events AS le
LEFT JOIN silver.tracks AS t
    ON le.track_id = t.track_id
WHERE t.track_id IS NULL;


-- 6. Track durations must be positive.
SELECT COUNT(*) AS invalid_track_duration_count
FROM silver.tracks
WHERE duration_seconds <= 0;


-- 7. Check for duplicate track-artist relationships.
SELECT
    track_id,
    artist_id,
    COUNT(*) AS duplicate_count
FROM silver.track_artists
GROUP BY
    track_id,
    artist_id
HAVING COUNT(*) > 1;