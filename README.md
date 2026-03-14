# Real‑Time Upscaler for Linux

[![PyPI version](https://img.shields.io/pypi/v/linux-rt-upscaler.svg)](https://pypi.org/project/linux-rt-upscaler/)
[![Python versions](https://img.shields.io/pypi/pyversions/linux-rt-upscaler.svg)](https://pypi.org/project/linux-rt-upscaler/)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A real‑time AI upscaler for any application window on GNU/Linux. It uses CuNNy neural networks to perform 2× upscaling, then scales the result to full screen while preserving aspect ratio. Mouse clicks and motion are automatically forwarded to the original window.

## Based on

Based on [RealTimeSuperResolutionScreenUpscalerforLinux](https://github.com/L65536/RealTimeSuperResolutionScreenUpscalerforLinux) by [L65536](https://github.com/L65536), with the following differences:

- **Full‑screen scaling** – The upscaled image now fills the monitor, applying a second scaling layer while preserving aspect ratio.
- **Click/motion forwarding** – Mouse clicks and motion are forwarded to the original window with proper coordinate transformation. This can be deactivated with the `-d` option.
- **Support all CuNNy NVL models** – All NVL models have been translated to pure HLSL to use.

## Features

- **AI‑Powered Upscaling** – Uses the CuNNy (Convolutional upscaling Neural Network) models, trained specifically for high‑quality 2× upscaling of visual novels and illustrations .
- **Complete Model Selection** – Choose from all nine CuNNy NVL variants, offering a range of quality/performance trade‑offs:
  - `8x32` – Highest quality, slowest. Uses 8 internal convolutions with 32 feature layers.
  - `4x32` – Excellent quality, slightly faster than 8x32.
  - `4x24` – Balanced high quality with reduced layer size.
  - `4x16` – Good quality, moderate speed.
  - `4x12` – Lower quality, faster performance.
  - `3x12` – Reduced convolution count for better speed.
  - `fast` – Recommended for slower machines, good balance.
  - `faster` – Prioritizes speed over quality.
  - `veryfast` – Fastest option, lowest quality .
- **Attach to Any Window** – Either grab the currently active window or launch a new program and capture its window automatically.
- **Full‑Screen Output** – The upscaled image is displayed in a transparent overlay that covers your entire monitor, scaled to fill the screen while preserving aspect ratio.
- **Input Forwarding** – Click, move, and drag on the upscaled image as if you were interacting directly with the original window.
- **Hardware Accelerated** – GPU compute via Compushady (Vulkan) works on NVIDIA, AMD, and Intel GPUs.
- **Low Overhead** – Minimal CPU/GPU usage; the final scaling pass uses hardware Lanczos2 filtering.

## Requirements

- GNU/Linux with X11 (Wayland is **not** supported)
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

# Run a command and upscale its window
upscale <command>

# Choose a specific model (examples)
upscale -m 4x32      # High quality, balanced performance
upscale -m fast       # Recommended for slower machines
upscale -m veryfast   # Maximum performance

# Disable mouse‑click forwarding (also enables dimming/click‑through)
upscale -d

# Show help
upscale -h
```

### Command‑Line Options

| Option                        | Description                                                                                                                                    |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `-m, --model`                 | Select upscaling model: `8x32`, `4x32`, `4x24`, `4x16`, `4x12`, `3x12`, `fast`, `faster`, `veryfast`. Default is `8x32`.                    |
| `-d, --disable-click-forward` | Disable forwarding mouse clicks to the original window. Also enables overlay dimming (20% opacity when mouse leaves source) and click‑through. |
| `-h, --help`                  | Show the help message and exit.                                                                                                                |

### Controls

- **Exit**: Press `Ctrl+C` in the terminal where the upscaler is running.
- **Dimming/Click‑through** (only when `-d` is used):
  - The overlay becomes semi‑transparent (20% opacity) when the mouse leaves the source window.
  - Clicks then pass through to whatever window is underneath (e.g., your desktop or other applications).

## How It Works

1. **Window Selection** – Uses X11 to find the target window by PID or WM_CLASS.
2. **Capture** – Grabs the window's pixels using a fast custom C library.
3. **AI Upscaling** – CuNNy compute shaders (written in HLSL, compiled via Compushady) produce a 2× larger image .
4. **Aspect‑Preserving Scaling** – A lightweight Lanczos2 compute shader scales the upscaled image to fill the monitor, adding black bars to maintain the original aspect ratio.
5. **Display** – The result is rendered in a transparent overlay window that bypasses the window manager (so it always stays on top).
6. **Input Forwarding** – Mouse events are transformed using the scaling ratios and sent to the original window via `XSendEvent`.

## Future Plans

- [ ] **Wayland support** – Add compatibility for Wayland display servers (currently X11 only)
- [ ] **Window selection GUI** – Add an option to interactively select from visible windows at startup
- [ ] **Configuration YAML** – Implement a config file for persistent settings (default model, forwarding options, etc.)
- [ ] **Standalone GUI application** – Create a windowed app interface for easier management of the upscaler

## Acknowledgments

- **[L65536](https://github.com/L65536)** – For the original [RealTimeSuperResolutionScreenUpscalerforLinux](https://github.com/L65536/RealTimeSuperResolutionScreenUpscalerforLinux) project, which provided the foundational scripts and CuNNy integration 
- **[funnyplanter](https://github.com/funnyplanter)** – For [CuNNy](https://github.com/funnyplanter/CuNNy), the neural network upscaling models, especially the NVL variants trained for visual novel content 
- **[Compushady](https://github.com/rdeioris/compushady)** – Python library for GPU compute (Vulkan backend)
- **[PySide6](https://pypi.org/project/PySide6/)** – Qt bindings used for the overlay window
- **[python‑xlib](https://github.com/python-xlib/python-xlib)** – X11 client library for window management and input forwarding
- **[pyewmh](https://github.com/parkouss/pyewmh)** – Query and control of window manager
- **[psutil](https://github.com/giampaolo/psutil)** – Library for retrieving information on running processes
