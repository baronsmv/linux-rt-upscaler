# Graphical User Interface (GUI)

## Layout

The main window is split into three panels:

| Panel             | Content                                                                               |
| ----------------- | ------------------------------------------------------------------------------------- |
| **Left sidebar**  | List of profiles (including a global entry) with a toolbar at the bottom for editing. |
| **Central grid**  | Live thumbnails of all open, valid windows. Click one to upscale it.                  |
| **Right sidebar** | Tabbed settings panels that control how the upscaler behaves once working.            |

### Central Grid: Window Previews

First, the windows that the upscaler can capture.

!!! note "A window doesn't appear"

    - The grid updates periodically (every 2 seconds).
    - If you can't see a window which should be valid, verify it's not minimized.

Here you can:

- Type in the bar at the top to filter by window title.
- You can also use `Ctrl+F` to focus the filter bar, then `↓` to move focus to the grid and any other arrow key to navigate through the thumbnails.
- Finally, click or press `Enter`/`Space` on a selected tile to start upscaling that window.
- And... That's it! Superresolution magic (hopefully)! ✨✨✨

### Right Sidebar: Settings

To customize the upscaling (or the app itself) you can change the settings at the right sidebar, organized into these tabs:

| Tab              | Configuration options                                                     |
| ---------------- |---------------------------------------------------------------------------|
| **General**      | Model, Double upscale, Focus tracking, Daemon mode                        |
| **Scaling**      | Spatial upsampler / downsampler                                           |
| **Display**      | Monitor, GPU, V-Sync, FPS limit, Wayland scale factor                     |
| **Presentation** | Overlay, Geometry, Cursor Hiding, Crop, Offset, Background color          |
| **Effects**      | Debanding, CAS sharpening, Bloom, Vignette, Film grain, LUT color grading |
| **Advanced**     | Vulkan, Tile processing, Timing, Error recovery                           |
| **Extras**       | Screenshot directory and template, On-Screen Display                      |
| **GUI Style**    | GUI color scheme and style                                                |

After changing any settings to your liking, you can either save them or revert them with the buttons at the bottom:

- `Save`: Writes the current configuration to `~/.config/linux-rt-upscaler/config.yaml`.
  - For changes to the GUI style it saves the changes to `~/.config/linux-rt-upscaler/config-gui.yaml`.
- `Reset`: Reverts all unsaved changes back to the last saved state. The button also has a dropdown menu:
  - If a profile is active: "Clear profile overrides" removes all options from that profile, falling back to global settings.
  - If global settings are active: "Restore system defaults" resets every option to the factory defaults.

### Left Sidebar: Profiles

!!! tip "Why use profiles"

    When upscaling a variety of windows, you may want to use different settings for each scenario.

    For example, while an 800x600 window would need double upscaling (two 2x passes = 4x total) to reach a 4k output, a 1080p one doesn't need the extra upscaling. For this reason, the upscaler supports profiles.

    Profiles let you define specific settings for each window or setup. They contain **settings overrides** that change how the upscaler behaves for matching windows.

    For more info on profiles, see [Configuration](configuration.md).

#### Profile list and toolbar

The profile list shows **Global** (applies to all windows) followed by your custom profiles.

The toolbar at the button contains buttons that let you:

- **Add** a new profile (`Ctrl`+`N`).
- **Edit** an existing profile (`Enter`/`F2` or double-click).
- **Delete** a profile (`Del`).
- **Reorder** with up/down arrows (`Ctrl`+`Shift`+`↑`/`↓`).

#### Creating a profile

1. Click the `+` button in the profile toolbar (or press `Ctrl`+`N`).
2. A dialog opens where you can:
   - Name the profile.
   - Optionally, set an icon from an open window or from a file.
   - Optionally, define any rules that the window needs to satisfy to automatically match.
3. After creating it, the profile appears in the left list, where it can be selected and edited.

!!! note "Selecting a profile"

    Selecting a profile (clicking it or navigating to it with arrow keys) activates it, and the right sidebar switches to editing that profile’s overrides.

    Instead, if the **Global** entry is active (no custom profile selected), the settings sidebar edits the base configuration that every window uses unless a profile overrides it.

#### Applying a profile

Profiles are applied:

- **Manually** by clicking a profile in the list. Any window upscaled that doesn't match a profile will use the manually selected profile.
- **Automatically** when selecting a window thumbnail if all the match rules are satisfied.
- With the **Daemon mode** (see below), if a match is found, the daemon switches to that window and applies the profile’s options.

## Daemon Mode

When **Daemon Mode** is enabled (found in the General tab), a background process continuously looks for windows that match any of your profiles. As soon as a match appears, the daemon:

1. Focus the matched window.
2. Starts upscaling with the profile’s settings.
3. If the window closes, the daemon goes back to scanning for the next match.

Daemon mode is ideal if you want to automatically upscaling a profiled window as soon as it launches.