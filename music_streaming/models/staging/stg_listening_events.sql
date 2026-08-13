SELECT
    event_id,
    user_id,
    track_id,
    event_type,
    event_timestamp,
    device_type,
    country,
    subscription_type,
    listening_duration_seconds
FROM {{ source('bronze', 'listening_events') }}