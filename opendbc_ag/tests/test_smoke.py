"""Smoke tests — verify the DBC corpus parses and policy invariants hold."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pytest
from canmatrix import formats


REPO_ROOT = Path(__file__).resolve().parents[2]
DBC_DIR = REPO_ROOT / "opendbc_ag/dbc"


def _dbc_files() -> list[Path]:
    return sorted(DBC_DIR.glob("*.dbc"))


@pytest.mark.parametrize("dbc_path", _dbc_files(), ids=lambda p: p.name)
def test_dbc_parses(dbc_path: Path) -> None:
    m = formats.loadp(str(dbc_path))
    matrices = list(m.values())
    assert len(matrices) == 1, f"expected single matrix in {dbc_path.name}"
    mat = matrices[0]
    assert len(mat.frames) > 0, f"{dbc_path.name} contains zero frames"
    for frame in mat.frames:
        assert len(frame.signals) >= 1, f"{dbc_path.name} :: {frame.name} has no signals"


def test_no_proprietary_pgns() -> None:
    """Pure-standard scope: reject PGNs in 0xEF00 or 0xFF00..0xFFFF."""
    violations = []
    for dbc_path in _dbc_files():
        m = formats.loadp(str(dbc_path))
        mat = list(m.values())[0]
        for frame in mat.frames:
            pgn = frame.arbitration_id.id
            if pgn == 0xEF00 or 0xFF00 <= pgn <= 0xFFFF:
                violations.append(f"{dbc_path.name}: {frame.name} (PGN 0x{pgn:X})")
    assert not violations, f"proprietary-range PGNs found: {violations}"


def test_no_cross_dbc_duplicates() -> None:
    """No PGN ID appears in more than one DBC (de-dup policy)."""
    seen = defaultdict(list)
    for dbc_path in _dbc_files():
        m = formats.loadp(str(dbc_path))
        mat = list(m.values())[0]
        for frame in mat.frames:
            seen[frame.arbitration_id.id].append((dbc_path.name, frame.name))
    dupes = {pgn: locs for pgn, locs in seen.items() if len(locs) > 1}
    assert not dupes, f"duplicate PGN IDs across DBC files: {dupes}"


def test_corpus_size() -> None:
    """Sanity floor: must have at least 80 PGNs total (PRD acceptance criterion)."""
    total = 0
    for dbc_path in _dbc_files():
        m = formats.loadp(str(dbc_path))
        mat = list(m.values())[0]
        total += len(mat.frames)
    assert total >= 80, f"corpus has only {total} PGNs (PRD requires >=80)"
