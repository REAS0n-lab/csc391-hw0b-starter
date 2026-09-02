#!/bin/bash
# Part A, job 1. Requests 8 cores and configures the code to use 1.
#SBATCH --job-name=hw0b-A-over
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=00:30:00
#SBATCH --output=results/%x-%j.out
#SBATCH --error=results/%x-%j.err

set -uo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"; mkdir -p results
source deac/site.sh; deac_load_cpu

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

hostname
echo "requested cpus-per-task ${SLURM_CPUS_PER_TASK:-unset}, using $OMP_NUM_THREADS"
python3 matmul_bench.py -n 4000 --json results/hw0b_partA.jsonl
