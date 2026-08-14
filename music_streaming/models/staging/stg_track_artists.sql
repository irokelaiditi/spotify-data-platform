SELECT
    track_id,
    artist_id
FROM {{ source('bronze', 'track_artists') }}