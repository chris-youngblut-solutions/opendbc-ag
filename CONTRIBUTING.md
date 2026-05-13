# Contributing to opendbc-ag

opendbc-ag is the OSS canonical ag-CAN DBC repository. Contributions are welcome — this guide tells you what fits in scope and how to submit.

## Scope policy

**opendbc-ag is pure-standard.** We accept PGNs from:

- ISO 11783 (ISOBUS) public summaries — primary source: [isobus.net](https://www.isobus.net/isobus/) VDMA Data Dictionary
- SAE J1939 ag-relevant subset — primary source: Wikipedia + CSS Electronics free educational content + community-curated repositories
- AgIsoStack++ MIT-licensed C++ source (Open-Agriculture/AgIsoStack-plus-plus)

**We do NOT accept:**

- PGNs in proprietary ranges `0xEF00` or `0xFF00..0xFFFF` (CI auto-rejects)
- Reverse-engineered OEM proprietary CAN bus data (John Deere, CNH, AGCO, Kubota, Kinze, Hagie, Brent, or any other OEM proprietary content)
- Content transcribed verbatim from paywalled spec PDFs (ISO 11783-X, SAE J1939-X)
- Anything that would violate the OEM's TOS or DMCA §1201 absent a research/repair exemption

If you have proprietary-OEM reverse-engineered DBCs and want a place to publish them, look at the [Tractor Hacking project](https://tractorhacking.github.io/) which has secured a DMCA §1201 exemption for John Deere research. opendbc-ag stays in pure-standard land.

See [`docs/legal-context.md`](docs/legal-context.md) for the rationale.

## How to contribute

### 1. New PGN at standard PGN-level

Use the [`new-pgn`](.github/ISSUE_TEMPLATE/new-pgn.yml) issue template, or open a PR directly with:

- Add a `BO_` entry to the appropriate DBC file under `opendbc_ag/dbc/`
- Cite the public source (URL, paper DOI, or library file:line) in a `CM_` comment on the frame
- At minimum add one `SG_` signal — even if it's a `RawPayload` placeholder

CI must pass:

- `canmatrix --check` on the DBC file (run locally first: `python -c "from canmatrix import formats; formats.loadp('opendbc_ag/dbc/<your>.dbc')"`)
- No proprietary-range PGNs
- No cross-DBC duplicate PGN IDs

### 2. Signal enrichment of an existing PGN

The `iso11783_from_vdma.dbc` file has ~2,900 PGN-level entries with `RawPayload` placeholders. Enriching any of these with actual signal-level definitions is a high-value contribution.

Workflow:

1. Look up the PGN on the detail-page URL in the DBC's `CM_` comment
2. Define signals per the [`docs/signal-naming-guide.md`](docs/signal-naming-guide.md) conventions
3. Submit a PR that replaces the placeholder signal with the enriched signal list
4. Cite the source in each signal's `CM_` comment

### 3. Tooling improvements

- `opendbc_ag/tools/dbc_inferrer.py` — heuristic DBC inference; improvements via Edge-Impulse-style ML welcome
- `opendbc_ag/tools/coverage_report.py` — expand coverage matrix detail
- `opendbc_ag/tools/anonymize.py` — PII stripping for `corpus/` submissions; improvements welcome

### 4. Reference CAN traces (`corpus/`)

When the manual-phase capture work begins, raw CAN traces will land in `corpus/`. Submissions MUST be processed through `opendbc_ag/tools/anonymize.py` first.

## PR workflow

1. Fork the repo
2. Create a feature branch (`feat/<short-description>`)
3. Make changes locally; run `pytest` to confirm 6/6 smoke tests pass
4. Open a PR against `main`
5. Fill out the PR template (source citation, scope check, CI green, signal-naming compliance)
6. Address review feedback
7. Squash-merge once approved

## Code of conduct

By participating you agree to the [Contributor Covenant 2.1](docs/code-of-conduct.md).

## License of contributions

By submitting a PR you agree your contribution is offered under the [MIT License](LICENSE) matching this repo's licensing.

## Questions?

Open a [discussion](https://github.com/in-loop/opendbc-ag/discussions) or a bug-report issue.
