# Toy workload card 04 — map index

TOY-OK

## Scope

Single-owner card. Writes only `workload/c04-mapindex.md`. No other card writes this file.

## Content

This card records the map-index format notes for the no-scope toy workload experiment (`docs/phase0-verification-2026-11-11.md`).

## Map index format

The map index is a fixed-record table used to locate entries in the companion payload store. Each record holds:

- `key` — the lookup key, UTF-8 encoded, fixed width within a table build.
- `offset` — byte offset of the payload in the store file, 64-bit unsigned little-endian.
- `len` — payload length in bytes, 32-bit unsigned little-endian.

Records are sorted ascending by `key` bytewise. Duplicate keys are not permitted; the second and later occurrences are dropped at build time.

## Lookup

A lookup binary-searches the index by `key`, reads `offset` and `len` from the matching record, then reads `len` bytes at `offset` from the store file.

## Notes

- All offsets are relative to the start of the store file.
- The checker (`workload/check.py`) verifies only the presence of the `TOY-OK` marker; the format above is the contract for downstream consumers.
