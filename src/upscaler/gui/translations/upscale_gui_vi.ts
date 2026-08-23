<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="vi">
<context>
    <name>AboutDialog</name>
    <message>
        <location filename="../dialogs/about.py" line="95"/>
        <source>Real-Time Upscaler</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/about.py" line="101"/>
        <source>Version {0}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/about.py" line="109"/>
        <source>A real-time SRCNN upscaler for any X-Window on GNU/Linux.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/about.py" line="120"/>
        <source>Close</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AdvancedTab</name>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="26"/>
        <source>Advanced</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="33"/>
        <source>Vulkan Rendering</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="35"/>
        <source>Buffer Pool Size</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="45"/>
        <source>Number of pre-allocated staging buffers for partial texture updates.
Raise this if you notice stutters when many small regions change rapidly.
Recommended range: 2 - 16.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="49"/>
        <source>Frame Timeout (ms)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="59"/>
        <source>Maximum time (in milliseconds) to wait for the GPU to finish the previous frame.
Lower values reduce CPU blocking but may drop frames under heavy load.
Recommended range: 17 (1/60 s) - 1000 (1 s).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="64"/>
        <source>Tile-Based Processing</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="66"/>
        <source>Enable Tile Mode</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="74"/>
        <source>Divide the frame into tiles and only re-process the ones that have changed.
Ideal for mostly static content (e.g. text editors, visual novels).
When disabled, the whole frame is upscaled in one pass: better for video or rapid changes.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="78"/>
        <source>Damage Tracking</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="85"/>
        <source>Transfer only the changed regions of the frame to the GPU instead of the entire image.
Disable if you suspect missed updates from the compositor causing glitches.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="89"/>
        <source>Tile Size</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="100"/>
        <source>Interior size of each tile in pixels.
Smaller tiles track changes more precisely but add CPU overhead.
Multiples of 32 work best with GPU workgroups.
Recommended range: 32 - 128.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="104"/>
        <source>Context Margin</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="114"/>
        <source>Extra border pixels added around each tile to provide context for the neural network.
Larger margins improve boundary quality but increase processing.
Recommended range: 4 - 24.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="118"/>
        <source>Max Tiles per Frame</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="128"/>
        <source>Maximum number of dirty tiles processed per frame.
When exceeded, the pipeline falls back to full-frame processing to avoid excessive GPU dispatches.
Recommended range: 4 - 32.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="132"/>
        <source>Area Threshold %</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="144"/>
        <source>Fraction of the window area (in %) that, when dirty, forces a fallback to full-frame processing.
Smaller values fall back earlier, preventing too many tiny tile dispatches.
Recommended range: 15% - 50%.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="149"/>
        <source>Timing</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="151"/>
        <source>Daemon Poll (s)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="160"/>
        <source>How often the daemon scans for matching windows.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="164"/>
        <source>Focus Poll (s)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="173"/>
        <source>How often the focus monitor checks for active window changes.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="177"/>
        <source>Pipeline Idle (s)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="186"/>
        <source>How often the pipeline checks its internal state when idle.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="191"/>
        <source>Error Recovery</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="193"/>
        <source>Max Capture Failures</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="202"/>
        <source>Consecutive frame-grab failures before the pipeline stops.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="206"/>
        <source>Capture Failure Delay (s)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="214"/>
        <source>Pause after a capture failure before retrying.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="218"/>
        <source>Swapchain Debounce (s)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="227"/>
        <source>Minimum time between two Vulkan swapchain recreations.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorPickerRow</name>
    <message>
        <location filename="../sidebars/controls/color.py" line="98"/>
        <source>Choose Background Color</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>DisplayTab</name>
    <message>
        <location filename="../sidebars/tabs/display.py" line="34"/>
        <source>Auto (best)</source>
        <comment>GPU automatic device option</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="36"/>
        <source>Display</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="43"/>
        <source>Devices</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="45"/>
        <source>Monitor</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="53"/>
        <source>Monitor to cover: &apos;primary&apos;, &apos;all&apos; (multi-monitor), or a specific output name (e.g., &apos;HDMI-1&apos;).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="63"/>
        <source>GPU</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="74"/>
        <source>Vulkan GPU used for rendering. &apos;{0}&apos; selects the most powerful GPU found.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="79"/>
        <source>V-Sync</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="81"/>
        <source>Present Mode</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="92"/>
        <source>Vulkan presentation mode:
