# Real-Time Upscaler for Linux

[![PyPI version](https://img.shields.io/pypi/v/linux-rt-upscaler.svg)](https://pypi.org/project/linux-rt-upscaler/)
[![Python versions](https://img.shields.io/pypi/pyversions/linux-rt-upscaler.svg)](https://pypi.org/project/linux-rt-upscaler/)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A real-time SRCNN upscaler for any X-Window (X11 or XWayland) on GNU/Linux. It uses [CuNNy](https://github.com/funnyplanter/CuNNy) neural networks to perform 2x (or 4x) upscaling to full screen while preserving aspect ratio. Mouse clicks and motion are automatically forwarded to the original window.

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/refs/heads/main/docs/gui/screenshots/dark_02.png)

## Results at 400% magnification

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/docs/comparisons/gurikaji/w40-60_h20-50_4x_comparison.png)

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/docs/comparisons/fatamoru/w30-50_h10-50_4x_comparison.png)

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/docs/comparisons/konosora/w10-30_h20-50_4x_comparison.png)

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/docs/comparisons/diagram/w40-70_h40-90_4x_comparison.png)

## Features

- **Neural-Network Upscaling** using SRCNNs trained specifically for high-quality 2x upscaling of visual novels and illustrations.
- **Complete Model Selection** from 9 variants with variable quality/performance trade-offs.
- **Tile‑Based Processing** that divides each frame into tiles and upscaling only the regions that change, reducing GPU load for mostly static content.
- **Select Any Window** from a list of visible windows or by its name.
- **Flexible Output Geometry**: scaling mode (fit, stretch, cover), offset, crop and zoom.
- **Input Forwarding** as if interacting directly with the original window.
- **Hardware Accelerated** using Vulkan compute.

## Requirements

- GNU/Linux (X11 or Wayland with XWayland)
- Vulkan-capable GPU (NVIDIA, AMD, Intel)
- Python 3.10 or newer

## Installation

### Install with pipx

```sh
pipx install linux-rt-upscaler
```

### Install from source

<details>
<summary>Required development packages (click to expand)</summary>

#### Debian / Ubuntu / Linux Mint

```sh
sudo apt update
sudo apt install gcc make libvulkan-dev libx11-dev libxcb1-dev libx11-xcb-dev \
    libxext-dev libxdamage-dev libxfixes-dev
```

#### Fedora / RHEL / CentOS

```sh
sudo dnf install gcc make vulkan-loader-devel libX11-devel libxcb-devel libX11-xcb-devel \
    libXext-devel libXdamage-devel libXfixes-devel
```

#### Arch Linux / CachyOS

```sh
sudo pacman -S base-devel vulkan-devel libx11 libxcb libxext libxdamage libxfixes
```

#### openSUSE

```sh
sudo zypper install gcc make vulkan-devel libX11-devel libxcb-devel libX11-xcb-devel \
    libXext-devel libXdamage-devel libXfixes-devel
```

---

</details>

```sh
git clone https://github.com/baronsmv/linux-rt-upscaler.git
cd linux-rt-upscaler

pip install -e .
```

## Usage

After installation, the `upscale-gui` and `upscale` commands will be available globally:

### Graphical mode

```bash
upscale-gui
```

The GUI displays live thumbnails of every open valid window. Click one to start upscaling that window. 

Use the right panel to adjust any setting, and the left panel to create profiles that automatically apply when a matching window is detected, or when selected manually.

### Command-line mode

```bash
# Upscale the currently active window
upscale

# Interactively select from visible windows
upscale -s

# Run a command and upscale its window
upscale -- <command>

# Choose a specific model (examples)
upscale -m 8x32      # Highest quality, slowest
upscale -m veryfast  # Maximum performance

# Perform 4x upscaling (two 2x passes)
upscale -2

# Crop 100 pixels from top and left, then upscale
upscale --crop-top 100 --crop-left 100
```

For a full list of options and examples:

```bash
upscale --help
```

### Controls

| Shortcut                            | Action                                                                   |
| ----------------------------------- | ------------------------------------------------------------------------ |
| `Alt`+`Shift`+`S`                   | Toggle overlay visibility / pause processing                             |
| `Alt`+`Shift`+`M`                   | Switch to the next upscaling model                                       |
| `Alt`+`Shift`+`G`                   | Cycle output geometry (fit → stretch → cover)                            |
| `Alt`+`Shift`+`P`                   | Take a lossless screenshot (`--screenshot-dir DIR` defines the location) |
| `Alt`+`Shift`+`+` / `-`             | Zoom in / Zoom out                                                       |
| `Alt`+`Shift`+`↑` / `↓` / `←` / `→` | Pan the upscaled content                                                 |
| `Alt`+`Shift`+`Escape`              | Exit the application                                                     |

