"""Generates the deterministic synthetic CAN log fixture used by test_dbc_inferrer.

The fixture seeds known signal patterns so the inferrer can be tested
against ground truth. Re-run after editing to regenerate `synthetic_can.csv`.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

OUT_PATH = Path(__file__).with_name("synthetic_can.csv")

# Ground-truth seeded patterns. Test cases pin against this dict.
GROUND_TRUTH = {
    0x100: {
        "cycle_ms": 100,
        "byte_0": "constant_0xFF",
        "byte_1_bit_0": "boolean_toggle",
        "bytes_2_3": "u16_ramp_counter_le",
        "bytes_4_7": "constant_0xFF",
    },
    0x200: {
        "cycle_ms": 1000,
        "byte_0": "constant_0x00",
        "bytes_1_7": "constant_0xFF",
    },
    0x300: {
        "cycle_ms": 50,
        "byte_0": "sinusoidal_u8",
        "bytes_1_7": "constant_0x00",
    },
}

DURATION_S = 10.0


def gen_rows():
    """Emit (timestamp, can_id, data_hex_8byte) tuples in time order."""
    rows = []
    for can_id, spec in GROUND_TRUTH.items():
        period = spec["cycle_ms"] / 1000.0
        n = int(DURATION_S / period)
        for i in range(n):
            t = i * period
            payload = bytearray(8)

            if can_id == 0x100:
                payload[0] = 0xFF
                payload[1] = 0x01 if (i % 2) else 0x00
                ramp = (i * 100) & 0xFFFF  # max 9900 = 0x26AC → both bytes vary
                payload[2] = ramp & 0xFF
                payload[3] = (ramp >> 8) & 0xFF
                payload[4:8] = b"\xFF\xFF\xFF\xFF"
            elif can_id == 0x200:
                payload[0] = 0x00
                payload[1:8] = b"\xFF" * 7
            elif can_id == 0x300:
                payload[0] = int(127 + 127 * math.sin(2 * math.pi * i / 40)) & 0xFF
                payload[1:8] = b"\x00" * 7

            rows.append((t, can_id, payload.hex().upper()))
    rows.sort(key=lambda r: r[0])
    return rows


def main():
    rows = gen_rows()
    with OUT_PATH.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "can_id", "data_hex"])
        for t, cid, data in rows:
            w.writerow([f"{t:.4f}", cid, data])
    print(f"Wrote {len(rows)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
