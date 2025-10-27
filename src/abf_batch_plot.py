#!/usr/bin/env python3
"""
PANX1 Electrophysiology ABF Batch Plotting
------------------------------------------
This script processes multiple ABF (Axon Binary Format) files recorded from patch-clamp
experiments, applies low-pass filtering, and generates overlaid sweep plots with
baseline and measurement markers.
"""

import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import pyabf
import sys


def get_sample_rate(abf: pyabf.ABF) -> float:
    """Return sample rate in Hz, supporting both old and new pyABF attributes."""
    if hasattr(abf, "sampleRateHz"):
        return float(abf.sampleRateHz)
    if hasattr(abf, "dataRate"):
        return float(abf.dataRate)
    raise AttributeError("ABF sample rate not found (sampleRateHz or dataRate missing).")


def low_pass_filter(data: np.ndarray, cutoff_hz: float, fs_hz: float, order: int = 4) -> np.ndarray:
    """Apply a low-pass Butterworth filter with zero-phase filtering."""
    nyquist = 0.5 * fs_hz
    if cutoff_hz >= nyquist:
        raise ValueError(f"Cutoff ({cutoff_hz} Hz) must be less than Nyquist ({nyquist:.1f} Hz).")
    b, a = butter(order, cutoff_hz / nyquist, btype="low", analog=False)
    return filtfilt(b, a, data)


def build_filename(prefix_date: str, number: int) -> str:
    """Build filename like 2024_02_21_0077.abf."""
    return f"{prefix_date}_{number:04d}.abf"


def plot_one_abf(abf_path: Path, cutoff_hz: float, baseline: tuple[float, float], measure_t: float, outdir: Path):
    """Plot all sweeps from one ABF file with filtering and markers."""
    abf = pyabf.ABF(str(abf_path))
    fs = get_sample_rate(abf)

    fig, ax = plt.subplots(figsize=(12, 6))
    for sweep in range(abf.sweepCount):
        abf.setSweep(sweep)
        y = low_pass_filter(abf.sweepY, cutoff_hz, fs)
        ax.plot(abf.sweepX, y, linewidth=0.8)

    base1, base2 = baseline
    ax.axvline(x=base1, linestyle="--", color="r", label=f"baseline start ({base1:.4f}s)")
    ax.axvline(x=base2, linestyle="--", color="g", label=f"baseline end ({base2:.4f}s)")
    ax.axvline(x=measure_t, linestyle="--", color="b", label=f"measure ({measure_t:.4f}s)")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Current (A.U.)")
    ax.set_title(f"ABF sweeps: {abf_path.name}")
    ax.legend()

    outdir.mkdir(parents=True, exist_ok=True)
    stem = abf_path.stem
    for ext in ["png", "pdf"]:
        out_file = outdir / f"{stem}.filtered.{ext}"
        fig.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Batch plot ABF files with low-pass filtering.")
    parser.add_argument("--base-dir", required=True, type=Path, help="Directory containing ABF files")
    parser.add_argument("--date-prefix", default="2024_02_21", help="ABF filename prefix (e.g., 2024_02_21)")
    parser.add_argument("--start", type=int, required=True, help="Start number (e.g., 77)")
    parser.add_argument("--end", type=int, required=True, help="End number (inclusive, e.g., 84)")
    parser.add_argument("--cutoff", type=float, default=1000.0, help="Low-pass cutoff (Hz)")
    parser.add_argument("--baseline", nargs=2, type=float, metavar=("T_START", "T_END"), default=[0.005, 0.011],
                        help="Baseline window (s)")
    parser.add_argument("--measure", type=float, default=0.0159, help="Measurement time (s)")
    parser.add_argument("--outdir", type=Path, default=Path("outputs"), help="Output directory for figures")
    args = parser.parse_args()

    missing_files = []
    for n in range(args.start, args.end + 1):
        fname = build_filename(args.date_prefix, n)
        fpath = args.base_dir / fname
        if not fpath.exists():
            missing_files.append(str(fpath))
            continue
        try:
            plot_one_abf(fpath, args.cutoff, tuple(args.baseline), args.measure, args.outdir)
            print(f"[OK] Processed {fpath}")
        except Exception as e:
            print(f"[ERROR] {fpath}: {e}", file=sys.stderr)

    if missing_files:
        print("\n[WARNING] Missing files:")
        for m in missing_files:
            print(" -", m)


if __name__ == "__main__":
    main()
