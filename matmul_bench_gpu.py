#!/usr/bin/env python3
"""GPU dense matrix multiply timing harness.

Same operation and same GFLOP/s formula as matmul_bench.py, run on a GPU.
Uses PyTorch if it is importable and falls back to CuPy.

Three things separate this from the CPU harness and all three matter later.

  1. Kernel launches are asynchronous. The timer must synchronize the device
     before it stops, otherwise it measures the launch and not the work.
  2. The first launch pays for context creation and autotuning. --warmup
     controls how many untimed iterations run first.
  3. Host to device transfer is timed separately from the multiply, because
     the two answer different questions.
"""

import argparse
import json
import os
import socket
import sys
import time


def load_backend(prefer):
    """Return (name, module) for the array backend that is available."""
    order = ["torch", "cupy"] if prefer in (None, "auto", "torch") else ["cupy", "torch"]
    errors = {}
    for name in order:
        try:
            if name == "torch":
                import torch
                if not torch.cuda.is_available():
                    errors["torch"] = "torch imported but torch.cuda.is_available() is False"
                    continue
                return "torch", torch
            import cupy
            return "cupy", cupy
        except Exception as exc:  # pragma: no cover - depends on the node
            errors[name] = repr(exc)
    raise SystemExit(
        "No usable GPU backend.\n"
        + "\n".join(f"  {k}: {v}" for k, v in errors.items())
        + "\nLoad the CUDA module and check that the job requested a GPU."
    )


def device_info(name, mod):
    if name == "torch":
        i = mod.cuda.current_device()
        props = mod.cuda.get_device_properties(i)
        return {
            "backend": "torch",
            "backend_version": mod.__version__,
            "cuda_version": mod.version.cuda,
            "device_name": props.name,
            "device_memory_gb": round(props.total_memory / 1e9, 2),
            "multiprocessors": props.multi_processor_count,
            "capability": f"{props.major}.{props.minor}",
        }
    props = mod.cuda.runtime.getDeviceProperties(0)
    return {
        "backend": "cupy",
        "backend_version": mod.__version__,
        "cuda_version": str(mod.cuda.runtime.runtimeGetVersion()),
        "device_name": props["name"].decode(),
        "device_memory_gb": round(props["totalGlobalMem"] / 1e9, 2),
        "multiprocessors": props["multiProcessorCount"],
        "capability": f"{props['major']}.{props['minor']}",
    }


def make_matrices(name, mod, n, dtype, seed):
    if name == "torch":
        dt = {"float32": mod.float32, "float64": mod.float64}[dtype]
        gen = mod.Generator(device="cuda").manual_seed(seed)
        a = mod.randn(n, n, generator=gen, device="cuda", dtype=dt)
        b = mod.randn(n, n, generator=gen, device="cuda", dtype=dt)
        return a, b
    mod.random.seed(seed)
    a = mod.random.standard_normal((n, n), dtype=dtype)
    b = mod.random.standard_normal((n, n), dtype=dtype)
    return a, b


def synchronize(name, mod):
    if name == "torch":
        mod.cuda.synchronize()
    else:
        mod.cuda.Stream.null.synchronize()


def time_transfer(name, mod, n, dtype, seed):
    """Time one host to device copy of a single N x N matrix."""
    import numpy as np
    rng = np.random.default_rng(seed)
    host = rng.standard_normal((n, n), dtype=np.dtype(dtype))
    synchronize(name, mod)
    start = time.perf_counter()
    if name == "torch":
        dev = mod.from_numpy(host).cuda()
    else:
        dev = mod.asarray(host)
    synchronize(name, mod)
    elapsed = time.perf_counter() - start
    del dev
    return elapsed, host.nbytes


def run(name, mod, n, reps, warmup, dtype, seed):
    a, b = make_matrices(name, mod, n, dtype, seed)

    for _ in range(warmup):
        c = a @ b
    synchronize(name, mod)

    times = []
    for _ in range(reps):
        start = time.perf_counter()
        c = a @ b
        synchronize(name, mod)
        times.append(time.perf_counter() - start)

    checksum = float(c[0, 0])
    return times, checksum


def gflops(n, seconds):
    return (2.0 * n ** 3) / seconds / 1e9


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-n", "--size", type=int, required=True)
    p.add_argument("-r", "--reps", type=int, default=5)
    p.add_argument("-w", "--warmup", type=int, default=3)
    p.add_argument("--dtype", default="float64", choices=["float32", "float64"])
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--backend", default="auto", choices=["auto", "torch", "cupy"])
    p.add_argument("--no-warmup", action="store_true",
                   help="set warmup to 0, for the comparison in part D")
    p.add_argument("--json", default=None)
    args = p.parse_args(argv)
    if args.no_warmup:
        args.warmup = 0

    name, mod = load_backend(args.backend)
    info = device_info(name, mod)
    info["hostname"] = socket.gethostname()
    info["slurm_job_id"] = os.environ.get("SLURM_JOB_ID", "")

    for k, v in info.items():
        print(f"{k:<20}{v}")
    print()

    xfer, nbytes = time_transfer(name, mod, args.size, args.dtype, args.seed)
    print(f"host to device      {xfer:.6f} s for {nbytes/1e6:.1f} MB "
          f"({nbytes/xfer/1e9:.2f} GB/s)")
    print()

    times, checksum = run(name, mod, args.size, args.reps, args.warmup,
                          args.dtype, args.seed)
    print(f"N {args.size}   dtype {args.dtype}   warmup {args.warmup}   reps {args.reps}")
    print(f"{'rep':>4}  {'seconds':>12}  {'GFLOP/s':>12}")
    for i, t in enumerate(times):
        print(f"{i:>4}  {t:>12.6f}  {gflops(args.size, t):>12.3f}")
    best = min(times)
    print()
    print(f"best        {best:.6f} s   {gflops(args.size, best):.3f} GFLOP/s")
    print(f"checksum    {checksum:.6e}")

    if args.json:
        with open(args.json, "a") as fh:
            for i, t in enumerate(times):
                record = {
                    "benchmark": "matmul",
                    "device": "gpu",
                    "n": args.size,
                    "rep": i,
                    "dtype": args.dtype,
                    "warmup": args.warmup,
                    "seconds": t,
                    "gflops": gflops(args.size, t),
                    "transfer_seconds": xfer,
                    "transfer_bytes": nbytes,
                }
                record.update(info)
                fh.write(json.dumps(record) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
