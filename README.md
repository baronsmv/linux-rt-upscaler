<p align="center">
  <img src="https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/data/icons/hicolor/scalable/apps/io.github.baronsmv.linux-rt-upscaler.svg" width="128" alt="icon">
</p>

<h1 align="center">Real-Time Upscaler for Linux</h1>

<p align="center">
  <a href="https://pypi.org/project/linux-rt-upscaler/"><img src="https://img.shields.io/pypi/v/linux-rt-upscaler.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/linux-rt-upscaler/"><img src="https://img.shields.io/pypi/pyversions/linux-rt-upscaler.svg" alt="Python versions"></a>
  <a href="https://www.gnu.org/licenses/gpl-3.0"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPLv3"></a>
</p>

A real-time SRCNN upscaler for any X-Window (X11 or XWayland) on GNU/Linux. It uses [CuNNy](https://github.com/funnyplanter/CuNNy) neural networks to perform 2x (or 4x) upscaling to full screen while preserving aspect ratio. Mouse clicks and motion are automatically forwarded to the original window.

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/docs/assets/screenshots/dark_02.png)

## Results at 400% magnification

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/docs/assets/comparisons/gurikaji/w40-60_h20-50_4x_comparison.png)

![](https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/main/docs/assets/comparisons/fatamoru/w30-50_h10-50_4x_comparison.png)

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
- Qt dependencies (see [Dependencies](https://baronsmv.github.io/linux-rt-upscaler/user/installation/#dependencies)).

## Installation

```sh
pipx install linux-rt-upscaler
```

For detailed installation instructions, including how to install `pipx`, see the [Installation Guide](https://baronsmv.github.io/linux-rt-upscaler/user/installation/).

After installation, the `upscale` and `upscale-gui` commands will be available globally. You can also create a [desktop entry](https://baronsmv.github.io/linux-rt-upscaler/user/installation/#desktop-integration-optional) of the GUI for easy access. 

## Guides and Docs

- [Home](https://baronsmv.github.io/linux-rt-upscaler/)
- [Installation](https://baronsmv.github.io/linux-rt-upscaler/user/installation/)
- [GUI Usage](https://baronsmv.github.io/linux-rt-upscaler/user/gui/)
- [CLI Options](https://baronsmv.github.io/linux-rt-upscaler/user/cli/)
- [Controls](https://baronsmv.github.io/linux-rt-upscaler/user/controls/)
- [Configuration](https://baronsmv.github.io/linux-rt-upscaler/user/configuration/)
- [API Reference](https://baronsmv.github.io/linux-rt-upscaler/api/overview/)

## Roadmap

- [ ] Translation infrastructure and community-contributed translations
- [ ] GUI Profiles operations (drag & drop, duplicate)
- [ ] GUI System Tray
- [ ] Complete GUI Style settings (font size, spacing, etc.)
- [ ] More SRCNN models ([FSRCNNX](https://github.com/igv/FSRCNN-TensorFlow/releases/tag/1.1) planned)
- [ ] Native Wayland capture prototype

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
- **[Compushady](https://github.com/rdeioris/compushady)**, which served as an invaluable Vulkan foundation during early development.
- **[PySide6](https://pypi.org/project/PySide6/)**, the Qt binding that powers the entire graphical interface and overlay window.
- **[xcffib](https://github.com/tych0/xcffib)**, the XCB binding used for window management, monitor querying and event forwarding.
- **[Pillow](https://python-pillow.github.io/)**, the Python Imaging Library, used for saving screenshots and rendering OSD messages.
- **[PyYAML](https://github.com/yaml/pyyaml)**, the YAML parser used for configuration file operations.
