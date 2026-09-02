#!/usr/bin/env python3
"""Collect benchmark records into one table.

Reading five output files by eye and retyping the numbers is a process that
does not survive being run thirty times, which is roughly what HW2 needs. This
script is the thing that survives.

Two functions are left for you to write. `summarize` reduces the raw records
to one row per configuration, and `to_markdown` renders those rows. The tests
in tests/test_collect.py define what they must do.

    python3 scripts/collect.py results/hw0b_partB.jsonl
    python3 scripts/collect.py results/*.jsonl --group n dtype
"""

import argparse
import glob
import json
import math
import sys


def load_jsonl(paths):
    """Read one or more JSON Lines files into a list of dicts."""
    records = []
    for pattern in paths:
        matched = sorted(glob.glob(pattern)) or [pattern]
        for path in matched:
            with open(path) as fh:
                for line_no, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        print(f"{path}:{line_no} skipped, {exc}", file=sys.stderr)
    return records


def mean(xs):
    return sum(xs) / len(xs)


def stdev(xs):
    """Sample standard deviation. Returns 0.0 for a single observation."""
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def summarize(records, group_keys=("n",), value_key="seconds"):
    """Reduce records to one row per unique combination of group_keys.

    Return a list of dicts sorted by the group key values. Each row holds

        the group key values themselves
        runs        number of records in the group
        mean        mean of value_key
        stdev       sample standard deviation of value_key
        min         smallest value_key in the group
        max         largest value_key in the group

    TODO. Write this. tests/test_collect.py is the specification.

    A group with one run has a standard deviation of zero. Reporting that as
    though it were measured variability is one of the defects this course
    spends the semester on, so `runs` belongs in the output next to it.
    """
    raise NotImplementedError("summarize is yours to write, see tests/test_collect.py")


def to_markdown(rows, columns=None):
    """Render summary rows as a GitHub flavored Markdown table.

    The first line is the header, the second is the separator, and one line
    follows per row. Floats are formatted to six significant figures.

    TODO. Write this. tests/test_collect.py is the specification.
    """
    raise NotImplementedError("to_markdown is yours to write, see tests/test_collect.py")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("paths", nargs="+", help="JSON Lines files, globs allowed")
    p.add_argument("--group", nargs="+", default=["n"],
                   help="keys to group by (default n)")
    p.add_argument("--value", default="seconds", help="key to summarize")
    p.add_argument("--out", default=None, help="write the table here")
    args = p.parse_args(argv)

    records = load_jsonl(args.paths)
    if not records:
        print("no records found", file=sys.stderr)
        return 1
    print(f"loaded {len(records)} records", file=sys.stderr)

    rows = summarize(records, tuple(args.group), args.value)
    table = to_markdown(rows)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(table + "\n")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
