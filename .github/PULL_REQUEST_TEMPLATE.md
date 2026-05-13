# Pull request

## What this PR does

<!-- One-line summary -->

## Type

- [ ] New PGN addition (standard ISO 11783 or J1939)
- [ ] Signal-level enrichment of an existing PGN
- [ ] Tooling change (extractor / inferrer / coverage / anonymize)
- [ ] Documentation
- [ ] CI / repo plumbing
- [ ] Other (please describe)

## Source citation

<!-- For DBC additions: cite the public source. Required. -->
<!-- Example: isobus.net VDMA Data Dictionary detail page <URL>, Wikipedia J1939 PGN table, AgIsoStack++ <file>:<line>, etc. -->

## Scope policy check

- [ ] PGN ID is NOT in proprietary range (`0xEF00` or `0xFF00..0xFFFF`)
- [ ] Source is public (not transcribed from paywalled spec PDF)
- [ ] No OEM proprietary CAN content reverse-engineered

## CI check

- [ ] `pytest` passes locally (6/6 smoke tests minimum)
- [ ] `canmatrix --check` parses all DBC files without errors
- [ ] No new cross-DBC duplicate PGN IDs introduced

## Signal-naming convention

<!-- If adding signals: see docs/signal-naming-guide.md -->
- [ ] Signal names follow the prefix conventions (`TRACTOR_*`, `IMPLEMENT_*`, `J1939_*`, `VDMA_*` for placeholders)
- [ ] Units are in standard SI where applicable
- [ ] Value tables (enum-like signals) use uppercase-PascalCase labels

## Notes for reviewer
