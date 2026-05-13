# Ralph-loop autonomous build report

**Project:** opendbc-ag
**Tag:** `v0.1.0-private`
**Date:** 2026-05-13
**Mode:** private-first; manual review required before public release
**Acceptance:** all 8 PRD acceptance criteria met — see `CHANGELOG.md` Phase 12 section

This report enumerates what the Ralph loop shipped, what it intentionally deferred, and the punch list of user-owned follow-ups before public release.

---

## What shipped

12 phases executed sequentially. Each phase has its own commit on `main`; the full chain is visible via `git log --oneline`.

| Phase | Deliverable | Lines |
|---|---|---|
| 0 | Repo + scaffold (LICENSE/README/CHANGELOG/.gitignore) | ~100 |
| 1 | Directory tree + per-dir READMEs | ~50 |
| 2 | AgIsoStack++ PGN extractor + DBC (46 PGNs, 84 signals) | ~600 |
| 3 | isobus.net VDMA scraper + DBC (2,892 PGNs) | ~400 |
| 4 | J1939 ag-subset (17 PGNs, 69 signals) | ~500 |
| 5 | CI workflows (3) + pyproject.toml + initial tests | ~250 |
| 6 | README + CHANGELOG finalization | ~70 |
| 7 | CoC + CONTRIBUTING + PR/issue templates + naming guide | ~420 |
| 8 | cabana-for-ag setup doc (generic + 5 fleet TODOs) | ~300 |
| 9 | dbc_inferrer + anonymize + synthetic fixtures + 17 tests | ~940 |
| 10 | Signal-naming test harness (6 tests) | ~90 |
| 11 | Legal-context + FAQ + architecture + README link pass | ~290 |
| 12 | CHANGELOG final entry + this report + tag + pre-release | ~150 |

**Corpus at ship time:**
- 2,955 unique PGN IDs
- 3,045 signals
- 3 DBC files
- 0 proprietary-range PGNs
- 0 cross-DBC duplicate PGN IDs
- 29/29 tests passing
- 3/3 CI workflows green

---

## Deviations from the PRD

These are not bugs; they are intentional choices made during execution with stated reasons. Listed for transparency so the reviewer can sanity-check the trade.

| # | Deviation | Reason |
|---|---|---|
| 1 | **Code of conduct adopted by link** rather than CC 2.1 verbatim text in the file | The verbatim text routinely triggers content-policy classifiers on output. Linking to the canonical upstream preserves the recognized adoption (CC 2.1) and matches how Apache, Linux, Kubernetes, and others handle CoC. The project-specific addendum addresses the gaps the upstream Covenant intentionally leaves to each project. |
| 2 | **Test files consolidated** — Phase 10 PRD called for separate `test_dbc_syntax.py` / `test_consistency.py` / `test_signal_naming.py`. Shipped as: existing `test_smoke.py` (covers syntax + consistency) + new `test_signal_naming.py`. | The syntax + consistency tests already shipped in Phase 5 as part of `test_smoke.py`. Splitting them into three files just to match PRD's literal text would have been churn with no behavioral change. |
| 3 | **Signal-name length limit lifted 32 → 64** chars in the naming guide | Initial 32-char cap was too tight: VDMA placeholders auto-generate names like `ExtendedTransportProtocolConnectionManagement_RawPayload` (56 chars). 64 matches the frame-name limit and DBC-tooling practical limits. |
| 4 | **`mkdir`/`extractions/` raw clone gitignored** but extraction JSONs kept (per user direction: "keep extractions") | Raw AgIsoStack++ clone is 26 MB and reproducible from upstream; extraction JSON is the value-added intermediate. |

---

## User-owned follow-ups (deferred from autonomous loop)

These items require either human input, paywalled access, hardware not yet deployed, or external communication. None of them block private review — they unlock on user trigger after review passes.

### Hot path (blocks public release)

1. **Decide whether to go public.** Default: stay private. Trigger: user reads the corpus and the docs, decides scope/quality is acceptable, then runs `gh repo edit in-loop/opendbc-ag --visibility public --accept-visibility-change-consequences`.
2. **Set canonical conduct-contact mailing setup.** `ctyoung.agent@gmail.com` is wired into `docs/code-of-conduct.md`. Verify the address is monitored and has an auto-acknowledgment template before going public.
3. **Skim `docs/legal-context.md`** and confirm wording is consistent with how you want to describe the FTC v Deere / FARM Act / §1201 landscape publicly. The doc is deliberately neutral; if your view is more pointed (or more conservative), this is the place to tune.
4. **Skim `docs/code-of-conduct.md` §8 (project vs legal scope)** for the same reason — it is the clearest single-line statement of what this project is and is not.

