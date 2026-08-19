# Installation

!!! warning "Dependency needed for the GUI"

    The [GUI](gui.md) used by the upscaler depends on Qt, which often requires a library that is not installed by default on most desktop environments. Make sure it's installed.

    <details>
    <summary>Install instructions for Qt XCB plugin (click to expand)</summary>

    **Debian / Ubuntu / Linux Mint**

    ```sh
    sudo apt update
    sudo apt install libxcb-cursor0
    ```

    **Fedora / RHEL / CentOS**

    ```sh
    sudo dnf install xcb-util-cursor
    ```

    **Arch Linux / CachyOS**

    ```sh
    sudo pacman -S xcb-util-cursor
    ```

    **openSUSE**
    
    ```sh
    sudo zypper install libxcb-cursor0
    ```

    </details>

## Installation methods

### Install with pipx (recommended)

```bash
pipx install linux-rt-upscaler
```

And that's it! ⭐

### Install from source

!!! note "Source compilation dependencies"

    At build time, the upscaler compiles a couple of C/C++ extensions, which require some dependencies, listed below.

    <details>
    <summary>Required development packages (click to expand)</summary>
    
    **Debian / Ubuntu / Linux Mint**
    
    ```sh
    sudo apt update
    sudo apt install gcc make libvulkan-dev libx11-dev libxcb1-dev libx11-xcb-dev \
        libxext-dev libxdamage-dev libxfixes-dev
    ```
    
    **Fedora / RHEL / CentOS**
    
    ```sh
    sudo dnf install gcc make vulkan-loader-devel libX11-devel libxcb-devel libX11-xcb-devel \
        libXext-devel libXdamage-devel libXfixes-devel
    ```
    
    **Arch Linux / CachyOS**
    
    ```sh
    sudo pacman -S base-devel vulkan-devel libx11 libxcb libxext libxdamage libxfixes
    ```
    
    **openSUSE**
    
    ```sh
    sudo zypper install gcc make vulkan-devel libX11-devel libxcb-devel libX11-xcb-devel \
        libXext-devel libXdamage-devel libXfixes-devel
    ```
    
    </details>

```sh
git clone https://github.com/baronsmv/linux-rt-upscaler.git
cd linux-rt-upscaler

# build in local env
pip install -e .

# or inside a uv virtual env:
uv venv && uv pip install -e . 
```

## Desktop integration (optional)

After installing, you can add a desktop entry so the [GUI](gui.md) appears in your application menu:

```sh
curl -fsSL https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/refs/heads/main/scripts/desktop_integration.sh \
    -o /tmp/desktop_integration.sh
less /tmp/desktop_integration.sh  # always review scripts before running them
sh /tmp/desktop_integration.sh
```

## What to read next

- Learn the basics of the [Graphical User Interface (GUI)](gui.md).
- If launching from terminal, see some of the options of the [Command-Line Interface (CLI)](cli.md).
- Read more about the YAML configuration file in [Configuration](configuration.md).
