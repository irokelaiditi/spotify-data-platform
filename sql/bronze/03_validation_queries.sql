-- Bronze data-quality validation queries.

-- =========================================
-- Bronze Listening Events Validations
-- =========================================

-- Total events.
SELECT COUNT(*) AS total_events
FROM bronze.listening_events;


-- Missing countries.
SELECT COUNT(*) AS missing_country_count
FROM bronze.listening_events
WHERE country IS NULL;


-- Missing device types.
SELECT COUNT(*) AS missing_device_count
FROM bronze.listening_events
WHERE device_type IS NULL;


-- Invalid event types.
SELECT
    event_type,
    COUNT(*) AS event_count
FROM bronze.listening_events
WHERE event_type NOT IN (
    'track_played',
    'track_paused',
    'track_skipped',
    'track_completed'
)
GROUP BY event_type;


-- Invalid listening durations.
SELECT COUNT(*) AS invalid_duration_count
FROM bronze.listening_events
WHERE listening_duration_seconds < 0;


-- Inconsistent subscription values.
SELECT
    subscription_type,
    COUNT(*) AS event_count
FROM bronze.listening_events
GROUP BY subscription_type
ORDER BY event_count DESC;


-- =========================================
-- Bronze Catalog Validations
-- =========================================

-- Check that every listening-event track exists in the catalog.
SELECT COUNT(*) AS missing_track_count
FROM bronze.listening_events AS le
LEFT JOIN bronze.tracks AS t
    ON le.track_id = t.track_id
WHERE t.track_id IS NULL;


-- Check that non-null track album IDs exist.
SELECT COUNT(*) AS missing_album_count
FROM bronze.tracks AS t
LEFT JOIN bronze.albums AS a
    ON t.album_id = a.album_id
WHERE t.album_id IS NOT NULL
  AND a.album_id IS NULL;


-- Check that every track-artist track exists.
SELECT COUNT(*) AS missing_track_artist_track_count
FROM bronze.track_artists AS ta
LEFT JOIN bronze.tracks AS t
    ON ta.track_id = t.track_id
WHERE t.track_id IS NULL;


-- Check that every track-artist artist exists.
SELECT COUNT(*) AS missing_track_artist_artist_count
FROM bronze.track_artists AS ta
LEFT JOIN bronze.artists AS a
    ON ta.artist_id = a.artist_id
WHERE a.artist_id IS NULL;


-- Check for duplicate track-artist relationships.
SELECT
    track_id,
    artist_id,
    COUNT(*) AS duplicate_count
FROM bronze.track_artists
GROUP BY track_id, artist_id
HAVING COUNT(*) > 1;