#!/bin/bash
# Part C. Two nodes, one process per node, each printing rank and hostname.
#
# Two distinct hostnames is the whole point. A script that asks for two nodes
# and quietly runs both processes on one produces plausible timings and a
# scaling curve that is an artifact. Read the hostnames.

#SBATCH --job-name=hw0b-C-nodes
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=results/%x-%j.out
#SBATCH --error=results/%x-%j.err

set -uo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"; mkdir -p results
source deac/site.sh; deac_load_cpu

echo "SLURM_JOB_NODELIST  ${SLURM_JOB_NODELIST:-unset}"
echo "SLURM_NNODES        ${SLURM_NNODES:-unset}"
echo
srun --ntasks=2 --ntasks-per-node=1 bash -c 'echo "rank ${SLURM_PROCID} on $(hostname)"'
echo
echo "distinct hosts seen by srun:"
srun --ntasks=2 --ntasks-per-node=1 hostname | sort -u
