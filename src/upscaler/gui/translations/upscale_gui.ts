<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
  <context>
    <name>AboutDialog</name>
    <message>
      <location filename="../dialogs/about.py" line="95" />
      <source>Real-Time Upscaler</source>
      <comment>Localized application name</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/about.py" line="102" />
      <source>Version {0}</source>
      <comment>Version of the upscaler</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/about.py" line="110" />
      <source>A real-time SRCNN upscaler for any X-Window on GNU/Linux.</source>
      <comment>Description of the upscaler</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/about.py" line="125" />
      <source>Close</source>
      <comment>Close button</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>AdvancedTab</name>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="26" />
      <source>Advanced</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="33" />
      <source>Vulkan Rendering</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="35" />
      <source>Buffer Pool Size</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="41" />
      <source>Number of pre-allocated staging buffers for partial texture updates.
Raise this if you notice stutters when many small regions change rapidly.
Recommended range: 2 - 16.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="49" />
      <source>Frame Timeout (ms)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="55" />
      <source>Maximum time (in milliseconds) to wait for the GPU to finish the previous frame.
Lower values reduce CPU blocking but may drop frames under heavy load.
Recommended range: 17 (1/60 s) - 1000 (1 s).</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="64" />
      <source>Tile-Based Processing</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="66" />
      <source>Enable Tile Mode</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="70" />
      <source>Divide the frame into tiles and only re-process the ones that have changed.
Ideal for mostly static content (e.g. text editors, visual novels).
When disabled, the whole frame is upscaled in one pass: better for video or rapid changes.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="78" />
      <source>Damage Tracking</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="82" />
      <source>Transfer only the changed regions of the frame to the GPU instead of the entire image.
Disable if you suspect missed updates from the compositor causing glitches.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="89" />
      <source>Tile Size</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="95" />
      <source>Interior size of each tile in pixels.
Smaller tiles track changes more precisely but add CPU overhead.
Multiples of 32 work best with GPU workgroups.
Recommended range: 32 - 128.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="104" />
      <source>Context Margin</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="110" />
      <source>Extra border pixels added around each tile to provide context for the neural network.
Larger margins improve boundary quality but increase processing.
Recommended range: 4 - 24.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="118" />
      <source>Max Tiles per Frame</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="124" />
      <source>Maximum number of dirty tiles processed per frame.
When exceeded, the pipeline falls back to full-frame processing to avoid excessive GPU dispatches.
Recommended range: 4 - 32.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="132" />
      <source>Area Threshold %</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="139" />
      <source>Fraction of the window area (in %) that, when dirty, forces a fallback to full-frame processing.
