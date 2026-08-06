DROP TABLE IF EXISTS silver.listening_events;

CREATE TABLE silver.listening_events AS
SELECT
    event_id,
    user_id,
    track_id,
    event_type,
    event_timestamp,
    COALESCE(device_type, 'UNKNOWN') AS device_type,
    COALESCE(country, 'UNKNOWN') AS country,
    LOWER(subscription_type) AS subscription_type,
    listening_duration_seconds
FROM bronze.listening_events
WHERE event_type IN (
    'track_played',
    'track_paused',
    'track_skipped',
    'track_completed'
)
  AND listening_duration_seconds >= 0;

ALTER TABLE silver.listening_events
ADD CONSTRAINT pk_silver_listening_events
PRIMARY KEY (event_id);

ALTER TABLE silver.listening_events
ALTER COLUMN country SET NOT NULL;

ALTER TABLE silver.listening_events
ALTER COLUMN device_type SET NOT NULL;

ALTER TABLE silver.listening_events
ADD CONSTRAINT chk_silver_event_type
CHECK (
    event_type IN (
        'track_played',
        'track_paused',
        'track_skipped',
        'track_completed'
    )
);

ALTER TABLE silver.listening_events
ADD CONSTRAINT chk_silver_subscription_type
CHECK (
    subscription_type IN (
        'free',
        'premium'
    )
);

ALTER TABLE silver.listening_events
ADD CONSTRAINT chk_silver_listening_duration
CHECK (
    listening_duration_seconds >= 0
);