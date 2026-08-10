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

SELECT COUNT(*)
FROM gold.track_performance;