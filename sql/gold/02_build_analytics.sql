-- =========================================
-- Gold Daily Listening Metrics
-- =========================================

DROP TABLE IF EXISTS gold.daily_listening_metrics;

CREATE TABLE gold.daily_listening_metrics AS
SELECT
    event_timestamp::date AS event_date,
    COUNT(*) AS total_events,
    COUNT(DISTINCT user_id) AS unique_users,
    SUM(listening_duration_seconds) AS total_listening_seconds,
    AVG(listening_duration_seconds) AS average_listening_seconds
FROM silver.listening_events
GROUP BY event_timestamp::date
ORDER BY event_date;

-- =========================================
-- Gold Track Performance
-- =========================================

DROP TABLE IF EXISTS gold.track_performance;

CREATE TABLE gold.track_performance AS
SELECT
    le.track_id,
    t.track_name,
    COUNT(*) AS total_events,
    COUNT(DISTINCT le.user_id) AS unique_listeners,
    SUM(le.listening_duration_seconds) AS total_listening_seconds,
    AVG(le.listening_duration_seconds) AS average_listening_seconds
FROM silver.listening_events AS le
JOIN silver.tracks AS t
    ON le.track_id = t.track_id
GROUP BY
    le.track_id,
    t.track_name
ORDER BY total_events DESC;

-- =========================================
-- Gold Artist Performance
-- =========================================

DROP TABLE IF EXISTS gold.artist_performance;

CREATE TABLE gold.artist_performance AS
SELECT
    a.artist_id,
    a.artist_name,
    COUNT(*) AS total_events,
    COUNT(DISTINCT le.user_id) AS unique_listeners,
    SUM(le.listening_duration_seconds) AS total_listening_seconds,
    AVG(le.listening_duration_seconds) AS average_listening_seconds
FROM silver.listening_events AS le
JOIN silver.track_artists AS ta
    ON le.track_id = ta.track_id
JOIN silver.artists AS a
    ON ta.artist_id = a.artist_id
GROUP BY
    a.artist_id,
    a.artist_name
ORDER BY total_events DESC;

-- =========================================
-- Gold Album Performance
-- =========================================

DROP TABLE IF EXISTS gold.album_performance;

CREATE TABLE gold.album_performance AS
SELECT
    a.album_id,
    a.album_name,
    COUNT(*) AS total_events,
    COUNT(DISTINCT le.user_id) AS unique_listeners,
    SUM(le.listening_duration_seconds) AS total_listening_seconds,
    AVG(le.listening_duration_seconds) AS average_listening_seconds
FROM silver.listening_events AS le
JOIN silver.tracks AS t
    ON le.track_id = t.track_id
JOIN silver.albums AS a
    ON t.album_id = a.album_id
GROUP BY
    a.album_id,
    a.album_name
ORDER BY total_events DESC;

-- =========================================
-- Gold Country Metrics
-- =========================================

DROP TABLE IF EXISTS gold.country_metrics;

CREATE TABLE gold.country_metrics AS
SELECT
    country,
    COUNT(*) AS total_events,
    COUNT(DISTINCT user_id) AS unique_users,
    SUM(listening_duration_seconds) AS total_listening_seconds,
    AVG(listening_duration_seconds) AS average_listening_seconds
FROM silver.listening_events
GROUP BY country
ORDER BY total_events DESC;


-- =========================================
-- Gold Device Metrics
-- =========================================

DROP TABLE IF EXISTS gold.device_metrics;

CREATE TABLE gold.device_metrics AS
SELECT
    device_type,
    COUNT(*) AS total_events,
    COUNT(DISTINCT user_id) AS unique_users,
    SUM(listening_duration_seconds) AS total_listening_seconds,
    AVG(listening_duration_seconds) AS average_listening_seconds
FROM silver.listening_events
GROUP BY device_type
ORDER BY total_events DESC;


-- =========================================
-- Gold Subscription Metrics
-- =========================================

