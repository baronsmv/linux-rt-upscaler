# Graphical User Interface (GUI)

## Starting

You can start the GUI running `upscale-gui` from the terminal or using the [desktop entry](installation.md#desktop-integration-optional).

## Layout

The main window is split into three panels:

| Panel             | Content                                                                               |
| ----------------- | ------------------------------------------------------------------------------------- |
| **Left sidebar**  | List of profiles (including a global entry) with a toolbar at the bottom for editing. |
| **Central grid**  | Live thumbnails of all open, valid windows. Click one to upscale it.                  |
| **Right sidebar** | Tabbed settings panels that control how the upscaler behaves once working.            |

### Central Grid: Window Previews

The central grid shows the windows that the upscaler can capture.

!!! note "If a window doesn't appear"

    The grid updates periodically (every 2 seconds). If you can't see a window which should be valid, make sure it's not minimized.

Here you can:

- Type in the bar at the top to **filter** by window title.
- You can also navigate through it using `Ctrl`+`F` to focus the filter bar, then `↓` to move focus to the grid and any other arrow key to navigate through the thumbnails.
- Finally, click or press `Enter`/`Space` on a selected tile to start upscaling that window.
- And... That's it! Superresolution magic (hopefully)! ✨✨✨

!!! note "Closing the upscale overlay"

    Once upscaling, you can use the Close hotkey `Alt`+`Shift`+`Escape` to stop upscaling and close the app.

    For more info on hotkeys, see [Controls](controls.md#hotkeys).

### Right Sidebar: Settings

#### Settings tabs

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

#### Relevant settings

Three of these settings deserve a look:

- **Model** defines the SRCNN model to use, ordered from the fastest (but worst quality) `veryfast` to the slowest (but superior) `8x32`. Each model upscales to 2x, differing in resource usage. Depending on your system and the window to upscale, you may want to test each to find the best tradeoff for you.

    !!! note "Testing SRCNN models"

        - You can cycle through all the models using the hotkey `Alt`+`Shift`+`M`.
        - The upscaler uses a tile-based processing, actively processing only the tiles (sections of the frame) that change. Static or mostly static frames therefore consume less GPU power than dynamic ones. Use a window with changing frames when evaluating models.
        - If you want to measure performance, consider using a tool like [MangoHUD](https://github.com/flightlessmango/MangoHud). 

- **Double upscaling** applies two consecutive 2x upscaling passes, with a total of 4x. This increases GPU usage and could lead to slower frames, so keep that in mind.
- **Daemon Mode**, that enables automatic upscaling ([see below](#daemon-mode)).

#### Saving settings, or reverting them

Once you've changed any settings to your liking, you can save or revert them with the buttons at the bottom:

- **Save**: Writes the current configuration to the YAML configuration file in `~/.config/linux-rt-upscaler/config.yaml`.
- **Reset**: Reverts all unsaved changes back to the last saved state. The button also has a dropdown menu with additional actions:
    - If a profile is active: "Clear profile overrides" removes all options from that profile, falling back to global settings.
    - If global settings are active: "Restore system defaults" resets every option to the factory defaults.

!!! note "About the YAML configuration file"

    - For operations like duplicating a profile, editing the file with a text editor may be easier.
    - The upscaler keeps backups of this file, but if the data is important to you, consider keeping your own backups.
    - Changes to the GUI style are saved to `~/.config/linux-rt-upscaler/config-gui.yaml`, independently of the upscaler settings.
    - For more info, see [Configuration](configuration.md#yaml-configuration-file).

### Left Sidebar: Profiles

!!! tip "Why use profiles"

    When upscaling a variety of windows, you may want to use different settings for each scenario. For example, while an 800x600 window would need double upscaling to reach a 4k output, a 1080p one doesn't need the extra upscaling.

    For this reason, the upscaler supports configuration profiles that let you define specific settings for each window or setup. They contain **settings overrides** that change how the upscaler behaves for matching windows.

    For more info on profiles, see [Configuration](configuration.md#profiles).

#### Profile list and toolbar

The profile list shows **Global** (applies to all windows) followed by your custom profiles.

The toolbar at the button contains buttons that let you:

- **Add** a new profile (`Ctrl`+`N`).
- **Edit** an existing profile (`Enter`, `F2` or double-click).
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

    - Selecting a profile (clicking it or navigating to it with arrow keys) activates it, and the right sidebar switches to editing that profile's overrides.
    - Instead, if the **Global** entry is active (no custom profile selected), the settings sidebar edits the base configuration that every window uses unless a profile overrides it.

#### Applying a profile

Profiles are applied:

- **Manually** by clicking a profile in the list. Any window selected in the grid will use the manually selected profile.
- **Automatically** when selecting a window thumbnail if all the match rules are satisfied.
- With the **Daemon mode** ([see below](#daemon-mode)), if a match is found, the daemon switches to that window and applies the profile's options.

## Daemon Mode

When **Daemon Mode** is enabled (found in the General tab), a background process continuously looks for windows that match any of your profiles. As soon as a match appears, the daemon:

1. Focus the matched window.
2. Starts upscaling with the profile's settings.
3. If the window closes, the daemon goes back to scanning for the next match.

Daemon mode is ideal if you want to automatically upscale a profiled window as soon as it launches, or if your mouse died from exhaustion after a long day of multi-clicking~.