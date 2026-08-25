<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="en">
  <context>
    <name>AboutDialog</name>
    <message>
      <location filename="../dialogs/about.py" line="95" />
      <source>Real-Time Upscaler</source>
      <comment>Name of the application</comment>
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
      <source>Tile-Based Processing</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="35" />
      <source>Enable Tile Mode</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="39" />
      <source>Process only the parts of the frame that have changed, using small tiles.
Best for mostly static content, such as text editors or visual novels.
When disabled, the entire frame is processed at once, better for video or fast-moving content.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="47" />
      <source>Damage Tracking</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="51" />
      <source>Send only the changed parts of the frame to the GPU, instead of the whole image.
Disable this if you see glitches that may be caused by missed updates.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="58" />
      <source>Tile Size</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="64" />
      <source>Size of each tile in pixels.
Smaller tiles update more precisely but use more CPU.
Values that are multiples of 32 usually perform best.
Recommended range: 32 - 128.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="73" />
      <source>Context Margin</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="79" />
      <source>Extra pixels added around each tile to give the neural network more context.
Larger margins can improve quality at tile edges but increase processing.
Recommended range: 4 - 24.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="87" />
      <source>Max Tiles per Frame</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="93" />
      <source>Maximum number of changed tiles to process per frame.
If more tiles than this need updating, the whole frame will be processed instead.
Recommended range: 4 - 32.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="101" />
      <source>Area Threshold %</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="108" />
      <source>If more than this percentage of the frame has changed, the whole frame will be processed instead of individual tiles.
Lower values switch to full-frame processing sooner.
Recommended range: 15% - 50%.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="118" />
      <source>Timing</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="120" />
      <source>Frame Timeout (ms)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="126" />
      <source>Maximum time to wait for the GPU to finish the previous frame.
