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
