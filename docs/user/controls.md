# Controls

## Hotkeys

While upscaling a window, you can use hotkeys to change the behavior of the upscaler, to take a screenshot or to exit.

| Shortcut                            | Action                                      |
| ----------------------------------- | --------------------------------------------|
| `Alt`+`Shift`+`S`                   | Pause / resume upscaling                    |
| `Alt`+`Shift`+`Escape`              | Exit the upscaler                           |
| `Alt`+`Shift`+`P`                   | Take a lossless screenshot                  |
| `Alt`+`Shift`+`M`                   | Switch to the next upscaling model          |
| `Alt`+`Shift`+`G`                   | Cycle output geometry (fit, stretch, cover) |
| `Alt`+`Shift`+`+` / `-`             | Zoom in / zoom out                          |
| `Alt`+`Shift`+`↑` / `↓` / `←` / `→` | Pan the upscaled content                    |

### Customizing hotkeys

Hotkeys can be modified in the [configuration file](configuration.md/#yaml-configuration-file) (`~/.config/linux-rt-upscaler/config.yaml`) under the `hotkeys` key.

By default, they are defined like this:

```yaml
hotkeys:
  toggle_scaling: "Alt+Shift+S"
  exit_app: "Alt+Shift+Escape"
  screenshot: "Alt+Shift+P"
  cycle_model: "Alt+Shift+M"
  cycle_geometry: "Alt+Shift+G"
  zoom_in: "Alt+Shift+Plus"
  zoom_out: "Alt+Shift+Minus"
  offset_up: "Alt+Shift+Up"
  offset_down: "Alt+Shift+Down"
  offset_left: "Alt+Shift+Left"
  offset_right: "Alt+Shift+Right"
```

To modify them, keep in mind this:

- Supported modifiers are `Ctrl`, `Alt`, `Shift`, `Super` (Windows key).
- Key names are case-insensitive and follow common X11 keysyms names (for example `A`, `Space`, `Return`, `Escape`, `Left`, `Right`, `Up`, `Down`, `Plus`, `Minus`).

!!! note "If using embedded API"

    If you are [embedding the upscaler in a Python application](../api/overview.md/#embedded-mode), you may want to disable or modify these hotkeys to avoid conflicts with your own shortcuts. To disable them, set `enable_hotkeys=False` when creating the `UpscalerSession`.
