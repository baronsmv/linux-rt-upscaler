# Real‑Time Upscaler for Linux

[![PyPI version](https://img.shields.io/pypi/v/linux-rt-upscaler.svg)](https://pypi.org/project/linux-rt-upscaler/)
[![Python versions](https://img.shields.io/pypi/pyversions/linux-rt-upscaler.svg)](https://pypi.org/project/linux-rt-upscaler/)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A real‑time AI upscaler for any application window on GNU/Linux. Uses **CuNNy‑veryfast** neural networks to perform 2× upscaling, with full‑screen stretching and optional click/motion forwarding.

## Based on

Based on [RealTimeSuperResolutionScreenUpscalerforLinux](https://github.com/L65536/RealTimeSuperResolutionScreenUpscalerforLinux) by L65536, with the following differences:

- **Full‑screen scaling** – The upscaled image now fills the monitor, applying a second scaling layer while preserving aspect ratio.
- **Click/motion forwarding** – With the `-m` flag, mouse clicks and motion are forwarded to the original window with proper coordinate transformation.

## Features

- **AI‑Powered Upscaling** – Uses CuNNy‑veryfast (4‑pass) neural network for high‑quality 2× upscaling.
- **Any Window** – Attach to an existing window or launch a new program.
- **Full‑Screen Output** – Stretch the upscaled image to fill your monitor (aspect‑ratio preserved, black bars).
- **Click/Motion Forwarding** (`-m`) – Click and move the mouse on the upscaled image as if it were the real window.
- **Opacity Control** – Overlay dims when mouse leaves the source window (optional, disabled with `-m`).
- **Hardware Accelerated** – GPU‑based compute via Compushady (Vulkan) – works on NVIDIA, AMD, and Intel.
- **Low Overhead** – Minimal performance impact; scaling pass uses hardware bilinear filtering.

## Requirements

- GNU/Linux with X11 (Wayland not supported)
- Vulkan-capable GPU from any vendor (NVIDIA, AMD, Intel)
- Vulkan drivers (`libvulkan-dev` on Debian/Ubuntu)
- X11 development libraries (`libx11-dev`)
- Python 3.8 or newer

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
# Install system dependencies (Debian/Ubuntu)
sudo apt install libvulkan-dev libx11-dev

# Install with pipx (recommended)
pipx install linux-rt-upscaler

# Or with regular pip
pip install linux-rt-upscaler
```

### Option 2: Install from source

```bash
# Clone the repository
git clone https://github.com/baronsmv/linux-rt-upscaler.git
cd linux-rt-upscaler

# Install system dependencies (Debian/Ubuntu)
sudo apt install libvulkan-dev libx11-dev

# Install Python packages
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

After installation, the `upscale` command will be available globally:

```bash
# Upscale the currently active window
upscale

# Enable click/motion forwarding (mouse interacts with upscaled window)
upscale -m
```

### Controls

- **Exit** – Press Ctrl+C in terminal
- **Opacity** – Without `-m`, overlay dims to 20% when mouse leaves source window
- **Click‑through** – Without `-m`, clicks pass through to underlying windows

## How It Works

1. **Window Selection** – Uses X11 to find the target window by PID or WM_CLASS
2. **Capture** – Fast X11 window capture via custom C library
3. **AI Upscaling** – Four CuNNy compute shaders produce 2× image
4. **Aspect Scaling** – Lightweight bilinear compute shader scales to full screen (preserves ratio)
5. **Display** – Rendered in a transparent overlay (bypasses window manager)
6. **Input Forwarding** – With `-m`, mouse events are transformed and sent to original window using XSendEvent

## Acknowledgments

- **[L65536](https://github.com/L65536)** – For the original [RealTimeSuperResolutionScreenUpscalerforLinux](https://github.com/L65536/RealTimeSuperResolutionScreenUpscalerforLinux) project, which provided the foundational scripts and CuNNy integration
- **CuNNy** – Neural network upscaling models
- **Compushady** – Python GPU compute library
- **PySide6** – Qt bindings for the overlay
- **python‑xlib** – X11 client library

