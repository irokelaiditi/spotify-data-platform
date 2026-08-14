SELECT
    artist_id,
    artist_name,
    genre,
    CASE
        WHEN country = 'GB' THEN 'UK'
        ELSE country
    END AS country
FROM {{ ref('stg_artists') }}