"""Tests for the log-anonymization tool."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from opendbc_ag.tools import anonymize


def test_quantize_gps_snaps_to_1km_grid():
    # Chicago Loop ≈ 41.8781°, -87.6298°
    qlat, qlon = anonymize.quantize_gps(41.8781, -87.6298)
    # Within half a grid cell of the input
    assert abs(qlat - 41.8781) < anonymize.GRID_DEGREES
    assert abs(qlon - (-87.6298)) < anonymize.GRID_DEGREES
    # And on the grid itself
    assert abs((qlat / anonymize.GRID_DEGREES) - round(qlat / anonymize.GRID_DEGREES)) < 1e-9


def test_quantize_gps_collapses_neighbors():
    # Two points within ~100 m of each other should snap to the same grid cell.
    a = anonymize.quantize_gps(41.87810, -87.62980)
    b = anonymize.quantize_gps(41.87815, -87.62985)
    assert a == b


def test_truncate_timestamp_to_date_drops_time_of_day():
    # 2024-06-15 14:30:45 UTC
    ts = 1718461845.0
    truncated = anonymize.truncate_timestamp_to_date(ts)
    # Should be midnight UTC of 2024-06-15
    from datetime import datetime, timezone
    dt = datetime.fromtimestamp(truncated, tz=timezone.utc)
    assert dt.year == 2024
    assert dt.month == 6
    assert dt.day == 15
    assert dt.hour == 0
    assert dt.minute == 0
    assert dt.second == 0


def test_strip_source_address_zeros_low_byte():
    # 29-bit ID: priority=6, PGN=0xFEF1, SA=0x42 → 0x18FEF142
    cid = 0x18FEF142
    stripped = anonymize.strip_source_address_j1939(cid)
    assert stripped & 0xFF == 0xFE  # NULL address per J1939-81
    assert (stripped >> 8) == (cid >> 8)  # priority + PGN preserved


def test_anonymize_payload_bytes_zeros_slice():
    data = bytes.fromhex("FFEEDDCCBBAA9988")
    out = anonymize.anonymize_payload_bytes(data, slice(2, 6))
    assert out.hex().upper() == "FFEE000000009988"


def test_anonymize_log_csv_writes_all_rows(tmp_path: Path):
    in_path = tmp_path / "in.csv"
    out_path = tmp_path / "out.csv"

    with in_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "can_id", "data_hex"])
        # Epoch timestamps so the date-quantization kicks in
        w.writerow(["1718461845.0", "0x18FEF142", "0102030405060708"])
        w.writerow(["1718461845.1", "0x18FEF142", "0102030405060708"])

    n = anonymize.anonymize_log_csv(in_path, out_path)
    assert n == 2

    with out_path.open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    for row in rows:
        cid = int(row["can_id"])
        assert cid & 0xFF == 0xFE  # SA stripped
