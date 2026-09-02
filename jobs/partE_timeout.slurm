#!/bin/bash
# Part E, failure 1. This job is designed to exceed its time limit.
# The time limit is 1 minute and the work takes longer. That is the point.

#SBATCH --job-name=hw0b-E-timeout
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:01:00
#SBATCH --output=results/%x-%j.out
#SBATCH --error=results/%x-%j.err

set -uo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"; mkdir -p results
source deac/site.sh; deac_load_cpu
export OMP_NUM_THREADS=1

echo "start $(date -Iseconds) on $(hostname)"
python3 -c "
import time
for i in range(600):
    print(f'still running at {i} s', flush=True)
    time.sleep(1)
"
echo "this line should never be reached"
