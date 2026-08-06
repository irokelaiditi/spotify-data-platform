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

### Deduplication

**Rule:** Keep only one row when multiple records represent the same business event.

The business key is defined as:

- `user_id`
- `track_id`
- `event_type`
- `event_timestamp`

**Reason:** Duplicate business events would inflate listening and activity metrics.

**Current dataset note:** No logical duplicates were found in the generated Bronze dataset using this business key.

## Silver Table Constraints

The Silver table applies database constraints in addition to transformation rules.

These constraints include:

- `event_id` as the primary key
- `country` must not be `NULL`
- `device_type` must not be `NULL`
- `event_type` must belong to the allowed list
- `subscription_type` must be either `free` or `premium`
- `listening_duration_seconds` must be greater than or equal to zero

**Reason:** Transformation rules clean the current dataset, while constraints protect the Silver table from invalid future inserts.