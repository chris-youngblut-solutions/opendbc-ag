"""Smoke test for the coverage report generator."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_coverage_report_runs_and_writes(tmp_path: Path) -> None:
    # Run with the real DBC corpus but redirect output to a tmp dir.
    # We do this by copying just the dbc/ tree and pointing --repo-root at it.
    target = tmp_path / "fake_repo"
    (target / "opendbc_ag/dbc").mkdir(parents=True)
    for dbc in (REPO_ROOT / "opendbc_ag/dbc").glob("*.dbc"):
        (target / "opendbc_ag/dbc" / dbc.name).write_bytes(dbc.read_bytes())

    result = subprocess.run(
        [sys.executable, "-m", "opendbc_ag.tools.coverage_report", "--repo-root", str(target)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"coverage_report failed: {result.stderr}"

    out_file = target / "docs" / "coverage.md"
    assert out_file.exists()
    text = out_file.read_text()
    assert "Coverage matrix" in text
    assert "Total unique PGN IDs" in text
    assert "Per-DBC breakdown" in text
    assert "Source attribution" in text
