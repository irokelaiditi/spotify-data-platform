WITH source AS (

    SELECT *
    FROM {{ ref('stg_listening_events') }}

),

cleaned AS (

    SELECT
        event_id,
        user_id,
        track_id,
        event_type,
        event_timestamp,

        COALESCE(
            device_type,
            'UNKNOWN'
        ) AS device_type,

        COALESCE(
            country,
            'UNKNOWN'
        ) AS country,

        LOWER(
            subscription_type
        ) AS subscription_type,

        listening_duration_seconds

    FROM source

    WHERE event_type IN (
        'track_played',
        'track_paused',
        'track_skipped',
        'track_completed'
    )

    AND listening_duration_seconds >= 0

),

deduplicated AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY
                user_id,
                track_id,
                event_type,
                event_timestamp
            ORDER BY event_id
        ) AS row_number

    FROM cleaned

)

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

FROM deduplicated

WHERE row_number = 1