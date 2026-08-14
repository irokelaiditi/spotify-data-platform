SELECT
    track_id,
    track_name,
    album_id,
    duration_seconds,
    release_date
FROM {{ source('bronze', 'tracks') }}