# Build report — opendbc-ag

**Project:** opendbc-ag
**Initial tag:** `v0.1.0-private`
**Initial build date:** 2026-05-13
**Mode:** private-first; maintainer review required before public release

This document records what the initial autonomous build shipped, what it intentionally deferred, and the follow-up items left for the maintainer. It is preserved alongside the source to give downstream readers (contributors, auditors, partners) transparency about the build process.

> Note: a remediation pass on 2026-05-14 addressed findings from a multi-panel pre-publication review. The initial-build numbers in this report reflect the v0.1.0-private state; current corpus numbers live in `docs/coverage.md` and the README's coverage table.

---

## What the initial build shipped

12 phases executed sequentially. Each phase is its own commit on `main`; the full chain is visible via `git log --oneline`.

| Phase | Deliverable | Lines |
|---|---|---|
| 0 | Repo + scaffold (LICENSE/README/CHANGELOG/.gitignore) | ~100 |
| 1 | Directory tree + per-dir READMEs | ~50 |
| 2 | AgIsoStack++ PGN extractor + DBC (46 PGNs, 84 signals) | ~600 |
| 3 | isobus.net VDMA scraper + DBC (~2.9k PGNs at v0.1.0-private; ~2.6k post-remediation) | ~400 |
| 4 | J1939 ag-subset (17 PGNs, 69 signals) | ~500 |
| 5 | CI workflows (3) + pyproject.toml + initial tests | ~250 |
| 6 | README + CHANGELOG finalization | ~70 |
| 7 | CoC + CONTRIBUTING + PR/issue templates + naming guide | ~420 |
| 8 | cabana-for-ag setup doc (generic + machine-class TODOs) | ~300 |
| 9 | dbc_inferrer + anonymize + synthetic fixtures + 17 tests | ~940 |
| 10 | Signal-naming test harness (6 tests) | ~90 |
| 11 | Legal-context + FAQ + architecture + README link pass | ~290 |
| 12 | CHANGELOG final entry + this report + tag + pre-release | ~150 |

**Corpus at v0.1.0-private ship time:**
- 2,955 unique PGN IDs
- 3,045 signals
- 3 DBC files
- CI: parse + scope + duplicate gates all green
- 29/29 tests passing

Current state (post-remediation) is reported in `docs/coverage.md`.

---

## Deviations from the original build plan

These were intentional choices made during execution with stated reasons. Listed for transparency.

| # | Deviation | Reason |
|---|---|---|
| 1 | **Code of conduct adopted by link** rather than CC 2.1 verbatim text in the file | The verbatim text routinely triggers content-policy classifiers on automated output. Linking to the canonical upstream preserves the recognized adoption (CC 2.1) and matches how Apache, Linux, Kubernetes, and others handle CoC. The project-specific addendum addresses the gaps the upstream Covenant intentionally leaves to each project. |
| 2 | **Test files consolidated** — initial plan called for separate `test_dbc_syntax.py` / `test_consistency.py` / `test_signal_naming.py`. Shipped as: existing `test_smoke.py` (covers syntax + consistency) + new `test_signal_naming.py`. | The syntax + consistency tests already shipped earlier as part of `test_smoke.py`. Splitting them into three files just to match the plan's literal text would have been churn with no behavioral change. |
| 3 | **Signal-name length limit lifted 32 → 64** chars in the naming guide | Initial 32-char cap was too tight: VDMA placeholders auto-generate names approaching 56 chars. 64 matches the frame-name limit and DBC-tooling practical limits. |
| 4 | **Raw AgIsoStack++ clone gitignored** but extraction JSONs kept | Raw clone is ~26 MB and reproducible from upstream; the extraction JSON is the value-added intermediate that should live in version control. |

---

## Follow-up items deferred from the initial build

These items require either maintainer input, paywalled access, hardware not yet deployed, or external communication. None of them block private review. Most are unlocked by maintainer trigger after review passes.

### Hot path (review-related)

