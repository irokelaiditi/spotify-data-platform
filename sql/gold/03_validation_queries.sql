-- =========================================
-- Gold Layer Validation Queries
-- =========================================


-- =========================================
-- 1. Daily Listening Metrics
-- =========================================
-- Every valid Silver listening event must be represented
-- exactly once in the daily listening metrics.

SELECT
    (SELECT COUNT(*)
     FROM silver.listening_events) AS silver_events,

    (SELECT SUM(total_events)
     FROM gold.daily_listening_metrics) AS gold_daily_events;


-- =========================================
-- 2. Track Performance
-- =========================================
-- Every valid listening event belongs to exactly one track,
-- therefore the totals must match.

SELECT
    (SELECT COUNT(*)
     FROM silver.listening_events) AS silver_events,

    (SELECT SUM(total_events)
     FROM gold.track_performance) AS gold_track_events;


-- =========================================
-- 3. Artist Performance
-- =========================================
-- Artist totals may exceed Silver event totals because tracks
-- can have multiple credited artists.

SELECT
    (SELECT COUNT(*)
     FROM silver.listening_events) AS silver_events,

    (SELECT SUM(total_events)
     FROM gold.artist_performance) AS gold_artist_events;


-- Count tracks credited to multiple artists.

SELECT COUNT(*) AS collaboration_tracks
FROM (
    SELECT track_id
    FROM silver.track_artists
    GROUP BY track_id
    HAVING COUNT(*) > 1
) AS collaborations;


-- =========================================
-- 4. Album Performance
-- =========================================
-- Album totals may be lower than Silver event totals because
-- album_id is optional in the catalog.

SELECT
    (SELECT COUNT(*)
     FROM silver.listening_events) AS silver_events,

    (SELECT SUM(total_events)
     FROM gold.album_performance) AS gold_album_events;


-- Count catalog tracks without an album relationship.

SELECT COUNT(*) AS tracks_without_album
FROM silver.tracks
WHERE album_id IS NULL;


-- =========================================
-- 5. Country Metrics
-- =========================================
-- Every valid Silver event must belong to one country.
-- Missing source countries are standardized to UNKNOWN.

SELECT
    (SELECT COUNT(*)
     FROM silver.listening_events) AS silver_events,

    (SELECT SUM(total_events)
     FROM gold.country_metrics) AS gold_country_events;


-- =========================================
-- 6. Device Metrics
-- =========================================
-- Every valid Silver event must belong to one device category.
-- Missing source devices are standardized to UNKNOWN.

SELECT
    (SELECT COUNT(*)
     FROM silver.listening_events) AS silver_events,

    (SELECT SUM(total_events)
     FROM gold.device_metrics) AS gold_device_events;


-- =========================================
-- 7. Subscription Metrics
-- =========================================
-- Every valid Silver event must belong to exactly one
-- standardized subscription type.

SELECT
    (SELECT COUNT(*)
     FROM silver.listening_events) AS silver_events,

    (SELECT SUM(total_events)
     FROM gold.subscription_metrics) AS gold_subscription_events;


-- =========================================
-- 8. Event Type Metrics
-- =========================================
-- Every valid Silver event must belong to exactly one
-- allowed event type.

SELECT
    (SELECT COUNT(*)
     FROM silver.listening_events) AS silver_events,

    (SELECT SUM(total_events)
     FROM gold.event_type_metrics) AS gold_event_type_events;


-- =========================================
-- 9. Engagement KPI Percentage Ranges
-- =========================================
-- Percentage metrics must remain between 0 and 100.
-- Expected result: zero rows.

SELECT *
FROM gold.engagement_kpis
WHERE
    played_event_percent < 0
    OR played_event_percent > 100
    OR paused_event_percent < 0
    OR paused_event_percent > 100
    OR skipped_event_percent < 0
    OR skipped_event_percent > 100
    OR completed_event_percent < 0
    OR completed_event_percent > 100;


-- =========================================
-- 10. Engagement KPI Percentage Total
-- =========================================
-- The four mutually exclusive event-type percentages should
-- sum to approximately 100%.
-- Small differences are acceptable due to rounding.

SELECT
    played_event_percent
    + paused_event_percent
    + skipped_event_percent
    + completed_event_percent
        AS total_event_percent
FROM gold.engagement_kpis;


-- =========================================
-- 11. Daily Event Metrics
-- =========================================
-- The sum of all event-type counts across all days must match
-- the number of valid Silver listening events.

SELECT
    (SELECT COUNT(*)
     FROM silver.listening_events) AS silver_events,

    (
        SELECT SUM(
            played_events
            + paused_events
            + completed_events
            + skipped_events
        )
        FROM gold.daily_event_metrics
    ) AS gold_daily_event_total;


-- =========================================
-- 12. Track Performance by Country
-- =========================================
-- Each valid Silver event belongs to exactly one track-country
-- combination, therefore totals must match.

SELECT
    (SELECT COUNT(*)
     FROM silver.listening_events) AS silver_events,

    (SELECT SUM(total_events)
     FROM gold.track_performance_by_country)
        AS gold_track_country_events;


-- =========================================
-- 13. Gold Track Referential Integrity
-- =========================================
-- Every track represented in Gold must exist in the
-- curated Silver catalog.
-- Expected result: 0.

SELECT COUNT(*) AS orphan_gold_tracks
FROM gold.track_performance AS gp
LEFT JOIN silver.tracks AS t
    ON gp.track_id = t.track_id
WHERE t.track_id IS NULL;