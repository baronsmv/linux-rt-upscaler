# Installation

## Dependencies

The GUI depends on Qt, which often requires a library that is not installed by default on most desktop environments. Install it with:

=== "Debian / Ubuntu / Linux Mint"

    ```sh
    sudo apt update && sudo apt install libxcb-cursor0
    ```

=== "Fedora / RHEL / CentOS"

    ```sh
    sudo dnf install xcb-util-cursor
    ```

=== "Arch Linux / CachyOS"

    ```sh
    sudo pacman -S xcb-util-cursor
    ```

=== "openSUSE"

    ```sh
    sudo zypper install libxcb-cursor0
    ```

## Installation methods

### Install with pipx (recommended)

If you don't have pipx installed, install it first:

=== "Debian / Ubuntu / Linux Mint"

    ```sh
    sudo apt update && sudo apt install pipx
    pipx ensurepath
    ```

=== "Fedora / RHEL / CentOS"

    ```sh
    sudo dnf install pipx
    pipx ensurepath
    ```

=== "Arch Linux / CachyOS"

    ```sh
    sudo pacman -S python-pipx
    pipx ensurepath
    ```

=== "openSUSE"

    ```sh
    sudo zypper install python-pipx
    pipx ensurepath
    ```

Then install the upscaler:

```bash
pipx install linux-rt-upscaler
```

And that's it! ⭐

### Install from source

Building from source requires C/C++ compilation tools and development packages. Install them with:

=== "Debian / Ubuntu / Linux Mint"

    ```sh
    sudo apt update && sudo apt install gcc make libvulkan-dev libx11-dev libxcb1-dev \
        libx11-xcb-dev libxext-dev libxdamage-dev libxfixes-dev
    ```

=== "Fedora / RHEL / CentOS"

    ```sh
    sudo dnf install gcc make vulkan-loader-devel libX11-devel libxcb-devel libX11-xcb-devel \
        libXext-devel libXdamage-devel libXfixes-devel
    ```

=== "Arch Linux / CachyOS"

    ```sh
    sudo pacman -S base-devel vulkan-devel libx11 libxcb libxext libxdamage libxfixes
    ```

=== "openSUSE"

    ```sh
    sudo zypper install gcc make vulkan-devel libX11-devel libxcb-devel libX11-xcb-devel \
        libXext-devel libXdamage-devel libXfixes-devel
    ```

Then clone and install:

```sh
git clone https://github.com/baronsmv/linux-rt-upscaler.git
cd linux-rt-upscaler

# build in local env:
pip install -e .

# or better, inside a uv virtual env:
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
- Check out the hotkeys you can use while upscaling in [Controls](controls.md).
- Read about the configuration options in [Configuration](configuration.md).