• fifo: VSync on, lowest power, no tearing
• mailbox: tear-free, lower latency, higher power
• immediate: no VSync, lowest latency, may tear</source>
        <extracomment>Do not translate &quot;fifo&quot;, &quot;mailbox&quot;, &quot;immediate&quot;: they are Vulkan presentation mode identifiers.</extracomment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="96"/>
        <source>Limit FPS</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="103"/>
        <source>Enable an upper frame-rate limit.
It&apos;s recommended to use &apos;mailbox&apos; presentation mode when limiting FPS.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="107"/>
        <source>Max FPS</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="117"/>
        <source>Target maximum frames per second.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="122"/>
        <source>Scale Factor</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="124"/>
        <source>Auto Scale</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="131"/>
        <source>Let the application automatically detect the correct scale factor based on the physical monitor resolution.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="135"/>
        <source>Scale Factor %</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="149"/>
        <source>Manual scale factor (e.g., 1.50 for 150% scaling). Only available when &apos;Auto Scale&apos; is disabled.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>EffectsTab</name>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="26"/>
        <source>Effects</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="33"/>
        <source>Debanding</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="35"/>
        <source>Enable Deband</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="42"/>
        <source>Smooth harsh color banding in gradients before upscaling. Helps skies, fog and smooth backgrounds.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="46"/>
        <location filename="../sidebars/tabs/effects.py" line="75"/>
        <location filename="../sidebars/tabs/effects.py" line="102"/>
        <location filename="../sidebars/tabs/effects.py" line="160"/>
        <location filename="../sidebars/tabs/effects.py" line="220"/>
        <source>Strength</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="56"/>
        <source>Debanding intensity (0 = off, 1 = maximum). Low values (0.1-0.3) are sufficient for most content.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="62"/>
        <source>CAS Sharpening</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="64"/>
        <source>Enable CAS</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="71"/>
        <source>Contrast Adaptive Sharpening: enhances text and line art without the halos of traditional unsharp masks.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="84"/>
        <source>Sharpening amount (0 = none, 1 = max). 0.2-0.5 gives pleasant crispness.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="90"/>
        <source>Bloom (Glow)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="92"/>
        <source>Enable Bloom</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="98"/>
        <source>Soft glow around bright areas, creating a cinematic look.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="112"/>
        <source>Bloom intensity (0 = off, 1 = max). Subtle values (0.02-0.06) add a gentle, polished look.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="118"/>
        <source>Threshold</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="128"/>
        <source>Brightness cutoff for bloom. Only pixels above this contribute. Lower values include more of the scene.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="134"/>
        <location filename="../sidebars/tabs/effects.py" line="176"/>
        <source>Radius</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="142"/>
        <source>Blur radius in pixels. Larger radii spread the glow further.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="148"/>
        <source>Vignette</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="150"/>
        <source>Enable Vignette</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="156"/>
        <source>Radial darkening of screen edges, drawing focus to the center.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="170"/>
        <source>Edge darkening intensity (0 = none, 1 = max). Moderate values (0.3-0.6) give a subtle framing effect.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="186"/>
        <source>Distance from center where darkening begins. Higher values keep the center bright longer.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="192"/>
        <source>Falloff</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="202"/>
        <source>Softness of the vignette transition. Low values = gentle, high values = sharp ring.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="208"/>
        <source>Film Grain</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="210"/>
        <source>Enable Grain</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="216"/>
        <source>Simulated film grain for a photochemical, organic look.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="230"/>
        <source>Grain intensity (0 = off, 1 = max). Low values (0.1-0.2) mimic fine photochemical grain.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="236"/>
        <source>Size</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="246"/>
        <source>Apparent particle size of the grain. Larger values produce coarser, more visible grain.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="252"/>
        <source>Color Grading (3D LUT)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="254"/>
        <source>Enable LUT</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="261"/>
        <source>Apply a cinematic color-lookup table for instant film-stock emulation or color grading.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="265"/>
        <source>Preset</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="272"/>
        <source>Built-in 3D LUT preset. Choose from warm, cool, film, sepia, etc.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="278"/>
        <source>Intensity</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="287"/>
        <source>Blend between original and graded image (0 = original, 1 = full effect).</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ExtrasTab</name>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="25"/>
        <source>Extras</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="32"/>
        <source>Screenshot Location</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="34"/>
        <source>Directory</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="38"/>
        <source>Folder where screenshots will be saved.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="41"/>
        <source>Template</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="54"/>
        <source>Filename template for screenshots. Available placeholders:
