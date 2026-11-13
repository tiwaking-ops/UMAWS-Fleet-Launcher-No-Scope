# Toy workload card 14 — replay format notes

TOY-OK

This card records the replay format notes for the no-scope toy experiment
(`docs/phase0-verification-2026-11-11.md`). It is a single-owner card; no other
card writes this file.

## Replay format

Replay payloads are newline-delimited JSON objects, one per line, with the
following envelope:

```json
{"seq": <int>, "ts": "<ISO-8601>", "event": "<name>", "payload": {...}}
```

Fields:

- `seq` — monotonically increasing sequence number per stream.
- `ts` — UTC timestamp in ISO-8601 format.
- `event` — event name from the catalog in `docs/data-intake.md`.
- `payload` — event-specific data; may be empty `{}`.

## Ordering

Replay is strictly ordered by `seq`. Ties are not permitted; a duplicate
`seq` is a format error and the offending line is dropped.

## Notes

- All timestamps are UTC.
- The checker (`workload/check.py`) verifies only the presence of the
  `TOY-OK` marker; the format above is the contract for downstream consumers.