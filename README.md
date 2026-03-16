# Real‑Time Upscaler for Linux

[![PyPI version](https://img.shields.io/pypi/v/linux-rt-upscaler.svg)](https://pypi.org/project/linux-rt-upscaler/)
[![Python versions](https://img.shields.io/pypi/pyversions/linux-rt-upscaler.svg)](https://pypi.org/project/linux-rt-upscaler/)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A real‑time AI upscaler for any application window on GNU/Linux. It uses [CuNNy](https://github.com/funnyplanter/CuNNy) neural networks to perform 2× (or 4×) upscaling, then scales the result to full screen while preserving aspect ratio. Mouse clicks and motion are automatically forwarded to the original window.

Now with full **XWayland support** – works seamlessly under Wayland compositors!

## Results at 400% magnification

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/docs/comparisons/gurikaji/w40-60_h20-50_4x_comparison.png)

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/docs/comparisons/fatamoru/w30-50_h10-50_4x_comparison.png)

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/docs/comparisons/konosora/w10-30_h20-50_4x_comparison.png)

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/docs/comparisons/diagram/w40-70_h40-90_4x_comparison.png)

## Features

- **AI‑Powered Upscaling** – Uses the CuNNy (Convolutional upscaling Neural Network) models, trained specifically for high‑quality 2× upscaling of visual novels and illustrations.
- **Complete Model Selection** – Choose from 9 variants, offering a range of quality/performance trade‑offs:
  - `8x32` – Highest quality, slowest.
  - `4x32`
  - `4x24`
  - `4x16`
  - `4x12`
  - `3x12`
  - `fast` – Default. Recommended for slow machines.
  - `faster`
  - `veryfast` – Fastest option, lowest quality.
- **Attach to Any Window** – Either grab the currently active window, select from visible windows or launch a new program and capture its window automatically.
- **Full‑Screen Output** – The upscaled image is displayed in a transparent overlay that covers your entire monitor, scaled to fill the screen while preserving aspect ratio.
- **Input Forwarding** – Click, move, and drag on the upscaled image as if you were interacting directly with the original window.
- **Hardware Accelerated** – GPU compute via Compushady (Vulkan) works on NVIDIA, AMD, and Intel GPUs.
- **XWayland Compatible** – Runs under Wayland compositors by automatically forcing X11 platform for Qt and disabling Wayland Vulkan extensions.
- **Low Overhead** – Minimal CPU/GPU usage; the final scaling pass uses hardware Lanczos2 filtering.

## Requirements

- GNU/Linux (X11 or Wayland with XWayland)
- Vulkan-capable GPU from any vendor (NVIDIA, AMD, Intel)
- Vulkan drivers (`libvulkan-dev` on Debian/Ubuntu)
- X11 development libraries (`libx11-dev`)
- Python 3.8 or newer

## Installation

### 1. System dependencies

#### Debian / Ubuntu / Linux Mint

```sh
sudo apt update
sudo apt install libvulkan-dev libx11-dev
```

#### Fedora / RHEL / CentOS (with EPEL)

```sh
sudo dnf install vulkan-loader-devel libX11-devel
```

#### Arch Linux

```sh
sudo pacman -S vulkan-devel libx11
```

#### openSUSE

```sh
sudo zypper install vulkan-devel libX11-devel
```

#### Alpine Linux

```sh
sudo apk add vulkan-headers libx11-dev
```

### 2. Python package

#### Install with pipx (recommended)

```sh
pipx install linux-rt-upscaler
```

#### Or with regular pip (inside a virtual environment is advised)

```sh
pip install linux-rt-upscaler
```

#### Or install from source

```sh
# Clone the repository
git clone https://github.com/baronsmv/linux-rt-upscaler.git
cd linux-rt-upscaler

# Install Python dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

After installation, the `upscale` command will be available globally:

```bash
# Upscale the currently active window
upscale

# Interactively select from visible windows at startup
upscale -s

# Run a command and upscale its window
upscale <command>

# Choose a specific model (examples)
upscale -m 8x32      # Highest quality, slowest
upscale -m 4x24      # A balanced option
upscale -m veryfast  # Maximum performance

# Disable mouse‑click forwarding (also enables dimming/click‑through)
upscale -d

# Perform two 2× passes (total 4×) (Experimental)
upscale -2

# Show help and other options
upscale -h
```

### Controls

- **Exit**: Press `Ctrl+C` in the terminal where the upscaler is running.
- **Dimming/Click‑through** (only when `-d` is used):
  - The overlay becomes semi‑transparent (20% opacity) when the mouse leaves the source window.
  - Clicks then pass through to whatever window is underneath (e.g., your desktop or other applications).

## How It Works

1. **Window Selection** – Uses X11 to find the target window by PID or WM_CLASS.
2. **Capture** – Grabs the window's pixels using a fast custom C library.
3. **AI Upscaling** – CuNNy compute shaders (written in HLSL, compiled via Compushady) produce a 2× (or 4×) larger image .
4. **Aspect‑Preserving Scaling** – A lightweight Lanczos2 compute shader scales the upscaled image to fill the monitor, adding black bars to maintain the original aspect ratio.
5. **Display** – The result is rendered in a transparent overlay window that bypasses the window manager (so it always stays on top).
6. **Input Forwarding** – Mouse events are transformed using the scaling ratios and sent to the original window via `XSendEvent`.

## Future Plans

- [ ] **Standalone GUI application** – Create a windowed app interface for easier management.
- [ ] **Addition of more models** – Parse and include other models and shaders.
- [ ] **Native Wayland support** – Support pure Wayland windows without XWayland.
- [ ] **Option to force screen aspect ratio** – Let users choose between letterboxing or stretching.

## Motivation

While real-time upscaling tools like [Magpie](https://github.com/Blinue/Magpie) and [Lossless Scaling](https://losslessscaling.com/) remain Windows-exclusive, projects such as [lsfg-vk](https://github.com/PancakeTAS/lsfg-vk) are successfully bringing their **frame generation** capabilities to Linux.

This project tackles the other half of the equation: **AI-powered upscaling** to deliver a native solution Linux has been missing, a fullscreen [Gamescope](https://github.com/ValveSoftware/gamescope)-like experience that applies intelligent upscaling (similar to [Anime4K](https://github.com/bloc97/Anime4K)) to any application.

## Acknowledgments

This project stands on the shoulders of several open‑source works:

- **[L65536](https://github.com/L65536)** – For the original [RealTimeSuperResolutionScreenUpscalerforLinux](https://github.com/L65536/RealTimeSuperResolutionScreenUpscalerforLinux), which demonstrated the feasibility of real‑time CuNNy upscaling on Linux. This project extends that foundation with full‑screen scaling, accurate input forwarding, and support for all CuNNy NVL models and GPU vendors.
- **[funnyplanter](https://github.com/funnyplanter)** – For [CuNNy](https://github.com/funnyplanter/CuNNy), the neural network upscaling models, especially the Magpie NVL variants trained for visual novel content.
- **[Compushady](https://github.com/rdeioris/compushady)** – Python library for GPU compute (Vulkan backend).
- **[PySide6](https://pypi.org/project/PySide6/)** – Qt bindings used for the overlay window.
- **[python‑xlib](https://github.com/python-xlib/python-xlib)** – X11 client library for window management and input forwarding.
- **[pyewmh](https://github.com/parkouss/pyewmh)** – Query and control of window manager.
- **[psutil](https://github.com/giampaolo/psutil)** – Library for retrieving information on running processes.
