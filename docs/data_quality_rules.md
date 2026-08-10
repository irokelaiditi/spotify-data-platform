# Data Quality Rules

This document defines the data-quality rules applied across the Spotify Data Platform.

## Bronze Layer

The Bronze layer stores ingested data as close to the source as possible.

No cleaning or correction is applied in this layer.

The Bronze layer may therefore contain:

- Missing values
- Invalid categorical values
- Negative listening durations
- Duplicate business events
- Inconsistent text formatting

Data-quality rules are applied when data is transformed into the Silver layer.

---

## Silver Layer

The Silver layer contains cleaned, standardized and validated datasets suitable for analytics.

### Listening Events

#### Country

**Rule:** Replace `NULL` values with `UNKNOWN`.

**Reason:** Country is optional metadata. A missing country does not make the listening event unusable.

#### Device Type

**Rule:** Replace `NULL` values with `UNKNOWN`.

**Reason:** A missing device type does not invalidate the listening activity.

#### Event Type

Allowed values:

- `track_played`
- `track_paused`
- `track_skipped`
- `track_completed`

**Rule:** Exclude rows with event types outside the allowed list.

**Reason:** Invalid event types cannot be classified reliably for analytics.

#### Listening Duration

**Rule:** Exclude rows where `listening_duration_seconds` is negative.

**Reason:** Negative listening time indicates corrupted or invalid source data.

#### Subscription Type

Allowed standardized values:

- `free`
- `premium`

**Rule:** Normalize values using lowercase formatting.

Example:

```text
PREMIUM → premium
```

#### Deduplication

**Rule:** Keep only one row when multiple records represent the same business event.

The business key is defined as:

- `user_id`
- `track_id`
- `event_type`
- `event_timestamp`

**Reason:** Duplicate business events would inflate listening and activity metrics.

**Current dataset note:** No logical duplicates were found in the generated Bronze dataset using this business key.

---

### Music Catalog

Music catalog metadata is sourced from MusicBrainz and normalized before being used for analytics.

#### Track Duration

**Rule:** Recordings without a valid positive duration are excluded from the catalog.

**Reason:** Track duration is required for reliable track-level analysis. Missing or invalid durations are not replaced with synthetic values.

#### Release Dates

**Rule:** Partial MusicBrainz dates are normalized into complete SQL-compatible dates.

Examples:

```text
1992       → 1992-01-01
1967-10    → 1967-10-01
2000-04-03 → 2000-04-03
```

Missing release dates remain `NULL`.

**Reason:** MusicBrainz may provide partial dates, while PostgreSQL `DATE` columns require complete dates.

#### Artist Country

**Rule:** MusicBrainz country code `GB` is normalized to `UK`.

**Reason:** This maintains a consistent country-code convention across the project datasets.

#### Track-Artist Relationships

**Rule:** Every track must be associated with at least one artist included in the catalog.

**Reason:** Tracks without an artist relationship cannot be reliably used for artist-level analytics.

The catalog supports many-to-many track-artist relationships so that collaborations and tracks with multiple credited artists can be represented correctly.

#### Album Relationships

**Rule:** `album_id` may be `NULL`.

**Reason:** Not every recording is associated with an eligible album release. Tracks without an album remain valid catalog records.

#### Artist Genre

**Rule:** Missing artist genres remain `NULL`.

**Reason:** Missing source metadata is preserved rather than replaced with invented or inferred values.

#### Duplicate Recordings

**Rule:** MusicBrainz recordings are deduplicated using their MusicBrainz recording identifier before internal track IDs are assigned.

**Reason:** The same recording may be returned through multiple artists, particularly for collaborations. Deduplication prevents duplicate catalog tracks.

---

## Silver Table Constraints

The Silver layer applies database constraints in addition to transformation rules.

### Listening Events

Constraints include:

- `event_id` as the primary key
- `country` must not be `NULL`
- `device_type` must not be `NULL`
- `event_type` must belong to the allowed list
- `subscription_type` must be either `free` or `premium`
- `listening_duration_seconds` must be greater than or equal to zero

### Catalog

Relational integrity rules ensure that:

- Artist, track and album identifiers are unique
- Track-artist relationships reference valid tracks and artists
- Track durations contain valid non-negative values
- Album relationships remain optional
- Duplicate track-artist relationships are prevented

**Reason:** Transformation rules clean and standardize the current datasets, while database constraints protect the Silver layer from invalid future records.