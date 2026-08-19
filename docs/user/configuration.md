# Configuration

## YAML configuration file

To avoid typing long command lines each time you want to upscale a window, the upscaler interfaces (both CLI and GUI) share a YAML configuration file located in `~/.config/linux-rt-upscaler/config.yaml`, which contains user-defined options that apply to all windows, or to some specifically (per-profile, see below).

An example of that file:

```yaml
# Options that apply to all windows, unless overriden by a profile or a CLI option
model: 8x32
double_upscale: true

# Profiles that override options for specific windows or setups
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

- 8x32 model and 4x upscaling will be the default options for any window.
- If the window size is that of a Full HD one (1920×1080) or larger, it will instead use 4x24 model and 2x upscaling.

## Profiles

Profiles allow you to automatically (or manually) apply a specific set of options when a matching window is detected.

Profiles are useful if you need a specific behavior depending on the properties of a window. For example, a window may need to be cropped, upscaled with a different upscaling model, or have a special effect.

A profile can include:

- **Match criteria**: window title (exact, contains, regex) and width/height interval expressions.
- **Options overrides**: any option changed from the right sidebar (e.g., model, crop, effects). Note: GUI Style options are the only ones not saved per-profile.
