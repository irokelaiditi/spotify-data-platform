SELECT
    album_id,
    album_name,
    release_date
FROM {{ ref('stg_albums') }}