• {timestamp}: capture time (supports strftime, e.g. {timestamp:%Y-%m-%d-%H-%M-%S})
• {title}: current window title
• {profile}: active profile name (fallback to {{title}} if no profile)
• {model}: active upscaling model
• {width}: upscaled image width
• {height}: upscaled image height</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="59"/>
        <source>On-Screen Display</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="61"/>
        <source>Show OSD</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="68"/>
        <source>Show on-screen messages when model, geometry, or zoom changes, and after taking a screenshot.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="72"/>
        <source>Duration (s)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="81"/>
        <source>How many seconds OSD messages remain visible before fading out.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>FilterBar</name>
    <message>
        <location filename="../grid/filter.py" line="34"/>
        <source>Filter windows</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>GeneralTab</name>
    <message>
        <location filename="../sidebars/tabs/general.py" line="32"/>
        <source>General</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="39"/>
        <source>Upscaling Model</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="41"/>
        <source>Model</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="49"/>
        <source>Upscaling model to use. Models are ordered from worst to best quality. Larger numbers indicate deeper networks (slower, higher quality).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="53"/>
        <source>Double Upscale (4x)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="62"/>
        <source>Perform two consecutive 2x upscales for a 4x total (e.g., 720p to 2880p). Useful for high-resolution screens (4K) and low-resolution sources. Increases GPU usage.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="68"/>
        <source>Focus Tracking</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="70"/>
        <source>Follow Focus</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="77"/>
        <source>Automatically switch the upscaling target to the currently focused window. Useful when moving between multiple windows.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="81"/>
        <source>Pause on Focus Loss</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="88"/>
        <source>When the target window loses focus, hide the overlay until it regains focus. Uncheck to keep the overlay always visible.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="93"/>
        <source>Automatic Upscaling</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="96"/>
        <source>Exclude from Daemon Mode</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="101"/>
        <source>Exclude this profile from automatic upscaling.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="106"/>
        <source>Daemon Mode</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="115"/>
        <source>When enabled, a daemon process runs in the background and automatically upscales any window that matches a profile.
Disable this to manually pick a window from the grid.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../main.py" line="83"/>
        <source>Real-Time Upscaler</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../main.py" line="139"/>
        <source>About Real-Time Upscaler.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../main.py" line="337"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../main.py" line="338"/>
        <source>Could not start pipeline:
{0}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../main.py" line="457"/>
        <source>Could not save:
{0}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../main.py" line="456"/>
        <source>Save Error</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>PathPickerRow</name>
    <message>
        <location filename="../sidebars/controls/path.py" line="51"/>
        <source>Select directory</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/controls/path.py" line="61"/>
        <source>Browse for directory.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/controls/path.py" line="107"/>
        <source>Choose screenshot directory</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>PresentationTab</name>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="27"/>
        <source>Presentation</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="34"/>
        <source>Overlay</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="36"/>
        <source>Overlay Mode</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="48"/>
        <source>Overlay window behaviour:
• always-on-top: floating, cannot be focused (recommended)
• top-transparent: click-through (mouse passes to window below)
• fullscreen: covers entire monitor
• windowed: normal window with decorations</source>
        <extracomment>Do not translate &quot;always-on-top&quot;, &quot;top-transparent&quot;, &quot;fullscreen&quot;, &quot;windowed&quot;: they are internal overlay mode identifiers.</extracomment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="52"/>
        <source>Output Geometry</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="63"/>
        <source>How the upscaled content fits the overlay:
