#!/bin/bash
# Part B. One array submission sweeps five problem sizes.
#
# Submit with
#   sbatch $(source deac/site.sh; deac_sbatch_args cpu) jobs/partB_array.slurm
# or put the account and partition directives back in by hand.

#SBATCH --job-name=hw0b-B-sweep
#SBATCH --array=0-4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=48G
#SBATCH --time=00:45:00
#SBATCH --output=results/%x-%A_%a.out
#SBATCH --error=results/%x-%A_%a.err

set -uo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"; mkdir -p results
source deac/site.sh; deac_load_cpu

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

SIZES=(500 1000 2000 4000 8000)
N=${SIZES[$SLURM_ARRAY_TASK_ID]}

echo "array task $SLURM_ARRAY_TASK_ID  ->  N = $N  on $(hostname)"
python3 matmul_bench.py -n "$N" --json "results/hw0b_partB.jsonl"
