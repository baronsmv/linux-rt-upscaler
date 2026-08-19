# Installation

## Some installation methods

### Install with pipx (recommended)

```bash
pipx install linux-rt-upscaler
```

### Install from source

<details>
<summary>Required development packages (click to expand)</summary>

Debian / Ubuntu / Linux Mint

```sh
sudo apt update
sudo apt install gcc make libvulkan-dev libx11-dev libxcb1-dev libx11-xcb-dev \
    libxext-dev libxdamage-dev libxfixes-dev
```

Fedora / RHEL / CentOS

```sh
sudo dnf install gcc make vulkan-loader-devel libX11-devel libxcb-devel libX11-xcb-devel \
    libXext-devel libXdamage-devel libXfixes-devel
```

Arch Linux / CachyOS

```sh
sudo pacman -S base-devel vulkan-devel libx11 libxcb libxext libxdamage libxfixes
```

openSUSE

```sh
sudo zypper install gcc make vulkan-devel libX11-devel libxcb-devel libX11-xcb-devel \
    libXext-devel libXdamage-devel libXfixes-devel
```

</details>

```sh
git clone https://github.com/baronsmv/linux-rt-upscaler.git
cd linux-rt-upscaler

pip install -e .
# or inside a uv virtual env:
uv venv
uv pip install -e . 
```

## Desktop integration (optional)

After installing, you can add a desktop entry so the [GUI](gui.md) appears in your application menu:

```sh
curl -fsSL https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/refs/heads/main/scripts/desktop_integration.sh \
    -o /tmp/desktop_integration.sh
less /tmp/desktop_integration.sh  # always review scripts before running them
sh /tmp/desktop_integration.sh
```