DROP TABLE IF EXISTS gold.subscription_metrics;

CREATE TABLE gold.subscription_metrics AS
SELECT
    subscription_type,
    COUNT(*) AS total_events,
    COUNT(DISTINCT user_id) AS unique_users,
    SUM(listening_duration_seconds) AS total_listening_seconds,
    AVG(listening_duration_seconds) AS average_listening_seconds
FROM silver.listening_events
GROUP BY subscription_type
ORDER BY total_events DESC;

SELECT *
FROM gold.subscription_metrics
ORDER BY total_events DESC;

SELECT COUNT(DISTINCT user_id) AS total_users
FROM silver.listening_events;

-- =========================================
-- Gold Event Type Metrics
-- =========================================

DROP TABLE IF EXISTS gold.event_type_metrics;

CREATE TABLE gold.event_type_metrics AS
SELECT
    event_type,
    COUNT(*) AS total_events,
    COUNT(DISTINCT user_id) AS unique_users,
    SUM(listening_duration_seconds) AS total_listening_seconds,
    AVG(listening_duration_seconds) AS average_listening_seconds
FROM silver.listening_events
GROUP BY event_type
ORDER BY total_events DESC;


-- =========================================
-- Gold Engagement KPIs
-- =========================================

-- =========================================
-- Gold Engagement KPIs
-- =========================================

DROP TABLE IF EXISTS gold.engagement_kpis;

CREATE TABLE gold.engagement_kpis AS
SELECT
    COUNT(*) AS total_events,

    COUNT(*) FILTER (
        WHERE event_type = 'track_played'
    ) AS played_events,

    COUNT(*) FILTER (
        WHERE event_type = 'track_paused'
    ) AS paused_events,

    COUNT(*) FILTER (
        WHERE event_type = 'track_completed'
    ) AS completed_events,

    COUNT(*) FILTER (
        WHERE event_type = 'track_skipped'
    ) AS skipped_events,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE event_type = 'track_played'
        ) / COUNT(*),
        2
    ) AS played_event_percent,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE event_type = 'track_paused'
        ) / COUNT(*),
        2
    ) AS paused_event_percent,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE event_type = 'track_completed'
        ) / COUNT(*),
        2
    ) AS completed_event_percent,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE event_type = 'track_skipped'
        ) / COUNT(*),
        2
    ) AS skipped_event_percent

FROM silver.listening_events;


-- =========================================
-- Gold Daily Event Metrics
-- =========================================

DROP TABLE IF EXISTS gold.daily_event_metrics;

CREATE TABLE gold.daily_event_metrics AS
SELECT
    event_timestamp::date AS event_date,

    COUNT(*) FILTER (
        WHERE event_type = 'track_played'
    ) AS played_events,

    COUNT(*) FILTER (
        WHERE event_type = 'track_paused'
    ) AS paused_events,

    COUNT(*) FILTER (
        WHERE event_type = 'track_completed'
    ) AS completed_events,

    COUNT(*) FILTER (
        WHERE event_type = 'track_skipped'
    ) AS skipped_events,

    COUNT(DISTINCT user_id) AS unique_users

FROM silver.listening_events
GROUP BY event_timestamp::date
ORDER BY event_date;


-- =========================================
-- Gold Top Tracks by Country
-- =========================================

DROP TABLE IF EXISTS gold.track_performance_by_country;

CREATE TABLE gold.track_performance_by_country AS
SELECT
    le.country,
    le.track_id,
    t.track_name,
    COUNT(*) AS total_events,
    COUNT(DISTINCT le.user_id) AS unique_listeners,
    SUM(le.listening_duration_seconds) AS total_listening_seconds,
    AVG(le.listening_duration_seconds) AS average_listening_seconds
FROM silver.listening_events AS le
JOIN silver.tracks AS t
    ON le.track_id = t.track_id
GROUP BY
    le.country,
    le.track_id,
    t.track_name;




