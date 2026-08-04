-- Stores raw synthetic listening events.
-- Bronze data may contain controlled data-quality issues.

CREATE TABLE IF NOT EXISTS bronze.listening_events (
    event_id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    event_timestamp TIMESTAMPTZ NOT NULL,
    device_type TEXT,
    country TEXT,
    subscription_type TEXT,
    listening_duration_seconds INTEGER
);