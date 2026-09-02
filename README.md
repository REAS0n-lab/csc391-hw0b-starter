# CSC 391/691 HW0b starter

This repository contains the job scripts and harnesses for HW0b. HW0a
established that you have an account and can get output back. This assignment
establishes that you can drive the scheduler deliberately.

The job scripts here are the ones HW2 runs. Treat them as infrastructure you
are building rather than an exercise you are completing.

**Assigned 9/16. Due Friday 9/18.**

## Layout

```
matmul_bench.py             carried over from HW0a, unchanged
matmul_bench_gpu.py         the same benchmark on a GPU, with a real timer
submit.sh                   submit wrapper, three TODOs are yours
scripts/collect.py          result collection, two functions are yours
jobs/partA_overrequest.slurm  8 cores requested, 1 used
jobs/partA_matched.slurm      1 core requested, 1 used
jobs/partB_array.slurm        one array submission, five problem sizes
jobs/partC_two_nodes.slurm    two nodes, one process each
jobs/partD_gpu.slurm          one GPU, device report and benchmark
jobs/partE_timeout.slurm      exceeds its time limit on purpose
jobs/partE_oom.slurm          exceeds its memory allocation on purpose
deac/site.sh                account, partitions, gres, and module loads
tests/                      offline tests, no cluster needed
```

No job script carries an `--account` or `--partition` directive. Both come
from `deac/site.sh` through the submit wrapper, so a change to the course
allocation is one edit rather than seven.

## Submitting

Once `submit.sh` works, every job in this repository is launched the same way.

```bash
./submit.sh cpu jobs/partB_array.slurm
./submit.sh gpu jobs/partD_gpu.slurm
./submit.sh cpu jobs/partC_two_nodes.slurm --nodes=4
```

Until then you can pass the flags directly.

```bash
sbatch $(source deac/site.sh; deac_sbatch_args cpu) jobs/partB_array.slurm
```

## What you write

Two files are deliberately incomplete, and both are HW2 infrastructure.

**`submit.sh`** has three TODOs. Assemble the sbatch flags, submit with
`--parsable` so the job id is the only thing on stdout, and append the id,
script, flags, and timestamp to `results/jobs.log`. A job id you did not save
is a measurement you cannot reconstruct.

**`scripts/collect.py`** has two functions to write, `summarize` and
`to_markdown`. `tests/test_collect.py` is the specification. Run it with

```bash
python3 -m pytest tests -q
```

Five output files that you read by eye and retyped into a table is a process
that does not survive being run thirty times, which is roughly what HW2 needs.

## Part A, the cost of a request

Run the same benchmark twice, once asking for 8 cores and using 1, once asking
for 1 and using 1. Report `seff <jobid>` for each, or

```bash
sacct -j <jobid> --format=JobID,ReqCPUS,AllocCPUS,Elapsed,CPUTime,MaxRSS
```

Then state, in core-hours, what the first job took from the cluster and did not
use. `CPUTime` is allocated cores times elapsed time, which is the number you
want. DEAC is shared, and seven idle reserved cores are seven cores someone
else's job was queued for.

## Part C, read the hostnames

```bash
srun --ntasks=2 --ntasks-per-node=1 hostname | sort -u
```

Two distinct hostnames is the whole point. A script that requests two nodes and
quietly runs both processes on one produces plausible timings and a scaling
curve that is entirely an artifact. Confirm it here so you can rule it out
later.

## Part D, two GPU numbers

`jobs/partD_gpu.slurm` runs the GPU benchmark twice, once with warmup and
device synchronization and once with neither. Keep both.

`matmul_bench_gpu.py` synchronizes the device before stopping the timer,
because a kernel launch returns before the kernel finishes and a timer that
does not synchronize measures the launch. It also times the host to device
copy separately from the multiply, because the two answer different questions.

Do not try to explain the CPU to GPU ratio yet. Write it down and keep it. The
GPU module starting 9/30 is about why it is what it is, and about why the
number you measured is probably not the number you think it is.

## Part E, break it on purpose

Both failure jobs are designed to fail. `partE_timeout.slurm` asks for one
minute and works for ten. `partE_oom.slurm` asks for 2 GB and allocates about
8 GB. For each, report the output file, `sacct` state and exit code, and how
you would recognize the failure if you had not caused it.

```bash
sacct -j <jobid> --format=JobID,JobName,State,ExitCode,DerivedExitCode,MaxRSS,ReqMem,Elapsed,Timelimit
```

A timeout shows `TIMEOUT` and a memory kill usually shows `OUT_OF_MEMORY` or a
`CANCELLED` state with exit code 137, which is 128 plus SIGKILL. The harder
question in the assignment is what either looks like when it hits one task in
an array of thirty, and the answer is that nothing announces it. That is why
`collect.py` reports `runs` next to `stdev`.

## Validation

`./validate.sh` reports the state of the environment and `./validate.sh
--submit` also submits the array, two-node, and GPU jobs. Course staff use it
to confirm the repository works on the current DEAC configuration.
