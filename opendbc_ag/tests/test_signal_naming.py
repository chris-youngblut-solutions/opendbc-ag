"""Validate frame and signal names against `docs/signal-naming-guide.md`.

Rules enforced:
- Frame names: max 64 characters, no whitespace, must start with a letter
  or a known prefix (`J1939_`, `VDMA_`).
- Signal names: max 64 characters, no whitespace, must start with a letter
  or a known prefix.
- Signal names use no characters outside `[A-Za-z0-9_]` (DBC identifier safety).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
from canmatrix import formats

REPO_ROOT = Path(__file__).resolve().parents[2]
DBC_DIR = REPO_ROOT / "opendbc_ag/dbc"

_DBC_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MAX_FRAME_NAME = 64
MAX_SIGNAL_NAME = 64


def _all_frames():
    for dbc_path in sorted(DBC_DIR.glob("*.dbc")):
        m = formats.loadp(str(dbc_path))
        mat = list(m.values())[0]
        for frame in mat.frames:
            yield dbc_path.name, frame


def test_frame_names_are_dbc_identifiers():
    bad = []
    for dbc_name, frame in _all_frames():
        if not _DBC_IDENTIFIER.match(frame.name):
            bad.append(f"{dbc_name}::{frame.name}")
    assert not bad, f"frame names violate DBC identifier syntax: {bad[:10]}"


def test_frame_names_under_max_length():
    bad = []
    for dbc_name, frame in _all_frames():
        if len(frame.name) > MAX_FRAME_NAME:
            bad.append(f"{dbc_name}::{frame.name} ({len(frame.name)} chars)")
    assert not bad, f"frame names over {MAX_FRAME_NAME} chars: {bad[:10]}"


def test_signal_names_are_dbc_identifiers():
    bad = []
    for dbc_name, frame in _all_frames():
        for sig in frame.signals:
            if not _DBC_IDENTIFIER.match(sig.name):
                bad.append(f"{dbc_name}::{frame.name}::{sig.name}")
    assert not bad, f"signal names violate DBC identifier syntax: {bad[:10]}"


def test_signal_names_under_max_length():
    bad = []
    for dbc_name, frame in _all_frames():
        for sig in frame.signals:
            if len(sig.name) > MAX_SIGNAL_NAME:
                bad.append(f"{dbc_name}::{frame.name}::{sig.name} ({len(sig.name)} chars)")
    assert not bad, f"signal names over {MAX_SIGNAL_NAME} chars: {bad[:10]}"


def test_vdma_frames_use_vdma_prefix():
    """All frames in iso11783_from_vdma.dbc should carry the VDMA_ prefix."""
    dbc_path = DBC_DIR / "iso11783_from_vdma.dbc"
    if not dbc_path.exists():
        pytest.skip("VDMA DBC not present")
    m = formats.loadp(str(dbc_path))
    mat = list(m.values())[0]
    non_prefixed = [f.name for f in mat.frames if not f.name.startswith("VDMA_")]
    assert not non_prefixed, f"VDMA DBC frames missing VDMA_ prefix: {non_prefixed[:10]}"


def test_j1939_frames_use_j1939_prefix():
    """All frames in j1939_ag_subset.dbc should carry the J1939_ prefix."""
    dbc_path = DBC_DIR / "j1939_ag_subset.dbc"
    if not dbc_path.exists():
        pytest.skip("J1939 DBC not present")
    m = formats.loadp(str(dbc_path))
    mat = list(m.values())[0]
    non_prefixed = [f.name for f in mat.frames if not f.name.startswith("J1939_")]
    assert not non_prefixed, f"J1939 DBC frames missing J1939_ prefix: {non_prefixed[:10]}"
