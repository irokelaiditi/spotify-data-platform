SELECT
    album_id,
    album_name,
    release_date
FROM {{ source('bronze', 'albums') }}