Lower values reduce waiting time but may cause dropped frames.
Recommended range: 17 (1/60 s) - 1000 (1 s).</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="134" />
      <source>Daemon Poll (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="141" />
      <source>How often the background service checks for matching windows.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="147" />
      <source>Focus Poll (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="154" />
      <source>How often the program checks which window is currently active.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="160" />
      <source>Pipeline Idle (s)</source>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="167" />
      <source>How often the program checks its internal state when no changes are detected.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="174" />
      <source>Error Recovery</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="176" />
      <source>Max Capture Failures</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="183" />
      <source>Number of consecutive frame capture failures before the program stops.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="189" />
      <source>Capture Failure Delay (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="196" />
      <source>Delay after a capture failure before trying again.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="202" />
      <source>Swapchain Debounce (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/advanced.py" line="209" />
      <source>Minimum time between two Vulkan swapchain recreations.
This prevents unnecessary rebuilds of the rendering pipeline.</source>
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
      <source>Monitor used for upscaling: the primary monitor, multi-monitor, or a specific output name (for example, HDMI-1).</source>
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
      <source>GPU used for upscaling.
Select '{0}' to automatically use the most powerful available GPU.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="80" />
      <source>V-Sync</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="82" />
      <source>Present Mode</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="87" />
      <source>Vulkan presentation mode:
• fifo: VSync on, lowest power, no tearing
• mailbox: tear-free, lower latency, higher power
• immediate: no VSync, lowest latency, may tear</source>
      <comment>Description of a setting (tooltip). Do not translate fifo, mailbox and immediate: they are Vulkan presentation mode identifiers.</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="98" />
      <source>Limit FPS</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="102" />
      <source>Enable a maximum frame rate.
For best results, use the 'mailbox' presentation mode when limiting FPS.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="109" />
      <source>Max FPS</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="119" />
      <source>Target maximum frames per second.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="127" />
      <source>Scale Factor</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="129" />
      <source>Auto Scale</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="133" />
      <source>Automatically detect the correct scale factor based on the physical monitor resolution.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="139" />
      <source>Scale Factor</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/display.py" line="150" />
      <source>Set the scale factor manually as a percentage (for example, 1.50 for 150% scaling).
Only available when Auto Scale is off.</source>
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
      <source>Reduce banding in smooth gradients before upscaling.
Only useful if you notice banding in skies, fog, and other large smooth areas.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="217" />
      <location filename="../sidebars/tabs/effects.py" line="158" />
      <location filename="../sidebars/tabs/effects.py" line="101" />
      <location filename="../sidebars/tabs/effects.py" line="73" />
      <location filename="../sidebars/tabs/effects.py" line="46" />
      <source>Strength</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="53" />
      <source>Debanding intensity.
Recommended range: 0.10 - 0.30.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="61" />
      <source>CAS Sharpening</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="63" />
      <source>Enable CAS</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="67" />
      <source>Contrast Adaptive Sharpening: enhances text and line art contrast.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="80" />
      <source>Sharpening amount.
Recommended range: 0.20 - 0.50.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="88" />
      <source>Bloom (Glow)</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="90" />
      <source>Enable Bloom</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="94" />
      <source>Soft glow around bright areas, for a cinematic look.
May introduce halos, especially with white text.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="108" />
      <source>Bloom intensity.
Recommended range: 0.02 - 0.06.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="116" />
      <source>Threshold</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="123" />
      <source>Brightness cutoff for bloom.
Only pixels brighter than this value will glow.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="173" />
      <location filename="../sidebars/tabs/effects.py" line="132" />
      <source>Radius</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="138" />
      <source>Blur radius in pixels. Larger radii spread the glow further.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="146" />
      <source>Vignette</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="148" />
      <source>Enable Vignette</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="152" />
      <source>Radial darkening of screen edges, drawing focus to the center.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="165" />
      <source>Edge darkening intensity.
Recommended range: 0.30 - 0.60.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="180" />
      <source>Distance from center where darkening begins.
Higher values keep the center brighter.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="189" />
      <source>Falloff</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="196" />
      <source>Softness of the vignette transition. Low values = gentle, high values = sharp ring.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="205" />
      <source>Film Grain</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="207" />
      <source>Enable Grain</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="211" />
      <source>Simulated film grain look.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="224" />
      <source>Grain intensity.
Recommended range: 0.10 - 0.20.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="232" />
      <source>Size</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="239" />
      <source>Particle size of the grain.
Larger values produce coarser, more visible grain.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="248" />
      <source>Color Grading (3D LUT)</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="250" />
      <source>Enable LUT</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="254" />
      <source>Apply a color grading preset (LUT) to change the look of the window.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="260" />
      <source>Preset</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="265" />
      <source>Built-in color grading preset (warm, cool, film, sepia, etc.).</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="273" />
      <source>Intensity</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/effects.py" line="280" />
      <source>Blend between original and graded image.</source>
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
      <source>Folder where screenshots are saved.</source>
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
      <source>Filename template for screenshots. You can use these placeholders:
• {timestamp}: capture time (supports strftime, for example {timestamp:%Y-%m-%d-%H-%M-%S})
• {title}: current window title
• {profile}: active profile name (or the window title if no profile)
• {model}: active upscaling model
• {width}: upscaled image width
• {height}: upscaled image height</source>
      <comment>Description of a setting (tooltip). Keep all placeholders exactly as they are, including braces, for example {timestamp} and the strftime format inside it.</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="64" />
      <source>On-Screen Display</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="66" />
      <source>Show OSD</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="70" />
      <source>Show on-screen messages when the model, window geometry, or zoom changes, or after taking a screenshot.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="77" />
      <source>Duration (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/extras.py" line="84" />
      <source>How many seconds on-screen messages remain visible before fading out.</source>
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
      <source>Upscaling SRCNN model to use.
All models upscale to 2x, and are ordered from lowest to highest quality.
Rightmost models are deeper and slower, but produce better results.
The value 'none' disables SRCNN processing and uses only the selected scaler (upsampler/downsampler).</source>
      <comment>Description of a setting (tooltip). Do not translate 'none', since it's a model identifier</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="56" />
      <source>Double Upscale (4x)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="60" />
      <source>Perform two 2x upscales in a row for a total of 4x (for example, 720p to 2880p).
Useful for high-resolution screens (4K) and low-resolution sources.
Uses more GPU power.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="70" />
      <source>Focus Tracking</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="72" />
      <source>Follow Focus</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="76" />
      <source>Automatically upscale the window that currently has focus.
Useful when working with multiple windows.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="83" />
      <source>Pause on Focus Loss</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="87" />
      <source>Hide the upscaled overlay when the target window loses focus, and show it again when focus returns.
Turn off to keep the overlay always visible.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="95" />
      <source>Automatic Upscaling</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="98" />
      <source>Exclude from Daemon Mode</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="102" />
      <source>When Daemon Mode is active, this profile will not be used to automatically upscale matching windows.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="110" />
      <source>Daemon Mode</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/general.py" line="114" />
      <source>When enabled, a background process automatically upscales any window that matches a profile.
Turn off to manually select a window from the grid.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>MainWindow</name>
    <message>
      <location filename="../main.py" line="95" />
      <source>Real-Time Upscaler</source>
      <comment>Name of the application</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../main.py" line="159" />
      <source>Enable/Disable System Tray</source>
      <comment>Tray toggle button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../main.py" line="179" />
      <source>About Real-Time Upscaler.</source>
      <comment>About dialog button</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../main.py" line="398" />
      <source>Error</source>
      <comment>Error starting pipeline</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../main.py" line="399" />
      <source>Could not start pipeline:
{0}</source>
      <comment>Error starting pipeline</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../main.py" line="562" />
      <source>Save Error</source>
      <comment>Error while saving configuration</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../main.py" line="563" />
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
• always-on-top: always visible above other windows, keeps focus on the target window (recommended)
• top-transparent: same as always-on-top, but click-through (mouse passes to window below)
• fullscreen: covers entire monitor, keyboard may not reach the target window
• windowed: normal window with decorations, keyboard may not reach the target window</source>
      <comment>Description of a setting (tooltip). Do not translate 'always-on-top', 'top-transparent', 'fullscreen', 'windowed': they are internal overlay mode identifiers.</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="53" />
      <source>Output Geometry</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="58" />
      <source>How the upscaled content fits the overlay:
• fit: show the entire image, adding black bars if necessary
• stretch: fill the whole area, aspect ratio may be distorted
• cover: fill the whole area and crop any excess</source>
      <comment>Description of a setting (tooltip). Do not translate 'fit', 'stretch', 'cover': they are internal output geometry identifiers.</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="70" />
      <source>Cursor</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="72" />
      <source>Hide cursor</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="76" />
      <source>Automatically hide the mouse cursor after a period of inactivity.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="89" />
      <source>Hide Timeout (s)</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="96" />
      <source>Time in seconds after which the cursor disappears.
Set to 0.00 to always hide the cursor.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="105" />
      <source>Crop</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="107" />
      <source>Left</source>
      <comment>Crop border label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="113" />
      <source>Pixels to crop from the left border of the target window.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="119" />
      <source>Top</source>
      <comment>Crop border label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="125" />
      <source>Pixels to crop from the top border of the target window.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="131" />
      <source>Right</source>
      <comment>Crop border label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="137" />
      <source>Pixels to crop from the right border of the target window.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="143" />
      <source>Bottom</source>
      <comment>Crop border label</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="149" />
      <source>Pixels to crop from the bottom border of the target window.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="156" />
      <source>Offset</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="159" />
      <source>X Offset</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="164" />
      <source>Y Offset</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="177" />
      <source>Horizontal offset in pixels (positive moves right, negative moves left).</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="182" />
      <source>Vertical offset in pixels (positive moves down, negative moves up).</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="190" />
      <source>Background Color</source>
      <comment>Settings section</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="194" />
      <source>Color</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/presentation.py" line="198" />
      <source>Background color behind the upscaled image (letterbox bars).
Supports transparency.</source>
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
      <location filename="../sidebars/profiles.py" line="135" />
      <source>Add profile (Ctrl+N)</source>
      <comment>Profile add action tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="141" />
      <source>Edit match criteria (Enter/F2)</source>
      <comment>Profile edit action tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="148" />
      <source>Delete profile (Del)</source>
      <comment>Profile delete action tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="156" />
      <source>Move up (Ctrl+Shift+Up)</source>
      <comment>Profile move up action tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="163" />
      <source>Move down (Ctrl+Shift+Down)</source>
      <comment>Profile move down action tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="280" />
      <source>Global</source>
      <comment>Global entry profile name</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="285" />
      <source>When selected, the settings panel on the right edits the global configuration.</source>
      <comment>Global entry profile tooltip</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="295" />
      <source>Global settings apply to all windows.

You can create a profile to override settings for a specific window, matched by its title or size.</source>
      <comment>No profile message</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/profiles.py" line="343" />
      <source>When selected, the settings panel on the right edits the settings overrides for '{0}'.</source>
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
      <source>Applied after SRCNN upscaling to reach the target output size (for example, 1440p → 4K).
• Lanczos-2 — sharp, best for 2D art and text (recommended)
• AMD FSR 1.0 — fast, best for 3D but may introduce artifacts on fine details
• NVIDIA Image Scaling — oversharpens and introduces ringing, not recommended</source>
      <comment>Description of a setting (tooltip). Do not translate the filter names (Lanczos-2, Lanczos-3, FSR, NIS).</comment>
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
• Catmull-Rom (bicubic) — sharp and fast, excellent tradeoff for most cases (recommended)
• Adaptive Lanczos — slower, best overall quality, handles extreme downscaling well</source>
      <comment>Description of a setting (tooltip). Do not translate the filter names (Catmull-Rom, Adaptive Lanczos).</comment>
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
Lower values are sharper but may ring; higher values are smoother.
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
Lower values preserve more detail but may allow ringing.
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
      <source>Use only the central 2x2 area for anti-ringing.
Keeps thin text and line art sharp. Turn off if you see ringing on high-contrast edges.</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="119" />
      <source>Override Lanczos Radius</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="123" />
      <source>Force a specific Lanczos kernel radius instead of automatic selection.
When off, the radius is chosen automatically (2 for upscaling, variable for downscaling).</source>
      <comment>Description of a setting (tooltip)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="130" />
      <source>Radius</source>
      <comment>Label of setting (must be short)</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../sidebars/tabs/scaler.py" line="140" />
      <source>Lanczos kernel radius (2 = standard Lanczos2, 3 = sharper 6-tap).
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
      <source>Semi-transparent background color of the central grid window titles.</source>
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
      <source>Reset Button</source>
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
      <source>Reset Button (hover)</source>
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
      <source>Fill color of scrollbar handles and other small controls.</source>
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
      <source>Fill color of scrollbar handles when hovered.</source>
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
      <comment>Description of a setting (tooltip). Preset names are not translated.</comment>
      <translation type="unfinished" />
    </message>
  </context>
  <context>
    <name>TrayController</name>
    <message>
      <location filename="../helpers/tray.py" line="403" />
      <location filename="../helpers/tray.py" line="48" />
      <source>Real-Time Upscaler</source>
      <comment>Name of the application</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="219" />
      <source>Unknown</source>
      <comment>Fallback if no window title was found</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="236" />
      <source>Stop</source>
      <comment>Stop action for tray icon menu</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="249" />
      <source>Hide</source>
      <comment>Hide action for tray icon menu</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="253" />
      <source>Show</source>
      <comment>Show action for tray icon menu</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="269" />
      <source>Daemon Mode</source>
      <comment>Daemon mode toggle for tray icon menu</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="283" />
      <source>Close to Tray</source>
      <comment>Tray menu option</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="292" />
      <source>Minimize to Tray</source>
      <comment>Tray menu option</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="301" />
      <source>Start Hidden</source>
      <comment>Tray menu option</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="312" />
      <source>Keep running after Exit hotkey</source>
      <comment>Tray menu option</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="329" />
      <source>Exit</source>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="390" />
      <source>Upscaling: '{0}'.
Use Stop from the tray menu to return.</source>
      <comment>Tray message if a window was already being upscaled. {0} is the window title placeholder.</comment>
      <translation type="unfinished" />
    </message>
    <message>
      <location filename="../helpers/tray.py" line="396" />
      <source>Upscaling in progress.
Use Stop from the tray menu to return.</source>
      <comment>Tray message if a window was already being upscaled and no window title was available to show.</comment>
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