• fit: letterbox, preserves aspect ratio
• stretch: fill, aspect ratio may be distorted
• cover: fill and crop to fit</source>
        <extracomment>Do not translate &quot;fit&quot;, &quot;stretch&quot;, &quot;cover&quot;: they are internal output geometry identifiers.</extracomment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="68"/>
        <source>Cursor</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="70"/>
        <source>Hide cursor</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="76"/>
        <source>Automatically hide the mouse cursor after a period of inactivity.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="87"/>
        <source>Hide Timeout (s)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="95"/>
        <source>Time in seconds after which the cursor disappears.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="104"/>
        <source>Left</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="105"/>
        <source>Top</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="106"/>
        <source>Right</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="107"/>
        <source>Bottom</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="118"/>
        <source>Pixels to crop from the {0} border of the target window.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="123"/>
        <source>Offset</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="125"/>
        <source>X Offset</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="126"/>
        <source>Y Offset</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="139"/>
        <source>Horizontal offset from the centered position (positive = right, negative = left).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="145"/>
        <source>Vertical offset from the centered position (positive = down, negative = up).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="151"/>
        <source>Background Color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="155"/>
        <source>Color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="160"/>
        <source>Color of the letterbox bars. Supports transparency.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ProfileActions</name>
    <message>
        <location filename="../helpers/profiles.py" line="59"/>
        <source>Unsaved changes</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="62"/>
        <source>Save changes before switching profile?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="114"/>
        <location filename="../helpers/profiles.py" line="169"/>
        <location filename="../helpers/profiles.py" line="195"/>
        <location filename="../helpers/profiles.py" line="210"/>
        <location filename="../helpers/profiles.py" line="225"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="115"/>
        <source>Could not add profile.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="139"/>
        <source>Duplicate name</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="143"/>
        <source>A profile named &apos;{0}&apos; already exists.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="181"/>
        <source>Delete profile &apos;{0}&apos;?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="170"/>
        <source>Could not edit profile.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="178"/>
        <source>Delete profile</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="198"/>
        <source>Could not delete profile.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="213"/>
        <location filename="../helpers/profiles.py" line="228"/>
        <source>Could not reorder profiles.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ProfileDialog</name>
    <message>
        <location filename="../dialogs/profile.py" line="59"/>
        <source>Profile Editor</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="60"/>
        <source>New Profile</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="80"/>
        <source>Name</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="85"/>
        <source>Profile name</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="86"/>
        <source>A unique name for this profile. Required.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="92"/>
        <source>Icon</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="133"/>
        <source>Capture window</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="139"/>
        <source>Fill name, icon, and match rules from a window.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="147"/>
        <source>Capture icon from window</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="153"/>
        <source>Load icon from file</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="159"/>
        <source>Remove icon</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="165"/>
        <source>Match rules</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="179"/>
        <source>All filled rules must match for the profile to apply (AND logic).
Examples:
• Match any Firefox windows wider than 1280px:
    • Title (exact): Firefox
    • Width: &gt;1280
• Match any VLC window (regardless of its size):
    • Title contains: VLC
• Match emulator windows between 720px and 1080px tall:
    • Title (regex): (Yuzu|Ryujinx).*
    • Height: 720-1080</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="187"/>
        <source>Title (exact):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="188"/>
        <source>e.g., Steam</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="194"/>
        <source>Match if the window title exactly equals this text (case-insensitive).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="199"/>
        <source>Title contains:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="200"/>
        <source>e.g., VLC</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="205"/>
        <source>Match if the window title contains this text (case-insensitive).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="210"/>
        <source>Title (regex):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="211"/>
        <source>e.g., (Yuzu|Ryujinx).*</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="217"/>
        <source>Match if the window title matches this regular expression (case-insensitive).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="232"/>
        <source>Match if the window width satisfies this condition:
• Exact: 1920
• Comparison: &lt;800, &gt;1024, &lt;=1366, &gt;=1920
• Range: 1280-1920, 720..1080, 1024,1366</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="246"/>
        <source>Match if the window height satisfies this condition:
• Exact: 1080
• Comparison: &lt;600, &gt;900, &lt;=768, &gt;=1440
• Range: 480-1080, 600..900, 720,1024</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="258"/>
        <source>Profiles let you override settings for specific windows and setups.
