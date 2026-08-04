-- Bronze data-quality validation queries.

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