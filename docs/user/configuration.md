# Configuration

## YAML configuration file

To persist any custom settings, both CLI and GUI interfaces share a YAML configuration file located in `~/.config/linux-rt-upscaler/config.yaml`.

The configuration file stores your custom settings and profiles. You only need to include options that differ from the built-in defaults, missing values fall back automatically.

You can also specify a different file with the `--config <path>` option.

### Settings precedence

Settings are merged in this order, from lowest to highest priority:

1. Built-in defaults.
2. Top-level options in `config.yaml`.
3. Profile options, when a profile matches or is selected manually.
4. Command-line arguments (e.g. `--model 4x24`).

In other words, a profile can override a top-level option, and a CLI argument can override both.

### Example

```yaml
# Options that apply to all windows (top-level, priority 2)
model: 8x32
double_upscale: true

# Profiles that override options for specific windows or setups (priority 3)
profiles:
  Full HD (1920×1080):
    match:
      width: <=1920
      height: <=1080
    options:
      model: 4x24
      double_upscale: false
```

With this configuration:

- Most windows use `8x32` and 4x upscaling (top-level options).
- Windows up to 1920x1080 (matching the profile) use `4x24` and 2x upscaling (profile options override top-level ones).

!!! note "Config references"

    - This extensive [configuration file example](https://github.com/baronsmv/linux-rt-upscaler/blob/main/config-example.yaml) details each possible option, along with profile examples.
    - For more details on the `Config` dataclass parsed from the configuration file, see the [Config API page](../api/classes/config.md).

## Profiles

Profiles allow you to define settings for specific windows or setups, matching their properties. They are defined at the `profiles` top-level option of the configuration file.

### Match rules

A profile in the configuration file may contain a `match` section with one or more of these keys:

| Key                | Description                                       |
| ------------------ |---------------------------------------------------|
| `title`            | Exact window title match (case-insensitive).      |
| `title_contains`   | Substring match in the title (case-insensitive).  |
| `title_startswith` | Title begins with this string (case-insensitive). |
| `title_endswith`   | Title ends with this string (case-insensitive).   |
| `title_regex`      | Regular expression match (case-insensitive).      |
| `width`            | Window width interval.                            |
| `height`           | Window height interval.                           |

For a window to match a profile, all rules in its `match` block must be satisfied (AND logic). If a window matches, and the profile has an `options` block, then all of those options are applied.

Profiles are checked top-to-bottom: if multiple profiles would match a window, only the first one will match.

Width and height rules accept the following interval syntax:

- Exact values: `1920`
- Comparisons: `<1280`, `>1024`, `<=1366`, `>=1920`
- Ranges: `1280-1920`, `720..1080`, `1024,1366`

### Example

Here, profiles are used to get the best possible tradeoff between framerate and quality, depending on the resolution of the source window.

For instance, upscaling more pixels takes longer, so you might choose a faster model for higher resolutions.

```yaml
profiles:
  VGA (640×480):
    match:
      width: <=640
      height: <=480
    options:
      model: 4x24
      double_upscale: true
  SVGA (800×600):
    match:
      width: <=800
      height: <=600
    options:
      model: 4x24
      double_upscale: true
  XGA (1024×768):
    match:
      width: <=1024
      height: <=768
    options:
      model: 4x16
      double_upscale: true
  HD (1280×720):
    match:
      width: <=1280
      height: <=720
    options:
      model: 4x16
      double_upscale: true
  Full HD (1920×1080):
    match:
      width: <=1920
      height: <=1080
    options:
      model: 4x24
      double_upscale: false
  QHD (2560×1440):
    match:
      width: <=2560
      height: <=1440
    options:
      model: 4x16
      double_upscale: false
```

## Overlay

### Overlay mode

The overlay is the Qt window that displays the upscaled result on top of the target window. It supports these modes:

| Mode               | Description                                                                                                                                                                                                  |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `always-on-top`    | Floating, borderless overlay that stays above all other windows **without taking focus**. Mouse events are forwarded to the target window. This is the default mode.                                         |
| `top-transparent`  | Same as `always-on-top`, but click-through. Mouse events pass through the overlay to the window underneath, and the overlay gets semi-transparent when the mouse isn't inside the source window coordinates. |
| `fullscreen`       | Frameless fullscreen window covering the entire monitor (or most of it, depending on the Window Manager).                                                                                                    |
| `windowed`         | Normal window with decorations and a fixed size.                                                                                                                                                             |

!!! note "Keyboard events"

    **Keyboard events are never forwarded**, regardless of overlay mode.

    If you need to use the keyboard (or any other peripheral input besides the mouse) in the target application, keep its window always focused. On a single monitor, `always-on-top` works well for this since the overlay cannot be focused, keeping the focus on the target window instead.
