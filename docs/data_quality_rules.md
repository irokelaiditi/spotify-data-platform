# Data Quality Rules

This document defines the data-quality rules applied across the Spotify Data Platform.

## Bronze Layer

The Bronze layer stores ingested listening events as close to the source as possible.

No cleaning or correction is applied in this layer.

The Bronze layer may therefore contain:

- Missing values
- Invalid categorical values
- Negative listening durations
- Duplicate business events
- Inconsistent text formatting

## Silver Layer

The Silver layer contains cleaned and standardized listening events suitable for analytics.

### Country

**Rule:** Replace `NULL` values with `UNKNOWN`.

**Reason:** Country is optional metadata. A missing country does not make the listening event unusable.

### Device Type

**Rule:** Replace `NULL` values with `UNKNOWN`.

**Reason:** A missing device type does not invalidate the listening activity.

### Event Type

Allowed values:

- `track_played`
- `track_paused`
- `track_skipped`
- `track_completed`

**Rule:** Exclude rows with event types outside the allowed list.

**Reason:** Invalid event types cannot be classified reliably for analytics.

### Listening Duration

**Rule:** Exclude rows where `listening_duration_seconds` is negative.

**Reason:** Negative listening time indicates corrupted or invalid source data.

### Subscription Type

Allowed standardized values:

- `free`
- `premium`

**Rule:** Normalize values using lowercase formatting.

Example:

```text
PREMIUM → premium