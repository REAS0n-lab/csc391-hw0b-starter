#!/bin/bash
# Environment validation for the CSC 391/691 HW0b starter.
#
#   ./validate.sh              login-node checks only
#   ./validate.sh --submit     also submit the array, two-node, and GPU jobs
#
# The three submitted jobs are the ones that need cluster configuration the
# course cannot check from a login node. Every check runs to completion.

set -uo pipefail
cd "$(dirname "$0")"
PASS=0; FAIL=0
ok()   { echo "[ok  ] $*"; PASS=$((PASS+1)); }
bad()  { echo "[FAIL] $*"; FAIL=$((FAIL+1)); }
info() { echo "[info] $*"; }

echo "=== CSC 391/691 HW0b starter validation ==="
echo "host $(hostname)   date $(date -Iseconds)"
echo

if source deac/site.sh 2>/dev/null; then ok "deac/site.sh sources"; else bad "deac/site.sh sources"; fi
info "account   ${DEAC_ACCOUNT:-unset}"
info "cpu part  ${DEAC_CPU_PARTITION:-unset}"
info "gpu part  ${DEAC_GPU_PARTITION:-unset}"
info "gres      ${DEAC_GPU_GRES:-unset}"
info "max nodes ${DEAC_MAX_NODES:-unset}"

deac_load_cpu 2>/dev/null || info "deac_load_cpu reported an error, continuing"
if python3 -c "import numpy" 2>/dev/null; then ok "numpy importable"; else bad "numpy importable"; fi

for tool in sbatch sacct sinfo squeue scancel; do
  if command -v $tool >/dev/null; then ok "$tool on PATH"; else bad "$tool on PATH"; fi
done
if command -v seff >/dev/null; then ok "seff on PATH"; else info "seff absent, part A falls back to sacct"; fi

for part in "${DEAC_CPU_PARTITION:-}" "${DEAC_GPU_PARTITION:-}"; do
  [ -z "$part" ] && continue
  if sinfo -h -p "$part" >/dev/null 2>&1 && [ -n "$(sinfo -h -p "$part" -o '%P')" ]; then
    ok "partition $part exists"
    sinfo -h -p "$part" -o '       %P avail=%a maxtime=%l nodes=%D state=%T cpus=%c mem=%m gres=%G' | head -4
  else
    bad "partition $part exists"
  fi
done

if [ -n "${DEAC_CPU_PARTITION:-}" ]; then
  AVAIL=$(sinfo -h -p "$DEAC_CPU_PARTITION" -o '%D' 2>/dev/null | paste -sd+ | bc 2>/dev/null || echo 0)
  info "nodes visible in ${DEAC_CPU_PARTITION}: ${AVAIL}"
  if [ "${AVAIL:-0}" -ge "${DEAC_MAX_NODES:-8}" ] 2>/dev/null; then
    ok "partition has at least DEAC_MAX_NODES=${DEAC_MAX_NODES} nodes"
  else
    bad "partition has at least DEAC_MAX_NODES=${DEAC_MAX_NODES} nodes (HW2 sweeps to this)"
  fi
fi

echo
echo "--- GPU stack (informational on a login node) ---"
deac_load_gpu 2>/dev/null || info "deac_load_gpu reported an error, continuing"
if command -v nvidia-smi >/dev/null; then
  info "nvidia-smi present on this host"
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv 2>/dev/null | head -3
else
  info "no nvidia-smi on the login node, which is expected. The GPU check is the batch job."
fi
python3 -c "import torch; print('[info] torch', torch.__version__, 'cuda', torch.version.cuda)" 2>/dev/null \
  || python3 -c "import cupy; print('[info] cupy', cupy.__version__)" 2>/dev/null \
  || info "neither torch nor cupy importable on the login node"

if [ "${1:-}" = "--submit" ]; then
  echo
  echo "--- submitting ---"
  mkdir -p results
  ARGS_CPU=$(deac_sbatch_args cpu)
  ARGS_GPU=$(deac_sbatch_args gpu)
  for spec in "cpu jobs/partB_array.slurm" "cpu jobs/partC_two_nodes.slurm" "gpu jobs/partD_gpu.slurm"; do
    set -- $spec
    KIND=$1; SCRIPT=$2
    ARGS=$([ "$KIND" = gpu ] && echo "$ARGS_GPU" || echo "$ARGS_CPU")
    if JOB=$(sbatch --parsable $ARGS "$SCRIPT" 2>&1); then
      ok "submitted $SCRIPT as $JOB"
    else
      bad "submitted $SCRIPT ($JOB)"
    fi
  done
  info "when they finish, confirm part C printed two distinct hostnames"
fi

echo
echo "passed $PASS   failed $FAIL"
[ "$FAIL" -eq 0 ]