A profile is applied automatically when the upscaled window matches all the rules defined here, or when manually selected before upscaling.
Profiles are checked top-to-bottom: the first match wins.
Leave a rule blank to ignore that property.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="366"/>
        <source>No icon</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="367"/>
        <source>The selected window has no icon.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="383"/>
        <source>Select Icon</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="390"/>
        <source>Invalid image</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="391"/>
        <source>Could not load the selected file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="419"/>
        <source>Missing name</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="420"/>
        <source>Profile name cannot be empty.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="428"/>
        <source>Duplicate name</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="431"/>
        <source>A profile named &apos;{0}&apos; already exists.
Please choose a different name.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ProfilesSidebar</name>
    <message>
        <location filename="../sidebars/profiles.py" line="133"/>
        <source>Add profile (Ctrl+N)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="139"/>
        <source>Edit match criteria (Enter/F2)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="146"/>
        <source>Delete profile (Del)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="154"/>
        <source>Move up (Ctrl+Shift+Up)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="161"/>
        <source>Move down (Ctrl+Shift+Down)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="265"/>
        <source>When selected, the settings panel on the right edits the global configuration.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="277"/>
        <source>Global settings apply to all windows.

Create a profile to override settings
for a specific window, matched by its
name or size.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="316"/>
        <source>When selected, the settings panel on the right edits the &apos;{0}&apos; profile overrides.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ScalingTab</name>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="32"/>
        <source>Scaling</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="39"/>
        <source>Sampler Algorithm</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="41"/>
        <source>Upsampler</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="51"/>
        <source>Applied after SRCNN upscaling to reach the target output size (e.g., 1440p → 4k).
• Fixed Lanczos-2 — sharp, linear-light, best for 2D art
• AMD FidelityFX Super Resolution 1.0 — fast, edge-adaptive, best for 3D content
• NVIDIA Image Scaling — directional sharpening, sRGB, may look oversharpened</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="55"/>
        <source>Downsampler</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="66"/>
        <source>Applied after SRCNN upscaling to reduce the image to the target output size (e.g., 1440p → 1080p).
• Catmull-Rom (bicubic) — sharper and faster than Lanczos for mild downscaling
• Adaptive Lanczos — variable radius, high quality even in extreme downscales</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="71"/>
        <source>Sampler Options</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="73"/>
        <source>Blur</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="84"/>
        <source>Kernel width (blur factor) for Lanczos and Catmull-Rom.
Lower values increase sharpness/ringing, while higher values smooth the result.
Recommended range: 0.8 - 1.2.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="88"/>
        <source>Antiring Strength</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="99"/>
        <source>Anti-ringing strength (0.0 - 1.0) for Adaptive Lanczos and Catmull-Rom.
Lower values soften the clamp, preserving more detail at the cost of possible ringing.
Recommended range: 0.7 - 1.0.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="104"/>
        <source>Lanczos Options</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="106"/>
        <source>Tight Antiring</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="114"/>
        <source>Use only the central 2x2 neighborhood for anti-ringing bounds.
Keeps thin text and line art sharp. Disable if you see distant ringing artifacts on high-contrast edges.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="118"/>
        <source>Override Lanczos Radius</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="125"/>
        <source>Force a specific Lanczos kernel radius instead of the automatic selection.
When unchecked, radius is chosen automatically (2 for upscaling, variable for downscaling).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="129"/>
        <source>Radius</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="142"/>
        <source>Lanczos kernel radius (2 = standard Lanczos2, 3 = sharper 6-tap, etc.).
