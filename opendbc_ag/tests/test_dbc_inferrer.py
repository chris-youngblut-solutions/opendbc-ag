"""Test dbc_inferrer against the deterministic synthetic CAN fixture.

Ground truth is defined in `fixtures/generate_synthetic_can.py`:
- 0x100 @ 100 ms: byte 0 const FF, byte 1 bit 0 boolean, bytes 2-3 u16 ramp, bytes 4-7 const
- 0x200 @ 1000 ms: byte 0 const 00, bytes 1-7 const FF
- 0x300 @  50 ms: byte 0 sinusoidal u8, bytes 1-7 const 00
"""
from __future__ import annotations

from pathlib import Path

import pytest

from opendbc_ag.tools import dbc_inferrer

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_can.csv"


@pytest.fixture(scope="module")
def analyses():
    records = dbc_inferrer.load_csv(FIXTURE)
    return dbc_inferrer.analyze(records)


def test_three_can_ids_detected(analyses):
    assert set(analyses) == {0x100, 0x200, 0x300}


def test_cycle_time_0x100(analyses):
    assert abs(analyses[0x100].cycle_time_ms - 100.0) < 5.0


def test_cycle_time_0x200(analyses):
    assert abs(analyses[0x200].cycle_time_ms - 1000.0) < 50.0


def test_cycle_time_0x300(analyses):
    assert abs(analyses[0x300].cycle_time_ms - 50.0) < 5.0


def test_constant_bytes_0x100(analyses):
    a = analyses[0x100]
    assert 0 in a.constant_bytes
    for i in (4, 5, 6, 7):
        assert i in a.constant_bytes
    # Bytes 2 and 3 carry the 16-bit ramp — both must vary
    assert 2 not in a.constant_bytes
    assert 3 not in a.constant_bytes


def test_constant_bytes_0x200(analyses):
    a = analyses[0x200]
    assert set(a.constant_bytes) == set(range(8))


def test_boolean_detected_0x100_byte1(analyses):
    a = analyses[0x100]
    bool_signals = [s for s in a.candidate_signals if s.start_bit == 8 and s.size == 1]
    assert len(bool_signals) == 1
    assert bool_signals[0].confidence >= 0.8


def test_multibyte_aggregate_0x100_bytes_2_3(analyses):
    a = analyses[0x100]
    u16 = [s for s in a.candidate_signals if s.start_bit == 16 and s.size == 16]
    assert len(u16) == 1
    assert u16[0].max_value > u16[0].min_value


def test_single_byte_signal_0x300(analyses):
    a = analyses[0x300]
    u8 = [s for s in a.candidate_signals if s.start_bit == 0 and s.size == 8]
    assert len(u8) == 1
    assert u8[0].max_value > u8[0].min_value + 50


def test_report_renders(analyses):
    report = dbc_inferrer.render_report(analyses)
    assert "CAN ID 0x100" in report
    assert "CAN ID 0x200" in report
    assert "CAN ID 0x300" in report
    assert "candidate signals" in report


def test_cycle_stats_populated(analyses):
    """R4: each analysis carries mode + stddev + p10 + p90 cycle stats."""
    for cid, a in analyses.items():
        assert a.cycle_stats is not None
        assert a.cycle_stats.mode_ms > 0
        assert a.cycle_stats.stddev_ms >= 0
        assert a.cycle_stats.p10_ms <= a.cycle_stats.p90_ms


def test_dbc_emission_format():
    """R4: --format dbc produces parseable DBC output."""
    import tempfile
    from canmatrix import formats

    records = dbc_inferrer.load_csv(FIXTURE)
    analyses = dbc_inferrer.analyze(records)
    dbc_text = dbc_inferrer.render_dbc(analyses)
    assert "BO_ " in dbc_text
    assert "SG_ " in dbc_text

    # Round-trip via canmatrix to confirm it parses
    with tempfile.NamedTemporaryFile(suffix=".dbc", mode="w", delete=False) as tf:
        tf.write(dbc_text)
        tmp = tf.name
    try:
        m = formats.loadp(tmp)
        mat = list(m.values())[0]
        assert len(mat.frames) >= 1
    finally:
        import os
        os.unlink(tmp)


@pytest.mark.xfail(reason="known limitation: outlier byte (cardinality=2) misclassified as boolean toggle")
def test_outlier_byte_not_misclassified_as_boolean():
    """Synthetic byte that's mostly-constant 0x00 with one 0xFF sample.

    Cardinality is 2, so current heuristic enters the boolean branch and reports
    a 1-bit signal. The correct call is "mostly-constant with outlier" — needs
    a separate detector that thresholds on transition frequency, not cardinality.
    """
    import csv as _csv
    from pathlib import Path as _P
    import tempfile

    rows = []
    for i in range(200):
        payload = bytes([0x00] * 8)
        if i == 100:
            payload = bytes([0xFF] + [0x00] * 7)
        rows.append((i * 0.1, 0x999, payload.hex().upper()))

    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as tf:
        w = _csv.writer(tf)
        w.writerow(["timestamp", "can_id", "data_hex"])
        for r in rows:
            w.writerow([f"{r[0]:.4f}", r[1], r[2]])
        path = tf.name

    try:
        records = dbc_inferrer.load_csv(_P(path))
        analyses = dbc_inferrer.analyze(records)
        a = analyses[0x999]
        bool_signals = [s for s in a.candidate_signals if s.size == 1]
        # We *want* this to be empty (the outlier should not look like a Bool)
        assert not bool_signals
    finally:
        import os
        os.unlink(path)


@pytest.mark.xfail(reason="known limitation: signed signals reported as unsigned with discontinuous range")
def test_signed_signal_crossing_0x80():
    """A signal that crosses the 0x80 sign boundary should be flagged as possibly signed."""
    import csv as _csv
    from pathlib import Path as _P
    import tempfile

    rows = []
    for i in range(200):
        # Triangle wave 0x70 → 0x90 → 0x70 (signed -16 to +16)
        v = 0x70 + (i % 32 if (i // 32) % 2 == 0 else 32 - (i % 32))
        rows.append((i * 0.1, 0xAAA, bytes([v & 0xFF] + [0x00] * 7).hex().upper()))

    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as tf:
        w = _csv.writer(tf)
        w.writerow(["timestamp", "can_id", "data_hex"])
        for r in rows:
            w.writerow([f"{r[0]:.4f}", r[1], r[2]])
        path = tf.name

    try:
        records = dbc_inferrer.load_csv(_P(path))
        analyses = dbc_inferrer.analyze(records)
        a = analyses[0xAAA]
        # We *want* the signed candidacy noted in the rationale.
        assert any("signed" in s.rationale.lower() for s in a.candidate_signals)
    finally:
        import os
        os.unlink(path)
