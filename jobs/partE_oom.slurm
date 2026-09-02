#!/bin/bash
# Part E, failure 2. This job is designed to exceed its memory allocation.
# It asks for 2 GB and allocates roughly 8 GB.

#SBATCH --job-name=hw0b-E-oom
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=results/%x-%j.out
#SBATCH --error=results/%x-%j.err

set -uo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"; mkdir -p results
source deac/site.sh; deac_load_cpu

echo "start $(date -Iseconds) on $(hostname), mem request ${SLURM_MEM_PER_NODE:-unset} MB"
python3 -c "
import numpy as np
blocks = []
for i in range(16):
    blocks.append(np.ones(64 * 1024 * 1024, dtype=np.float64))  # 512 MB each
    print(f'allocated {(i + 1) * 0.5:.1f} GB', flush=True)
"
echo "this line should never be reached"