Higher radii reduce aliasing but increase GPU load.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>SettingsSidebar</name>
    <message>
        <location filename="../sidebars/settings.py" line="76"/>
        <source>General</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="77"/>
        <source>Scaling</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="78"/>
        <source>Display</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="79"/>
        <source>Presentation</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="80"/>
        <source>Effects</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="81"/>
        <source>Advanced</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="82"/>
        <source>Extras</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="83"/>
        <source>GUI Style</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="188"/>
        <location filename="../sidebars/settings.py" line="294"/>
        <source>Save Profile</source>
        <comment>Save button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="190"/>
        <location filename="../sidebars/settings.py" line="296"/>
        <source>Save</source>
        <comment>Save button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="200"/>
        <location filename="../sidebars/settings.py" line="297"/>
        <source>Reset</source>
        <comment>Reset button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="212"/>
        <source>Clear profile overrides</source>
        <comment>Reset button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="214"/>
        <source>Restore system defaults</source>
        <comment>Reset button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="222"/>
        <source>Reset to last applied</source>
        <comment>Reset button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="225"/>
        <source>Restore Auto preset</source>
        <comment>Reset button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="273"/>
        <source>Apply Style</source>
        <comment>Apply button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="274"/>
        <source>Reset Style</source>
        <comment>Reset button</comment>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StyleTab</name>
    <message>
        <location filename="../sidebars/tabs/style.py" line="42"/>
        <source>GUI Style</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="56"/>
        <source>Background &amp; Surfaces</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="60"/>
        <source>Primary Background</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="63"/>
        <source>Main background color of the application window and dialogs.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="68"/>
        <source>Input Background</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="71"/>
        <source>Background color of text fields, combo boxes, and editable areas.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="76"/>
        <source>Input Background (hover)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="79"/>
        <source>Background color when the mouse hovers over an input field.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="84"/>
        <source>Input Background (disabled)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="87"/>
        <source>Background color for disabled (greyed-out) input fields.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="92"/>
        <source>Button Background</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="93"/>
        <source>Background color of buttons.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="97"/>
        <source>Button Background (hover)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="100"/>
        <source>Background color of a button when the mouse hovers over it.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="105"/>
        <source>Caption Background</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="108"/>
        <source>Semi-transparent background color of each window titles.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="114"/>
        <source>Text &amp; Icons</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="118"/>
        <source>Primary Text</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="120"/>
        <source>Text color of body text and labels.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="125"/>
        <source>Primary Text (hover)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="128"/>
        <source>Text color when the mouse hovers over clickable items.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="133"/>
        <source>Secondary Text</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="136"/>
        <source>Text color for secondary information, captions, and section headers.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="141"/>
        <source>Icon Fill</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="143"/>
        <source>Fill color of sidebar and toolbar icons.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="149"/>
        <source>Borders &amp; Separators</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="153"/>
        <source>Border</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="156"/>
        <source>Border color for input fields, buttons, and panels.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="161"/>
        <source>Border (hover)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="164"/>
        <source>Border color when hovering over interactive elements.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="170"/>
        <source>Controls &amp; Highlights</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="174"/>
        <source>Accent</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="177"/>
        <source>Primary accent color for checkboxes, sliders and other interactive controls.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="182"/>
        <source>Accent (hover)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="185"/>
        <source>Accent color when the mouse hovers over an interactive control.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="190"/>
        <source>Revert Button</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="192"/>
        <source>Background color of the &apos;Reset&apos; button.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="197"/>
        <source>Revert Button (hover)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="200"/>
        <source>&apos;Reset&apos; button background color on hover.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="205"/>
        <source>Handle</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="208"/>
        <source>Fill color of scrollbar handles and subtle interactive areas.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="213"/>
        <source>Handle (hover)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="215"/>
        <source>Handle control fill color on hover.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="229"/>
        <source>Palette Preset</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="231"/>
        <source>Preset</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="238"/>
        <source>Select a pre-built color scheme for the GUI.</source>
        <extracomment>Do not translate &quot;Custom&quot; and preset names like &quot;Auto&quot;, they are internal identifiers.</extracomment>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>WindowGridManager</name>
    <message>
        <location filename="../helpers/grid.py" line="128"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../helpers/grid.py" line="131"/>
        <source>Could not enumerate windows.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>WindowPickerDialog</name>
    <message>
        <location filename="../dialogs/window.py" line="39"/>
        <source>Select Window</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/window.py" line="51"/>
        <source>Filter windows</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/window.py" line="93"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/window.py" line="94"/>
        <source>Could not list windows.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/window.py" line="143"/>
        <source>No selection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../dialogs/window.py" line="144"/>
        <source>Select a window first.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