Smaller values fall back earlier, preventing too many tiny tile dispatches.
Recommended range: 15% - 50%.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="149" />
      <source>Timing</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="151" />
      <source>Daemon Poll (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="158" />
      <source>How often the daemon scans for matching windows.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="164" />
      <source>Focus Poll (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="171" />
      <source>How often the focus monitor checks for active window changes.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="177" />
      <source>Pipeline Idle (s)</source>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="184" />
      <source>How often the pipeline checks its internal state when idle.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="191" />
      <source>Error Recovery</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="193" />
      <source>Max Capture Failures</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="200" />
      <source>Consecutive frame-grab failures before the pipeline stops.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="206" />
      <source>Capture Failure Delay (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="213" />
      <source>Pause after a capture failure before retrying.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="219" />
      <source>Swapchain Debounce (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="226" />
      <source>Minimum time between two Vulkan swapchain recreations.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>ColorPickerRow</name>
    <message>
      <location filename="../sidebars/controls/color.py" line="98" />
      <source>Choose Background Color</source>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>DisplayTab</name>
    <message>
      <location filename="../sidebars/tabs/display.py" line="33" />
      <source>Auto (best)</source>
      <comment>GPU automatic device option</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="36" />
      <source>Display</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="43" />
      <source>Devices</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="45" />
      <source>Monitor</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="50" />
      <source>Monitor to cover: 'primary', 'all' (multi-monitor), or a specific output name (e.g., 'HDMI-1').</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="63" />
      <source>GPU</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="72" />
      <source>Vulkan GPU used for rendering. '{0}' selects the most powerful GPU found.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="79" />
      <source>V-Sync</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="81" />
      <source>Present Mode</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="86" />
      <source>Vulkan presentation mode:
• fifo: VSync on, lowest power, no tearing
• mailbox: tear-free, lower latency, higher power
• immediate: no VSync, lowest latency, may tear</source>
      <comment>Description of a setting (tooltip). Do not translate fifo, mailbox and immediate: they are Vulkan presentation mode identifiers.</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="97" />
      <source>Limit FPS</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="101" />
      <source>Enable an upper frame-rate limit.
It's recommended to use 'mailbox' presentation mode when limiting FPS.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="108" />
      <source>Max FPS</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="118" />
      <source>Target maximum frames per second.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="126" />
      <source>Scale Factor</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="128" />
      <source>Auto Scale</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="132" />
      <source>Let the application automatically detect the correct scale factor based on the physical monitor resolution.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="139" />
      <source>Scale Factor %</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="150" />
      <source>Manual scale factor (e.g., 1.50 for 150% scaling). Only available when 'Auto Scale' is disabled.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>EffectsTab</name>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="26" />
      <source>Effects</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="33" />
      <source>Debanding</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="35" />
      <source>Enable Deband</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="39" />
      <source>Smooth harsh color banding in gradients before upscaling. Helps skies, fog and smooth backgrounds.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="220" />
      <location filename="../sidebars/tabs/effects.py" line="160" />
      <location filename="../sidebars/tabs/effects.py" line="102" />
      <location filename="../sidebars/tabs/effects.py" line="75" />
      <location filename="../sidebars/tabs/effects.py" line="46" />
      <source>Strength</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="53" />
      <source>Debanding intensity (0 = off, 1 = maximum). Low values (0.1-0.3) are sufficient for most content.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="62" />
      <source>CAS Sharpening</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="64" />
      <source>Enable CAS</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="68" />
      <source>Contrast Adaptive Sharpening: enhances text and line art without the halos of traditional unsharp masks.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="82" />
      <source>Sharpening amount (0 = none, 1 = max). 0.2-0.5 gives pleasant crispness.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="90" />
      <source>Bloom (Glow)</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="92" />
      <source>Enable Bloom</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="96" />
      <source>Soft glow around bright areas, creating a cinematic look.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="109" />
      <source>Bloom intensity (0 = off, 1 = max). Subtle values (0.02-0.06) add a gentle, polished look.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="118" />
      <source>Threshold</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="125" />
      <source>Brightness cutoff for bloom. Only pixels above this contribute. Lower values include more of the scene.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="176" />
      <location filename="../sidebars/tabs/effects.py" line="134" />
      <source>Radius</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="140" />
      <source>Blur radius in pixels. Larger radii spread the glow further.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="148" />
      <source>Vignette</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="150" />
      <source>Enable Vignette</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="154" />
      <source>Radial darkening of screen edges, drawing focus to the center.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="167" />
      <source>Edge darkening intensity (0 = none, 1 = max). Moderate values (0.3-0.6) give a subtle framing effect.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="183" />
      <source>Distance from center where darkening begins. Higher values keep the center bright longer.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="192" />
      <source>Falloff</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="199" />
      <source>Softness of the vignette transition. Low values = gentle, high values = sharp ring.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="208" />
      <source>Film Grain</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="210" />
      <source>Enable Grain</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="214" />
      <source>Simulated film grain for a photochemical, organic look.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="227" />
      <source>Grain intensity (0 = off, 1 = max). Low values (0.1-0.2) mimic fine photochemical grain.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="236" />
      <source>Size</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="243" />
      <source>Apparent particle size of the grain. Larger values produce coarser, more visible grain.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="252" />
      <source>Color Grading (3D LUT)</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="254" />
      <source>Enable LUT</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="258" />
      <source>Apply a cinematic color-lookup table for instant film-stock emulation or color grading.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="265" />
      <source>Preset</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="270" />
      <source>Built-in 3D LUT preset. Choose from warm, cool, film, sepia, etc.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="278" />
      <source>Intensity</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="285" />
      <source>Blend between original and graded image (0 = original, 1 = full effect).</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>ExtrasTab</name>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="25" />
      <source>Extras</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="32" />
      <source>Screenshot Location</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="34" />
      <source>Directory</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="38" />
      <source>Folder where screenshots will be saved.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="44" />
      <source>Template</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="48" />
      <source>Filename template for screenshots. Available placeholders:
• {timestamp}: capture time (supports strftime, e.g. {timestamp:%Y-%m-%d-%H-%M-%S})
• {title}: current window title
• {profile}: active profile name (fallback to {{title}} if no profile)
• {model}: active upscaling model
• {width}: upscaled image width
• {height}: upscaled image height</source>
      <comment>Description of a setting (tooltip). Do not translate any of the placeholders (eg. {timestamp}).</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="63" />
      <source>On-Screen Display</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="65" />
      <source>Show OSD</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="69" />
      <source>Show on-screen messages when model, geometry, or zoom changes, and after taking a screenshot.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="76" />
      <source>Duration (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="83" />
      <source>How many seconds OSD messages remain visible before fading out.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>FilterBar</name>
    <message>
      <location filename="../grid/filter.py" line="35" />
      <source>Filter windows</source>
      <comment>Filter windows search bar placeholder</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>GeneralTab</name>
    <message>
      <location filename="../sidebars/tabs/general.py" line="32" />
      <source>General</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="39" />
      <source>Upscaling Model</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="41" />
      <source>Model</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="46" />
      <source>Upscaling model to use. Models are ordered from worst to best quality. Larger numbers indicate deeper networks (slower, higher quality).</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="53" />
      <source>Double Upscale (4x)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="58" />
      <source>Perform two consecutive 2x upscales for a 4x total (e.g., 720p to 2880p). Useful for high-resolution screens (4K) and low-resolution sources. Increases GPU usage.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="68" />
      <source>Focus Tracking</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="70" />
      <source>Follow Focus</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="74" />
      <source>Automatically switch the upscaling target to the currently focused window. Useful when moving between multiple windows.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="81" />
      <source>Pause on Focus Loss</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="85" />
      <source>When the target window loses focus, hide the overlay until it regains focus. Uncheck to keep the overlay always visible.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="93" />
      <source>Automatic Upscaling</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="96" />
      <source>Exclude from Daemon Mode</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="100" />
      <source>Exclude this profile from automatic upscaling.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="107" />
      <source>Daemon Mode</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="112" />
      <source>When enabled, a daemon process runs in the background and automatically upscales any window that matches a profile.
Disable this to manually pick a window from the grid.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>MainWindow</name>
    <message>
      <location filename="../main.py" line="84" />
      <source>Real-Time Upscaler</source>
      <comment>Localized name of the application</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../main.py" line="142" />
      <source>About Real-Time Upscaler.</source>
      <comment>About dialog button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../main.py" line="341" />
      <source>Error</source>
      <comment>Error starting pipeline</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../main.py" line="342" />
      <source>Could not start pipeline:
{0}</source>
      <comment>Error starting pipeline</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../main.py" line="462" />
      <source>Save Error</source>
      <comment>Error while saving configuration</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../main.py" line="463" />
      <source>Could not save:
{0}</source>
      <comment>Error while saving configuration</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>PathPickerRow</name>
    <message>
      <location filename="../sidebars/controls/path.py" line="52" />
      <source>Select directory</source>
      <comment>Path selector placeholder</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/controls/path.py" line="64" />
      <source>Browse for directory.</source>
      <comment>Path selector placeholder</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/controls/path.py" line="113" />
      <source>Choose screenshot directory</source>
      <comment>Screenshot directory dialog title</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>PresentationTab</name>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="27" />
      <source>Presentation</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="34" />
      <source>Overlay</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="36" />
      <source>Overlay Mode</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="41" />
      <source>Overlay window behaviour:
• always-on-top: floating, cannot be focused (recommended)
• top-transparent: click-through (mouse passes to window below)
• fullscreen: covers entire monitor
• windowed: normal window with decorations</source>
      <comment>Description of a setting (tooltip). Do not translate 'always-on-top', 'top-transparent', 'fullscreen', 'windowed': they are internal overlay mode identifiers.</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="51" />
      <source>Output Geometry</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="56" />
      <source>How the upscaled content fits the overlay:
• fit: letterbox, preserves aspect ratio
• stretch: fill, aspect ratio may be distorted
• cover: fill and crop to fit</source>
      <comment>Description of a setting (tooltip). Do not translate 'fit', 'stretch', 'cover': they are internal output geometry identifiers.</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="68" />
      <source>Cursor</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="70" />
      <source>Hide cursor</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="74" />
      <source>Automatically hide the mouse cursor after a period of inactivity.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="87" />
      <source>Hide Timeout (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="94" />
      <source>Time in seconds after which the cursor disappears.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="104" />
      <source>Left</source>
      <comment>Crop border label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="105" />
      <source>Top</source>
      <comment>Crop border label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="106" />
      <source>Right</source>
      <comment>Crop border label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="108" />
      <source>Bottom</source>
      <comment>Crop border label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="120" />
      <source>Pixels to crop from the {0} border of the target window.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="127" />
      <source>Offset</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="130" />
      <source>X Offset</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="135" />
      <source>Y Offset</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="148" />
      <source>Horizontal offset from the centered position (positive = right, negative = left).</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="154" />
      <source>Vertical offset from the centered position (positive = down, negative = up).</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="163" />
      <source>Background Color</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="167" />
      <source>Color</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="171" />
      <source>Color of the letterbox bars. Supports transparency.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>ProfileActions</name>
    <message>
      <location filename="../helpers/profiles.py" line="59" />
      <source>Unsaved changes</source>
      <comment>Warning dialog title</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/profiles.py" line="62" />
      <source>Save changes before switching profile?</source>
      <comment>Warning dialog</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/profiles.py" line="180" />
      <location filename="../helpers/profiles.py" line="118" />
      <source>Error</source>
      <comment>Error dialog title</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/profiles.py" line="121" />
      <source>Could not add profile.</source>
      <comment>Error while adding profile</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/profiles.py" line="147" />
      <source>Duplicate name</source>
      <comment>Error dialog title</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/profiles.py" line="150" />
      <source>A profile named '{0}' already exists.</source>
      <comment>Error while adding profile</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/profiles.py" line="183" />
      <source>Could not edit profile.</source>
      <comment>Error while editing profile</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/profiles.py" line="195" />
      <source>Delete profile</source>
      <comment>Delete window confirmation title</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/profiles.py" line="200" />
      <source>Delete profile '{0}'?</source>
      <comment>Delete profile confirmation</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/profiles.py" line="256" />
      <location filename="../helpers/profiles.py" line="237" />
      <location filename="../helpers/profiles.py" line="218" />
      <source>Error</source>
      <comment>Error window title</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/profiles.py" line="221" />
      <source>Could not delete profile.</source>
      <comment>Error while deleting profile</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/profiles.py" line="259" />
      <location filename="../helpers/profiles.py" line="240" />
      <source>Could not reorder profiles.</source>
      <comment>Error while reordering profiles</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>ProfileDialog</name>
    <message>
      <location filename="../dialogs/profile.py" line="59" />
      <source>Profile Editor</source>
      <comment>Window title of the profile editor</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="61" />
      <source>New Profile</source>
      <comment>Window title of the profile creator</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="82" />
      <source>Name</source>
      <comment>Profile dialog label of profile 'Name'</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="88" />
      <source>Profile name</source>
      <comment>Profile name label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="91" />
      <source>A unique name for this profile. Required.</source>
      <comment>Tooltip of profile name text input</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="101" />
      <source>Icon</source>
      <comment>Label of Icon button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="143" />
      <source>Capture window</source>
      <comment>'Capture window' button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="149" />
      <source>Fill name, icon, and match rules from a window.</source>
      <comment>Capture window tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="161" />
      <source>Capture icon from window</source>
      <comment>Capture icon tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="167" />
      <source>Load icon from file</source>
      <comment>Load icon tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="173" />
      <source>Remove icon</source>
      <comment>Remove icon tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="179" />
      <source>Match rules</source>
      <comment>Match rules group label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="181" />
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
      <comment>Match rules tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="202" />
      <source>Title (exact):</source>
      <comment>Match rule label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="203" />
      <source>e.g., Steam</source>
      <comment>Match rule placeholder</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="205" />
      <source>Match if the window title exactly equals this text (case-insensitive).</source>
      <comment>Match rule tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="215" />
      <source>Title contains:</source>
      <comment>Match rule label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="216" />
      <source>e.g., VLC</source>
      <comment>Match rule placeholder</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="218" />
      <source>Match if the window title contains this text (case-insensitive).</source>
      <comment>Match rule tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="227" />
      <source>Title (regex):</source>
      <comment>Match rule label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="228" />
      <source>e.g., (Yuzu|Ryujinx).*</source>
      <comment>Match rule placeholder</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="230" />
      <source>Match if the window title matches this regular expression (case-insensitive).</source>
      <comment>Match rule tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="241" />
      <source>Width:</source>
      <comment>Match rule label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="242" />
      <source>e.g., &gt;1280</source>
      <comment>Match rule placeholder</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="244" />
      <source>Match if the window width satisfies this condition:
• Exact: 1920
• Comparison: &lt;800, &gt;1024, &lt;=1366, &gt;=1920
• Range: 1280-1920, 720..1080, 1024,1366</source>
      <comment>Match rule tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="256" />
      <source>Height:</source>
      <comment>Match rule label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="257" />
      <source>e.g., &gt;800</source>
      <comment>Match rule placeholder</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="271" />
      <source>Profiles let you override settings for specific windows and setups.
A profile is applied automatically when the upscaled window matches all the rules defined here, or when manually selected before upscaling.
Profiles are checked top-to-bottom: the first match wins.
Leave a rule blank to ignore that property.</source>
      <comment>Profile note</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="388" />
      <source>No icon</source>
      <comment>No icon warning</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="389" />
      <source>The selected window has no icon.</source>
      <comment>No icon warning</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="407" />
      <source>Select Icon</source>
      <comment>Select Icon dialog title</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="416" />
      <source>Invalid image</source>
      <comment>Invalid image warning</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="417" />
      <source>Could not load the selected file.</source>
      <comment>Invalid image warning</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="448" />
      <source>Missing name</source>
      <comment>Warning while saving a profile without name</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="449" />
      <source>Profile name cannot be empty.</source>
      <comment>Warning while saving a profile without name</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="461" />
      <source>Duplicate name</source>
      <comment>Warning while saving a profile with an existing name</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/profile.py" line="465" />
      <source>A profile named '{0}' already exists.
Please choose a different name.</source>
      <comment>Warning while saving a profile with an existing name</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>ProfilesSidebar</name>
    <message>
      <location filename="../sidebars/profiles.py" line="80" />
      <source>Profiles</source>
      <comment>Profiles sidebar title</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="133" />
      <source>Add profile (Ctrl+N)</source>
      <comment>Profile add action tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="139" />
      <source>Edit match criteria (Enter/F2)</source>
      <comment>Profile edit action tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="146" />
      <source>Delete profile (Del)</source>
      <comment>Profile delete action tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="154" />
      <source>Move up (Ctrl+Shift+Up)</source>
      <comment>Profile move up action tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="161" />
      <source>Move down (Ctrl+Shift+Down)</source>
      <comment>Profile move down action tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="259" />
      <source>Global</source>
      <comment>Global entry profile name</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="264" />
      <source>When selected, the settings panel on the right edits the global configuration.</source>
      <comment>Global entry profile tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="274" />
      <source>Global settings apply to all windows.

Create a profile to override settings
for a specific window, matched by its
name or size.</source>
      <comment>No profile message (preserve line width)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="317" />
      <source>When selected, the settings panel on the right edits the '{0}' profile overrides.</source>
      <comment>Profile selected tooltip</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>ScalingTab</name>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="32" />
      <source>Scaling</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="39" />
      <source>Sampler Algorithm</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="41" />
      <source>Upsampler</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="46" />
      <source>Applied after SRCNN upscaling to reach the target output size (e.g., 1440p → 4k).
• Fixed Lanczos-2 — sharp, linear-light, best for 2D art
• AMD FidelityFX Super Resolution 1.0 — fast, edge-adaptive, best for 3D content
• NVIDIA Image Scaling — directional sharpening, sRGB, may look oversharpened</source>
      <comment>Description of a setting (tooltip). Do not alter the names of the filters (eg. Lanczos-2).</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="56" />
      <source>Downsampler</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="63" />
      <source>Applied after SRCNN upscaling to reduce the image to the target output size (e.g., 1440p → 1080p).
• Catmull-Rom (bicubic) — sharper and faster than Lanczos for mild downscaling
• Adaptive Lanczos — variable radius, high quality even in extreme downscales</source>
      <comment>Description of a setting (tooltip). Do not alter the names of the filters (eg. Catmull-Rom).</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="73" />
      <source>Sampler Options</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="75" />
      <source>Blur</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="82" />
      <source>Kernel width (blur factor) for Lanczos and Catmull-Rom.
Lower values increase sharpness/ringing, while higher values smooth the result.
Recommended range: 0.8 - 1.2.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="90" />
      <source>Antiring Strength</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="97" />
      <source>Anti-ringing strength (0.0 - 1.0) for Adaptive Lanczos and Catmull-Rom.
Lower values soften the clamp, preserving more detail at the cost of possible ringing.
Recommended range: 0.7 - 1.0.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="106" />
      <source>Lanczos Options</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="108" />
      <source>Tight Antiring</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="112" />
      <source>Use only the central 2x2 neighborhood for anti-ringing bounds.
Keeps thin text and line art sharp. Disable if you see distant ringing artifacts on high-contrast edges.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="120" />
      <source>Override Lanczos Radius</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="124" />
      <source>Force a specific Lanczos kernel radius instead of the automatic selection.
When unchecked, radius is chosen automatically (2 for upscaling, variable for downscaling).</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="131" />
      <source>Radius</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="141" />
      <source>Lanczos kernel radius (2 = standard Lanczos2, 3 = sharper 6-tap, etc.).
Higher radii reduce aliasing but increase GPU load.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>SettingsSidebar</name>
    <message>
      <location filename="../sidebars/settings.py" line="78" />
      <source>General</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="83" />
      <source>Scaling</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="88" />
      <source>Display</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="93" />
      <source>Presentation</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="98" />
      <source>Effects</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="103" />
      <source>Advanced</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="108" />
      <source>Extras</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="113" />
      <source>GUI Style</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="324" />
      <location filename="../sidebars/settings.py" line="218" />
      <source>Save Profile</source>
      <comment>Save button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="326" />
      <location filename="../sidebars/settings.py" line="220" />
      <source>Save</source>
      <comment>Save button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="328" />
      <location filename="../sidebars/settings.py" line="231" />
      <source>Reset</source>
      <comment>Reset button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="242" />
      <source>Clear profile overrides</source>
      <comment>Reset button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="244" />
      <source>Restore system defaults</source>
      <comment>Reset button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="252" />
      <source>Reset to last applied</source>
      <comment>Reset button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="255" />
      <source>Restore Auto preset</source>
      <comment>Reset button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="304" />
      <source>Apply Style</source>
      <comment>Apply button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/settings.py" line="305" />
      <source>Reset Style</source>
      <comment>Reset button</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>StyleTab</name>
    <message>
      <location filename="../sidebars/tabs/style.py" line="42" />
      <source>GUI Style</source>
      <comment>Name of a settings tab</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="56" />
      <source>Background &amp; Surfaces</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="60" />
      <source>Primary Background</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="63" />
      <source>Main background color of the application window and dialogs.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="70" />
      <source>Input Background</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="71" />
      <source>Background color of text fields, combo boxes, and editable areas.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="78" />
      <source>Input Background (hover)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="82" />
      <source>Background color when the mouse hovers over an input field.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="89" />
      <source>Input Background (disabled)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="93" />
      <source>Background color for disabled (greyed-out) input fields.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="100" />
      <source>Button Background</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="103" />
      <source>Background color of buttons.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="110" />
      <source>Button Background (hover)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="114" />
      <source>Background color of a button when the mouse hovers over it.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="121" />
      <source>Caption Background</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="124" />
      <source>Semi-transparent background color of each window titles.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="132" />
      <source>Text &amp; Icons</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="136" />
      <source>Primary Text</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="137" />
      <source>Text color of body text and labels.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="144" />
      <source>Primary Text (hover)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="147" />
      <source>Text color when the mouse hovers over clickable items.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="154" />
      <source>Secondary Text</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="155" />
      <source>Text color for secondary information, captions, and section headers.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="162" />
      <source>Icon Fill</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="163" />
      <source>Fill color of sidebar and toolbar icons.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="171" />
      <source>Borders &amp; Separators</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="175" />
      <source>Border</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="176" />
      <source>Border color for input fields, buttons, and panels.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="183" />
      <source>Border (hover)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="184" />
      <source>Border color when hovering over interactive elements.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="192" />
      <source>Controls &amp; Highlights</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="196" />
      <source>Accent</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="197" />
      <source>Primary accent color for checkboxes, sliders and other interactive controls.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="204" />
      <source>Accent (hover)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="205" />
      <source>Accent color when the mouse hovers over an interactive control.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="212" />
      <source>Revert Button</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="213" />
      <source>Background color of the 'Reset' button.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="220" />
      <source>Revert Button (hover)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="223" />
      <source>'Reset' button background color on hover.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="230" />
      <source>Handle</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="231" />
      <source>Fill color of scrollbar handles and subtle interactive areas.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="238" />
      <source>Handle (hover)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="239" />
      <source>Handle control fill color on hover.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="255" />
      <source>Palette Preset</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="257" />
      <source>Preset</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/style.py" line="261" />
      <source>Select a pre-built color scheme for the GUI.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>WindowGridManager</name>
    <message>
      <location filename="../helpers/grid.py" line="128" />
      <source>Error</source>
      <comment>Error warning while enumerating windows</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/grid.py" line="133" />
      <source>Could not enumerate windows.</source>
      <comment>Error warning while enumerating windows</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>WindowPickerDialog</name>
    <message>
      <location filename="../dialogs/window.py" line="39" />
      <source>Select Window</source>
      <comment>Select Window dialog title</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/window.py" line="52" />
      <source>Filter windows</source>
      <comment>Filter windows placeholder</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/window.py" line="96" />
      <source>Error</source>
      <comment>Could not list windows error</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/window.py" line="97" />
      <source>Could not list windows.</source>
      <comment>Could not list windows error</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/window.py" line="148" />
      <source>No selection</source>
      <comment>No window selected warning title</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../dialogs/window.py" line="149" />
      <source>Select a window first.</source>
      <comment>No window selected warning</comment>
      <translation type="unfinished" />
    </message>
  </context>
</TS>