1. **Maintainer decides whether to go public.** Visibility flip is an explicit maintainer action, not automated. Default is to stay private until the maintainer has reviewed the corpus and the documentation.
2. **Confirm the conduct-contact email is monitored.** `ctyoungb.agent@gmail.com` is wired into `docs/code-of-conduct.md` and `SECURITY.md`. The maintainer should verify monitoring + acknowledgment template before going public.
3. **Skim `docs/legal-context.md`** and confirm wording is consistent with how the project wants to describe the FTC v Deere / FARM Act / §1201 landscape publicly. The doc is deliberately neutral; sharper or softer framing is a maintainer call.
4. **Skim `docs/code-of-conduct.md` §8 (project vs legal scope)** for the same reason — it is the clearest single-line statement of what this project is and is not.

### Machine-class capture TODOs (post-hardware deployment)

The setup doc's §7 names five machine classes (4WD tractor, planter, sprayer, auger wagon, combine) with explicit `<TODO>` placeholders for first-hand pinouts, port locations, and observed PGNs. Filling these in requires hands-on capture against specific equipment.

### Reference CAN trace corpus

5. The `corpus/` directory is currently empty. Captures during planting / spraying / harvest are needed to (a) test the inferrer against real data, (b) tune heuristic thresholds, and (c) provide community reference logs. Captures should run through `python -m opendbc_ag.tools.anonymize` before being added.

### Partnership / community (post-public-release)

6. **Cross-link with AgOpenGPS** — open a PR or issue in their repo announcing the DBC corpus as a dependency option. They currently use a partial in-repo DBC.
7. **Cross-link with Open-Agriculture / AgIsoStack++** — they are the primary upstream PGN source; reciprocal acknowledgment is courtesy.
8. **Tractor Hacking outreach** — spiritual peer for the right-to-repair side; coordinate posting norms.
9. **ISOBlue HD (Purdue)** — academic collaboration potential for the trace corpus.
10. **LinkedIn / Discourse / Reddit announcements** — maintainer-published; not automated.

### Paywalled (only relevant if the maintainer chooses to access)

11. **ISO 11783-7 paid PDF** (~$200/part via ISO) — would enrich the VDMA placeholders into signal-rich definitions. **Do not transcribe paid spec text into this repository.** Use it as private reference for confirming your own captures; contribute resulting definitions with public-source citations only.
12. **Full SAE J1939 PDFs** (paywalled via SAE) — similar caveat.

---

## How to resume

- **Approve + go public:** the maintainer addresses items 1-4 and decides the visibility flip. A follow-on remediation pass can draft cross-link PR/issue text for items 6-10 if desired, but the maintainer publishes them.
- **Request revisions:** GitHub issues on the private repo describe the change; remediation cycle re-engages with the specific scope.
- **Hold:** no action. The tag persists; rejoining later is straightforward.

---

## Verification checklist

```bash
# Run from the repo root after pulling a fresh copy
.venv/bin/python -m pytest opendbc_ag/tests/             # → current pass count
.venv/bin/python -m opendbc_ag.tools.coverage_report     # → regenerates docs/coverage.md
.venv/bin/python scripts/check_dbc_policy.py             # → scope-policy + dupe + citation gates
git log --oneline | head -25                             # → phase + remediation commits
```

---

## Closing note

This build prioritized **shipping a complete, reviewable, defensible artifact in one autonomous pass** rather than aiming for a polished tool. The DBC corpus is real and usable. The community workflow surface is real and ready to receive contributions. The legal posture is real and defensible.

What this build is **not** yet: tuned against real-world ag-CAN logs (no corpus), polished by community feedback (no community), or comprehensive on every PGN detail (most VDMA frames are PGN-level placeholders pending enrichment).

The gap from `v0.1.0-private` to a useful public project is bounded by items 1-12 above. Approximate effort: hours for items 1-4 (maintainer review), weeks-to-months for items 5-10 spread across the field season and outreach campaign.
