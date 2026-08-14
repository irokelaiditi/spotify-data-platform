SELECT
    artist_id,
    artist_name,
    genre,
    country
FROM {{ source('bronze', 'artists') }}