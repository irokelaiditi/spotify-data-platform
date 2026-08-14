SELECT
    track_id,
    track_name,
    album_id,
    duration_seconds,
    release_date
FROM {{ ref('stg_tracks') }}
WHERE duration_seconds > 0