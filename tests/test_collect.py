"""Specification for the two functions you write in scripts/collect.py.

Run with  python3 -m pytest tests -q
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from collect import load_jsonl, mean, stdev, summarize, to_markdown  # noqa: E402

RECORDS = [
    {"n": 1000, "dtype": "float64", "seconds": 0.10, "gflops": 20.0},
    {"n": 1000, "dtype": "float64", "seconds": 0.12, "gflops": 16.7},
    {"n": 1000, "dtype": "float64", "seconds": 0.14, "gflops": 14.3},
    {"n": 2000, "dtype": "float64", "seconds": 0.80, "gflops": 20.0},
    {"n": 2000, "dtype": "float64", "seconds": 0.90, "gflops": 17.8},
]


def test_load_jsonl_round_trip(tmp_path):
    path = tmp_path / "r.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in RECORDS) + "\n")
    assert load_jsonl([str(path)]) == RECORDS


def test_load_jsonl_skips_blank_and_bad_lines(tmp_path):
    path = tmp_path / "r.jsonl"
    path.write_text('{"n": 1}\n\nnot json\n{"n": 2}\n')
    assert load_jsonl([str(path)]) == [{"n": 1}, {"n": 2}]


def test_stdev_of_one_observation_is_zero():
    assert stdev([1.0]) == 0.0


def test_summarize_groups_and_counts():
    rows = summarize(RECORDS, ("n",), "seconds")
    assert [r["n"] for r in rows] == [1000, 2000]
    assert [r["runs"] for r in rows] == [3, 2]


def test_summarize_statistics():
    rows = summarize(RECORDS, ("n",), "seconds")
    first = rows[0]
    assert first["mean"] == pytest.approx(0.12)
    assert first["min"] == pytest.approx(0.10)
    assert first["max"] == pytest.approx(0.14)
    assert first["stdev"] == pytest.approx(stdev([0.10, 0.12, 0.14]))


def test_summarize_multiple_group_keys():
    rows = summarize(RECORDS, ("n", "dtype"), "seconds")
    assert len(rows) == 2
    assert rows[0]["dtype"] == "float64"


def test_summarize_can_summarize_another_column():
    rows = summarize(RECORDS, ("n",), "gflops")
    assert rows[0]["mean"] == pytest.approx(mean([20.0, 16.7, 14.3]))


def test_to_markdown_shape():
    rows = summarize(RECORDS, ("n",), "seconds")
    table = to_markdown(rows)
    lines = [line for line in table.strip().splitlines() if line.strip()]
    assert len(lines) == len(rows) + 2
    assert lines[0].startswith("|") and lines[0].endswith("|")
    assert set(lines[1].replace("|", "").replace(" ", "")) <= set("-:")
    assert "n" in lines[0] and "runs" in lines[0]
