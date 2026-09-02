"""Structural checks on the job scripts. No cluster required."""

import glob
import os
import re

JOBS = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "jobs", "*.slurm")))


def read(path):
    with open(path) as fh:
        return fh.read()


def test_jobs_exist():
    assert len(JOBS) >= 6


def test_every_job_sources_site_config():
    for path in JOBS:
        assert "source deac/site.sh" in read(path), os.path.basename(path)


def test_every_job_writes_into_results():
    for path in JOBS:
        text = read(path)
        assert "--output=results/" in text, os.path.basename(path)
        assert "--error=results/" in text, os.path.basename(path)


def test_no_hardcoded_account_or_partition():
    # Account and partition come from deac/site.sh through submit.sh so that
    # one edit reaches every job.
    for path in JOBS:
        text = read(path)
        assert not re.search(r"^#SBATCH\s+--account=", text, re.M), os.path.basename(path)
        assert not re.search(r"^#SBATCH\s+--partition=", text, re.M), os.path.basename(path)


def test_part_c_requests_two_nodes_one_task_each():
    text = read([p for p in JOBS if "partC" in p][0])
    assert "--nodes=2" in text
    assert "--ntasks-per-node=1" in text


def test_part_a_pair_differs_only_in_cpus_per_task():
    over = read([p for p in JOBS if "partA_overrequest" in p][0])
    matched = read([p for p in JOBS if "partA_matched" in p][0])
    assert "--cpus-per-task=8" in over
    assert "--cpus-per-task=1" in matched
    assert "OMP_NUM_THREADS=1" in over and "OMP_NUM_THREADS=1" in matched
