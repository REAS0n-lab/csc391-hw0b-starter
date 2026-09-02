#!/bin/bash
# Part D. One GPU. Reports the device, then runs the matmul on it.
#
# Submit with
#   sbatch $(source deac/site.sh; deac_sbatch_args gpu) jobs/partD_gpu.slurm

#SBATCH --job-name=hw0b-D-gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --output=results/%x-%j.out
#SBATCH --error=results/%x-%j.err

set -uo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"; mkdir -p results
source deac/site.sh; deac_load_gpu

echo "=== device ==="
nvidia-smi
echo
nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv
echo

echo "=== matmul on GPU, N = 4000 ==="
python3 matmul_bench_gpu.py -n 4000 --json results/hw0b_partD.jsonl
echo

echo "=== the same run with no warmup and no synchronization discipline ==="
echo "Keep both numbers. The gap between them is a deposit for 9/30."
python3 matmul_bench_gpu.py -n 4000 --no-warmup -r 1 --json results/hw0b_partD.jsonl
