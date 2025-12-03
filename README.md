# PANX1 Electrophysiology ABF Batch Plotting

This repository provides Python scripts for analyzing and visualizing patch-clamp electrophysiology data recorded in the Axon Binary Format (ABF).  
The code was developed for the processing and figure generation of PANX1 current recordings used in the manuscript submitted.

---

## Overview

The scripts load multiple ABF files, apply digital low-pass filtering, and plot all sweeps from each file with clearly marked baseline and measurement windows.  
The filtering step removes high-frequency noise while preserving physiologically relevant current kinetics.

---

## Features

- Batch processing of ABF files (e.g., `2024_02_21_0077.abf` – `2024_02_21_0084.abf`)
- Zero-phase low-pass Butterworth filtering (4th order)
- Automatic visualization of all sweeps with baseline and measurement markers
- Optional figure export as `.png` and `.pdf`
- Configurable parameters through command-line arguments

---

## Installation

Create a virtual environment and install the required Python packages:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