### Fleet-specific TODOs (post-Stub-R hardware deployment)

5. **JD 9R-series tractor (cab CAN tap)** — `docs/cabana-for-ag-setup.md` §7a — fill in connector ID, port location, photo, harness annotation.
6. **Kinze 3700 planter (ISOBUS connector location)** — §7b — fill in physical location, mating connector PN, terminator location, working-set master behavior.
7. **Hagie STS Raven controller (CAN-FD bus access)** — §7c — fill in physical access point, bitrate, isolation from main ISOBUS, observed boom-section PGNs.
8. **Brent V-Series TRAX auger wagon** — §7d — fill in CAN access point, bitrate, weight-sensor PGNs, hydraulic command PGNs.
9. **JD S/X combine ISOBUS port** — §7e — fill in connector location, header-bus tap, header-class PGNs, separator drive PGNs.

### Capture corpus (post-Stub-R, during field operations)

10. **Reference CAN trace corpus.** `corpus/` directory is currently empty. Captures from planting/spraying/harvest are needed to (a) test the inferrer against real data, (b) tune the heuristic thresholds, and (c) provide community reference logs. Run captures through `python -m opendbc_ag.tools.anonymize` before adding.

### Partnership / community (post-public-release)

11. **Cross-link with AgOpenGPS** — open a PR or issue in their repo announcing the DBC corpus as a dependency option. They currently use a partial in-repo DBC; offering the canonical baseline is the value prop.
12. **Cross-link with Open-Agriculture / AgIsoStack++** — they are the primary upstream PGN source. A reciprocal acknowledgment is courtesy.
13. **Tractor Hacking outreach** — they are the spiritual peer for the right-to-repair side. Coordinate posting norms before going loud.
14. **ISOBlue HD (Purdue)** — academic collaboration potential for the trace corpus (item 10). Their data-collection model is more research-rigorous; sync with whoever runs the project before assuming a corpus exchange.
15. **LinkedIn / Discourse / Reddit announcements** — user-published from user's account; not automated. Draft text not pre-staged in the repo — the launch frame is partly determined by the timing of items 1-9.

### Paywalled (only relevant if you ever decide to access)

16. **ISO 11783-7 paid PDF** (~$200/part via ISO) — would enrich the iso11783_from_vdma.dbc placeholders into signal-rich definitions. **Do not transcribe paid spec text into this repository.** Use it as private reference for confirming your own captures; contribute resulting definitions with public-source citations only.
17. **Full SAE J1939 PDFs** (paywalled via SAE) — similar caveat.

---

## How to resume the loop

The Ralph loop **halts at this report.** To resume:

- **Approve + go public:** address items 1-4, then user-publishes the repo and the announcements. A follow-on Ralph mini-loop can draft cross-link PR/issue text for items 11-15 if requested, but the user publishes them.
- **Request revisions:** leave GitHub issue comments on the private repo, or describe the change in conversation. Ralph re-engages with the specific scope.
- **Hold:** no action. The tag persists; rejoining later is straightforward.

---

## Verification checklist (run before review)

```bash
# In the repo root
.venv/bin/python -m pytest opendbc_ag/tests/         # → 29 passed
.venv/bin/python -m opendbc_ag.tools.coverage_report  # → 2955 PGNs / 3045 signals
gh repo view in-loop/opendbc-ag --json visibility -q .visibility  # → "PRIVATE"
gh release view v0.1.0-private                       # → release exists
git log --oneline | head -15                         # → 12 phase commits
```

---

## Closing note

This loop optimized for **shipping a complete, reviewable, defensible artifact in one autonomous pass** — not for being the perfect tool. The DBC corpus is real and usable today. The community workflow surface is real and ready to receive contributions. The legal posture is real and defensible.

What it is **not** yet: tuned against real-world ag-CAN logs (no corpus), polished by community feedback (no community), or comprehensive on every PGN-detail (most VDMA frames are placeholders pending enrichment).

The gap from `v0.1.0-private` to a useful public project is bounded by items 1-15 in the punch list above. Approximate effort estimate: hours for items 1-4, weeks-to-months for items 5-15 spread across the field season and outreach campaign.

— Ralph
