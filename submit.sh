#!/bin/bash
# Submit wrapper for CSC 391/691.
#
# The point of this file is that account, partition, and reservation flags
# live in exactly one place. HW2 reuses it to launch thirty jobs, so it needs
# to be something you would run again next week without editing.
#
#   ./submit.sh cpu jobs/partB_array.slurm
#   ./submit.sh gpu jobs/partD_gpu.slurm
#   ./submit.sh cpu jobs/partC_two_nodes.slurm --nodes=4
#
# Anything after the script path is passed through to sbatch, which lets a
# sweep vary node count without editing the job file.

set -euo pipefail
cd "$(dirname "$0")"
source deac/site.sh

KIND="${1:-}"
SCRIPT="${2:-}"
shift 2 || true

if [ -z "$KIND" ] || [ -z "$SCRIPT" ]; then
  echo "usage: $0 <cpu|gpu> <job script> [extra sbatch flags]" >&2
  exit 2
fi

# TODO 1. Build the sbatch flag list. deac_sbatch_args in deac/site.sh already
#         assembles account, partition, and gres for the requested kind.
# TODO 2. Submit with --parsable so that the job id is the only thing on
#         stdout, and record it. A job id you did not save is a measurement
#         you cannot reconstruct.
# TODO 3. Append the job id, the script name, the extra flags, and a UTC
#         timestamp to results/jobs.log. HW2 asks for job identifiers in the
#         submission and this is where they come from.

echo "submit.sh is not finished, see the TODOs" >&2
exit 1