All hotkeys can be customised in the configuration file.

### Profiles

You can define named configuration profiles in your YAML config file. Profiles let you quickly switch settings for different games or applications without typing long command lines each time.

Create a config file (e.g., `~/.config/linux-rt-upscaler/config.yaml`) and add a top-level `profiles` key. Each profile is a dictionary with an optional `match` section and an `options` section.

If no profile is selected manually, the program checks all profiles that have a `match` section against the title of the target window. If a profile matches (any match criterion is sufficient), its options are applied automatically.

```yaml
# General defaults (lowest priority)
model: fast
select: false

profiles:
  game:
    match:
      title: "Danganronpa"     # Exact match (case-insensitive)
      title_contains: "ronp"   # Or substring match (case-insensitive)
      title_regex: "Dangan.*"  # Or regular expression (case-insensitive)
    options:
      model: 4x24
      double_upscale: true
```

A more detailed example is included [here](https://github.com/baronsmv/linux-rt-upscaler/blob/main/config-example.yaml).

## How It Works

1. **Selects** a window using X11 to find the target window by PID or WM_CLASS.
2. **Captures** the window's pixels using XShm and XDamage.
3. **Upscales** with SRCNN compute shaders to a 2x (or 4x) larger image.
4. **Scales** with a Lanczos2 shader to fill the monitor.
5. **Renders** in a overlay window that bypasses the window manager (so it always stays on top).
6. **Forwards** mouse events to the original window.

## Future Plans

- [ ] Addition of more SRCNN models ([FSRCNNX](https://github.com/awused/dotfiles/tree/master/mpv/.config/mpv/shaders/fsrcnnx) planned).
- [ ] ~~Native Wayland support~~ (**on hold**: the Wayland capture model would be deeply compositor-specific and doesn’t align with the XShm/XDamage pipeline.)

## Known Issues

### Mouse forwarding may not work with Wine, Proton <10 and other applications

Synthetic mouse events (clicks, motion, wheel) sent by the overlay are ignored by:

- Wine and Proton versions older than 10.0 (Proton 10 works correctly).
- Certain native applications like Firefox.

For more details, see [issue #7](https://github.com/baronsmv/linux-rt-upscaler/issues/7).

## Motivation

While real-time upscaling tools like [Magpie](https://github.com/Blinue/Magpie) and [Lossless Scaling](https://losslessscaling.com/) remain Windows-exclusive, projects such as [lsfg-vk](https://github.com/PancakeTAS/lsfg-vk) are successfully bringing their **frame generation** capabilities to Linux.

This project tackles the other half of the equation: **SRCNN upscaling** to deliver a native solution Linux has been missing, an experience similar to [Gamescope](https://github.com/ValveSoftware/gamescope) that applies intelligent upscaling (similar to [Anime4K](https://github.com/bloc97/Anime4K)) to any application.

## Acknowledgments

This project stands on the shoulders of several open-source works, mantained by amazing people:

- **[L65536](https://github.com/L65536)**, for the original [RealTimeSuperResolutionScreenUpscalerforLinux](https://github.com/L65536/RealTimeSuperResolutionScreenUpscalerforLinux), which demonstrated the feasibility of real-time CuNNy upscaling on Linux and served as a proof-of-concept for this project.
- **[funnyplanter](https://github.com/funnyplanter)**, for the incredible [CuNNy](https://github.com/funnyplanter/CuNNy) neural network upscaling models, especially the Magpie NVL variants trained on visual novel artwork.
- **[Compushady](https://github.com/rdeioris/compushady)**, which served as an invaluable foundation during early development.
- **[PySide6](https://pypi.org/project/PySide6/)**, the Qt binding that powers the entire graphical interface and overlay window.
- **[xcffib](https://github.com/tych0/xcffib)**, the low‑level XCB binding used for all window management and event forwarding.
- **[screeninfo](https://github.com/rr-/screeninfo)**, used for automatic scale factor detection in Wayland.
- **[psutil](https://github.com/giampaolo/psutil)**, used to locate the target window PID.
- **[Pillow](https://python-pillow.github.io/)**, used for saving screenshots and rendering OSD messages.
