<p align="center">
  <img src="https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/6f3f1c70b54e705665d2039d549afc0e4a8380b2/data/icons/hicolor/scalable/apps/io.github.baronsmv.linux-rt-upscaler.svg" width="128" alt="icon">
</p>

<h1 align="center">Real-Time Upscaler for Linux</h1>

<p align="center">
  <a href="https://pypi.org/project/linux-rt-upscaler/"><img src="https://img.shields.io/pypi/v/linux-rt-upscaler.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/linux-rt-upscaler/"><img src="https://img.shields.io/pypi/pyversions/linux-rt-upscaler.svg" alt="Python versions"></a>
  <a href="https://www.gnu.org/licenses/gpl-3.0"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPLv3"></a>
</p>

A real-time SRCNN upscaler for any X-Window (X11 or XWayland) on GNU/Linux. It uses [CuNNy](https://github.com/funnyplanter/CuNNy) neural networks to perform 2x (or 4x) upscaling to full screen while preserving aspect ratio. Mouse clicks and motion are automatically forwarded to the original window.

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/6f3f1c70b54e705665d2039d549afc0e4a8380b2/docs/gui/screenshots/dark_02.png)

## Results at 400% magnification

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/6f3f1c70b54e705665d2039d549afc0e4a8380b2/docs/comparisons/gurikaji/w40-60_h20-50_4x_comparison.png)

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/6f3f1c70b54e705665d2039d549afc0e4a8380b2/docs/comparisons/fatamoru/w30-50_h10-50_4x_comparison.png)

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/6f3f1c70b54e705665d2039d549afc0e4a8380b2/docs/comparisons/konosora/w10-30_h20-50_4x_comparison.png)

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/6f3f1c70b54e705665d2039d549afc0e4a8380b2/docs/comparisons/diagram/w40-70_h40-90_4x_comparison.png)

## Features

- **Neural-Network upscaling** using SRCNNs trained for high-quality upscaling of visual novels and illustrations.
- **Model selection** from 9 variants with variable quality/performance trade-offs.
- **Hardware accelerated** using Vulkan compute.
- **Tile-Based processing** that upscales only the frame regions that change, reducing GPU load for mostly static content.
- **Customizable output geometry**: scaling mode (fit, stretch, cover), offset, crop and zoom.
- **Input forwarding** as if interacting directly with the original window.

## Requirements

- GNU/Linux (X11 or Wayland with XWayland)
- Vulkan-capable GPU (NVIDIA, AMD, Intel)
- Python 3.10 or newer
- Qt XCB plugin (`libxcb-cursor0` / `xcb-util-cursor`)

> [!IMPORTANT]
>
> **Qt XCB plugin**
>
> This library is not installed by default on most desktop environments.
>
> <details>
> <summary>Install instructions (click to expand)</summary>
>
> #### Debian / Ubuntu / Linux Mint
>
> ```sh
> sudo apt install libxcb-cursor0
> ```
>
> #### Fedora / RHEL / CentOS
>
> ```sh
> sudo dnf install xcb-util-cursor
> ```
>
> #### Arch Linux / CachyOS
>
> ```sh
> sudo pacman -S xcb-util-cursor
> ```
>
> #### openSUSE
>
> ```sh
> sudo zypper install libxcb-cursor0
> ```
>
> </details>

## Installation

### Install with pipx (recommended)

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

### Optional: Desktop integration

After installing, you can add a desktop entry so the GUI appears in your application menu:

```sh
curl -fsSL https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/refs/heads/main/scripts/desktop_integration.sh \
    -o /tmp/desktop_integration.sh
less /tmp/desktop_integration.sh  # always review scripts before running them
sh /tmp/desktop_integration.sh
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

| Shortcut                            | Action                                      |
| ----------------------------------- | --------------------------------------------|
| `Alt`+`Shift`+`S`                   | Pause upscaling                             |
| `Alt`+`Shift`+`Escape`              | Exit upscaling                              |
| `Alt`+`Shift`+`P`                   | Take a lossless screenshot                  |
| `Alt`+`Shift`+`M`                   | Switch to the next model                    |
| `Alt`+`Shift`+`G`                   | Cycle output geometry (fit, stretch, cover) |
| `Alt`+`Shift`+`+` / `-`             | Zoom in / Zoom out                          |
| `Alt`+`Shift`+`↑` / `↓` / `←` / `→` | Pan the upscaled content                    |

All hotkeys can be customised in the configuration file.

### Profiles

You can define named configuration profiles in your YAML config file. Profiles let you quickly switch settings for different games or applications without typing long command lines each time.

Create a config file (e.g., `~/.config/linux-rt-upscaler/config.yaml`) and add a top-level `profiles` key. Each profile is a dictionary with an optional `match` section and an `options` section.

If no profile is selected manually, the program checks all profiles that have a `match` section against the title of the target window. If a profile matches (any match criterion is sufficient), its options are applied automatically.

```yaml
# General defaults (lowest priority)
model: 3x12
double_upscale: true

# Profiles that override if matched
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

1. Selects a window using X11 to find the target window by PID or WM_CLASS.
2. Captures the window's pixels using XShm and XDamage.
3. Upscales with SRCNN compute shaders to a 2x (or 4x) larger image.
4. Scales with a Lanczos2 shader to fill the monitor.
5. Renders in a overlay window that bypasses the window manager (so it always stays on top).
6. Forwards mouse events to the original window.

## Future Plans

- [ ] Addition of more SRCNN models ([FSRCNNX](https://github.com/igv/FSRCNN-TensorFlow/releases/tag/1.1) planned).
- [ ] ~~Native Wayland support~~ (**on hold**: Wayland capture is deeply compositor-specific and currently doesn’t align with the XShm/XDamage pipeline.)

## Known Issues

### Mouse forwarding may not work with Wine, Proton <10 and other applications

Synthetic mouse events (clicks, motion, wheel) sent by the overlay are ignored by:

- Wine and Proton versions older than 10.0 (GE-Proton10 + UMU works).
- Some native applications like Firefox.

For more details, see [issue #7](https://github.com/baronsmv/linux-rt-upscaler/issues/7).

## Acknowledgments

This project stands on the shoulders of several open-source works, mantained by amazing people:

- **[L65536](https://github.com/L65536)**, for the original [RealTimeSuperResolutionScreenUpscalerforLinux](https://github.com/L65536/RealTimeSuperResolutionScreenUpscalerforLinux), which demonstrated the feasibility of real-time SRCNN upscaling on Linux and served as a proof-of-concept for this project.
- **[funnyplanter](https://github.com/funnyplanter)**, for the incredible [CuNNy](https://github.com/funnyplanter/CuNNy) neural network upscaling models.
- **[Compushady](https://github.com/rdeioris/compushady)**, which served as an invaluable foundation during early development.
- **[PySide6](https://pypi.org/project/PySide6/)**, the Qt binding that powers the entire graphical interface and overlay window.
- **[xcffib](https://github.com/tych0/xcffib)**, the low‑level XCB binding used for all window management and event forwarding.
- **[screeninfo](https://github.com/rr-/screeninfo)**, used for automatic scale factor detection in Wayland.
- **[psutil](https://github.com/giampaolo/psutil)**, used to locate the target window PID.
- **[Pillow](https://python-pillow.github.io/)**, used for saving screenshots and rendering OSD messages.
