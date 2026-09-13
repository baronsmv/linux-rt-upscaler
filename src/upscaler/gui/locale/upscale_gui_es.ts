<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="es_ES">
<context>
    <name>AboutDialog</name>
    <message>
        <location filename="../dialogs/about.py" line="82"/>
        <source>About</source>
        <translation>Acerca de</translation>
    </message>
    <message>
        <location filename="../dialogs/about.py" line="107"/>
        <source>Real-Time Upscaler</source>
        <comment>Name of the application</comment>
        <translation>Escalador en Tiempo Real</translation>
    </message>
    <message>
        <location filename="../dialogs/about.py" line="114"/>
        <source>Version {0}</source>
        <comment>Version of the upscaler</comment>
        <translation>Versión {0}</translation>
    </message>
    <message>
        <location filename="../dialogs/about.py" line="122"/>
        <source>A real-time SRCNN upscaler for any X-Window on GNU/Linux.</source>
        <comment>Description of the upscaler</comment>
        <translation>Un escalador SRCNN en tiempo real para cualquier ventana X en GNU/Linux.</translation>
    </message>
    <message>
        <location filename="../dialogs/about.py" line="137"/>
        <source>Close</source>
        <comment>Close button</comment>
        <translation>Cerrar</translation>
    </message>
</context>
<context>
    <name>AdvancedTab</name>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="26"/>
        <source>Advanced</source>
        <comment>Name of a settings tab</comment>
        <translation>Avanzado</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="35"/>
        <source>Tile-based processing</source>
        <comment>Settings section</comment>
        <translation>Procesamiento por bloques</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="37"/>
        <source>Enable tile mode</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Habilitar procesamiento por bloques</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="42"/>
        <source>Process only the parts of the frame that have changed, using small tiles.
Best for mostly static content, such as text editors or visual novels.
When disabled, the entire frame is processed at once, better for video or fast-moving content.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Procesa sólo las partes del fotograma que han cambieado, usando pequeños bloques.
Esto es mejor para contenido más estático, como editores de texto o novelas visuales.
Cuando deshabilitado, el fotograma entero es procesado, lo que es mejor para videos o contenido dinámico.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="50"/>
        <source>Damage tracking</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Seguimiento de daño</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="55"/>
        <source>Send only the changed parts of the frame to the GPU, instead of the whole image.
Disable this if you see glitches that may be caused by missed updates.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Manda a la GPU sólo las partes del fotograma que han cambiado, en lugar de toda la imagen.
Deshabilita esto si ves artefactos que pudieran deberse a actualizaciones omitidas de la imagen.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="62"/>
        <source>Tile size</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Tamaño del bloque</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="69"/>
        <source>Size of each tile in pixels.
Smaller tiles update more precisely but use more CPU.
Values that are multiples of 32 usually perform best.
Recommended range: 32 - 128.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Tamaño (en píxeles) de cada uno de los bloques.
Bloques más pequeños actualizan con más precisión pero usan más CPU.
Valores múltiplos de 32 generalmente ofrecen mejor rendimiento.
Rango recomendado: 32 - 128.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="78"/>
        <source>Context margin</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Margen de contexto</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="85"/>
        <source>Extra pixels added around each tile to give the neural network more context.
Larger margins can improve quality at tile edges but increase processing.
Recommended range: 4 - 24.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Píxeles adicionales alrededor de cada bloque para proporcionar más contexto a la red neuronal.
Valores más amplios pueden mejorar la calidad en los bordes de los mosaicos, pero usan más GPU.
Rango recomendado: 4 - 24.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="93"/>
        <source>Max tiles per frame</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Límite de bloques</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="100"/>
        <source>Maximum number of changed tiles to process per frame.
If more tiles than this need updating, the whole frame will be processed instead.
Recommended range: 4 - 32.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Límite de bloques a procesar por fotograma.
Si es necesario actualizar más bloques que esta cantidad, se procesará el fotograma completo en su lugar.
Rango recomendado: 4 - 32.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="108"/>
        <source>Area threshold</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Umbral de área %</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="116"/>
        <source>If more than this percentage of the frame has changed, the whole frame will be processed instead of individual tiles.
Lower values switch to full-frame processing sooner.
Recommended range: 15% - 50%.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Si un fotograma cambia más que este porcentaje, se procesará el fotograma completo en lugar de bloques.
Valores más bajos cambian al procesamiento completo antes.
Rango recomendado: 15 % - 50 %.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="126"/>
        <source>Timing</source>
        <comment>Settings section</comment>
        <translation>Tiempo</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="128"/>
        <source>Frame timeout (ms)</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Espera de fotograma (ms)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="135"/>
        <source>Maximum time to wait for the GPU to finish the previous frame.
Lower values reduce waiting time but may cause dropped frames.
Recommended range: 17 (1/60 s) - 1000 (1 s).</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Tiempo máximo de espera para que la GPU termine un fotograma.
Valores bajos reducen el tiempo de espera pero puedo omitir fotogramas.
Rango recomendado: 17 (1/60 s) - 1000 (1 s).</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="143"/>
        <source>Daemon poll (s)</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Sondeo Demonio (s)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="151"/>
        <source>How often the background service checks for matching windows.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Con qué frecuencia el servicio en segundo plano busca ventanas coincidentes.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="157"/>
        <source>Focus poll (s)</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Sondeo de enfoque (s)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="165"/>
        <source>How often the program checks which window is currently active.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Con qué frecuencia el programa comprueba qué ventana está activa actualmente.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="171"/>
        <source>Pipeline idle (s)</source>
        <translation>Inactividad (s)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="179"/>
        <source>How often the program checks its internal state when no changes are detected.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Con qué frecuencia el programa comprueba su estado interno cuando no se detectan cambios.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="186"/>
        <source>Error Recovery</source>
        <comment>Settings section</comment>
        <translation>Recuperación de errores</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="188"/>
        <source>Max capture failures</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Límite de fallos de captura</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="196"/>
        <source>Number of consecutive frame capture failures before the program stops.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Número de fallos consecutivos en la captura de fotogramas antes de que el programa se detenga.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="202"/>
        <source>Capture failure delay (s)</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Retardo de fallos (s)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="210"/>
        <source>Delay after a capture failure before trying again.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Retraso tras un fallo de captura antes de volver a intentarlo.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="216"/>
        <source>Swapchain debounce (s)</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Espera de recreación (s)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/advanced.py" line="224"/>
        <source>Minimum time between two Vulkan swapchain recreations.
This prevents unnecessary rebuilds of the rendering pipeline.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Tiempo mínimo entre dos recreaciones de la cadena de intercambio (swapchain) de Vulkan.
Esto evita reconstrucciones innecesarias del pipeline de renderizado.</translation>
    </message>
</context>
<context>
    <name>ColorPickerRow</name>
    <message>
        <location filename="../sidebars/controls/color.py" line="97"/>
        <source>Choose Background Color</source>
        <translation>Elija un color de fondo</translation>
    </message>
</context>
<context>
    <name>ConfirmDialog</name>
    <message>
        <location filename="../dialogs/confirm.py" line="52"/>
        <source>Save them before closing, discard them, or cancel to stay.</source>
        <comment>Dialog secondary text</comment>
        <translation>Guárdalos antes de cerrar, descártalos, o cancela para permanecer.</translation>
    </message>
    <message>
        <location filename="../dialogs/confirm.py" line="57"/>
        <source>Save and close</source>
        <comment>Dialog button</comment>
        <translation>Guardar y cerrar</translation>
    </message>
    <message>
        <location filename="../dialogs/confirm.py" line="60"/>
        <source>Discard and close</source>
        <comment>Dialog button</comment>
        <translation>Descartar y cerrar</translation>
    </message>
    <message>
        <location filename="../dialogs/confirm.py" line="64"/>
        <source>Save them before switching, discard them, or cancel to stay.</source>
        <comment>Dialog secondary text</comment>
        <translation>Guárdalos antes de cambiar, descártalos, o cancela para permanecer.</translation>
    </message>
    <message>
        <location filename="../dialogs/confirm.py" line="69"/>
        <source>Save and switch</source>
        <comment>Dialog button</comment>
        <translation>Guardar y cambiar</translation>
    </message>
    <message>
        <location filename="../dialogs/confirm.py" line="72"/>
        <source>Discard and switch</source>
        <comment>Dialog button</comment>
        <translation>Descartar y cambiar</translation>
    </message>
    <message>
        <location filename="../dialogs/confirm.py" line="79"/>
        <source>Unsaved changes</source>
        <comment>Dialog title</comment>
        <translation>Cambios sin guardar</translation>
    </message>
    <message>
        <location filename="../dialogs/confirm.py" line="82"/>
        <source>You have unsaved changes in the current configuration.</source>
        <comment>Dialog main text</comment>
        <translation>Tienes cambios sin guardar en la configuración actual.</translation>
    </message>
    <message>
        <location filename="../dialogs/confirm.py" line="93"/>
        <source>Cancel</source>
        <comment>Dialog button</comment>
        <translation>Cancelar</translation>
    </message>
</context>
<context>
    <name>DisplayTab</name>
    <message>
        <location filename="../sidebars/tabs/display.py" line="33"/>
        <source>Auto (best)</source>
        <comment>GPU automatic device option</comment>
        <translation>Automático (mejor)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="36"/>
        <source>Display</source>
        <comment>Name of a settings tab</comment>
        <translation>Pantalla</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="45"/>
        <source>Devices</source>
        <comment>Settings section</comment>
        <translation>Dispositivos</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="47"/>
        <source>Monitor</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Monitor</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="53"/>
        <source>Monitor used for upscaling: the primary monitor, multi-monitor, or a specific output name (for example, HDMI-1).</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Monitor utilizado para el escalado: el monitor primario, multi-monitor, o un nombre específico (por ejemplo, HDMI-1).</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="66"/>
        <source>GPU</source>
        <comment>Label of setting (must be short)</comment>
        <translation>GPU</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="76"/>
        <source>GPU used for upscaling.
Select &apos;{0}&apos; to automatically use the most powerful available GPU.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Tarjeta gráfica utilizada para el escalado.
Selecciona &apos;{0}&apos; para utilizar automáticamente la GPU disponible más potente.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="84"/>
        <source>V-Sync</source>
        <comment>Settings section</comment>
        <translation>V-Sync</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="86"/>
        <source>Presentation mode</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Modo de presentación</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="92"/>
        <source>Vulkan presentation mode:
• fifo: VSync on, lowest power, no tearing
• mailbox: tear-free, lower latency, higher power
• immediate: no VSync, lowest latency, may tear</source>
        <comment>Description of a setting (tooltip). Do not translate fifo, mailbox and immediate: they are Vulkan presentation mode identifiers.</comment>
        <translation>Modos de presentación de Vulkan:
• fifo: VSync activado, menor consumo de energía, sin tearing
• mailbox: sin *tearing*, menor latencia, mayor consumo de energía
• immediate: sin VSync, latencia mínima, posible tearing</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="103"/>
        <source>Limit FPS</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Limitar FPS</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="108"/>
        <source>Enable a maximum frame rate.
For best results, use the &apos;mailbox&apos; presentation mode when limiting FPS.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Habilita una velocidad de fotogramas máxima.
Para obtener mejores resultados, usa el modo de presentación &apos;mailbox&apos; al limitar FPS.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="115"/>
        <source>Max FPS</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Límite de FPS</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="126"/>
        <source>Target maximum frames per second.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Velocidad de fotogramas máxima.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="134"/>
        <source>Scale factor</source>
        <comment>Settings section</comment>
        <translation>Factor de escala</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="136"/>
        <source>Auto scale</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Auto-escalado</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="141"/>
        <source>Automatically detect the correct scale factor based on the physical monitor resolution.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Detecta automáticamente el factor de escala correcto, basado en la resolutión del monitor físico.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="147"/>
        <source>Scale factor</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Factor de escala</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/display.py" line="159"/>
        <source>Set the scale factor manually as a percentage (for example, 1.50 for 150% scaling).
Only available when Auto Scale is off.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Factor de escala manual, como un porcentaje (por ejemplo, 1.50 para una escala del 150%).
Solo disponible cuando Auto-escala está desactivada.</translation>
    </message>
</context>
<context>
    <name>EffectsTab</name>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="26"/>
        <source>Effects</source>
        <comment>Name of a settings tab</comment>
        <translation>Efectos</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="35"/>
        <source>Debanding</source>
        <comment>Settings section</comment>
        <translation>Supresión de bandas</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="37"/>
        <source>Enable deband</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Habilitar supresión de bandas</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="42"/>
        <source>Reduce banding in smooth gradients before upscaling.
Only useful if you notice banding in skies, fog, and other large smooth areas.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Elimina bandas de color en degradados suaves antes del escalado.
Solo es útil si observas bandas de color (color banding) en cielos, niebla y otras áreas uniformes.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="232"/>
        <location filename="../sidebars/tabs/effects.py" line="169"/>
        <location filename="../sidebars/tabs/effects.py" line="108"/>
        <location filename="../sidebars/tabs/effects.py" line="78"/>
        <location filename="../sidebars/tabs/effects.py" line="49"/>
        <source>Strength</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Magnitud</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="57"/>
        <source>Debanding intensity.
Recommended range: 0.10 - 0.30.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Intensidad de la eliminación de bandas de color.
Rango recomendado: 0.10 - 0.30.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="65"/>
        <source>CAS sharpening</source>
        <comment>Settings section</comment>
        <translation>Contraste CAS</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="67"/>
        <source>Enable CAS</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Habilitar CAS</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="72"/>
        <source>Contrast Adaptive Sharpening: enhances text and line art contrast.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Contrast Adaptive Sharpening: mejora el contraste del texto y del arte lineal.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="86"/>
        <source>Sharpening amount.
Recommended range: 0.20 - 0.50.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Magnitud del contraste.
Rango recomendado: 0.20 - 0.50.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="94"/>
        <source>Bloom (glow)</source>
        <comment>Settings section</comment>
        <translation>Resplandor (brillo)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="96"/>
        <source>Enable bloom</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Habilitar resplandor</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="101"/>
        <source>Soft glow around bright areas, for a cinematic look.
May introduce halos, especially with white text.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Un suave resplandor alrededor de zonas brillantes, que crea un efecto cinematográfico.
Puede generar halos, especialmente con texto blanco.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="116"/>
        <source>Bloom intensity.
Recommended range: 0.02 - 0.06.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Intensidad del resplandor.
Rango recomendado: 0.02 - 0.06.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="124"/>
        <source>Threshold</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Límite</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="132"/>
        <source>Brightness cutoff for bloom.
Only pixels brighter than this value will glow.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Umbral de brillo.
Solo píxeles más brillantes que este valor emitirán resplandor.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="185"/>
        <location filename="../sidebars/tabs/effects.py" line="141"/>
        <source>Radius</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Radio</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="148"/>
        <source>Blur radius in pixels. Larger radii spread the glow further.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Radio del resplandor en píxeles. Radios mayores extienden más el resplandor.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="156"/>
        <source>Vignette</source>
        <comment>Settings section</comment>
        <translation>Viñetado</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="158"/>
        <source>Enable vignette</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Habilitar viñetado</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="163"/>
        <source>Radial darkening of screen edges, drawing focus to the center.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Oscurecimiento radial de los bordes de la pantalla, dirigiendo la atención hacia el centro.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="177"/>
        <source>Edge darkening intensity.
Recommended range: 0.30 - 0.60.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Intensidad del oscurecimiento de los bordes.
Rango recomendado: 0.30 - 0.60.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="193"/>
        <source>Distance from center where darkening begins.
Higher values keep the center brighter.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Distancia desde el centro donde comienza el oscurecimiento.
Valores más altos mantienen el centro más brillante.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="202"/>
        <source>Falloff</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Atenuación</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="210"/>
        <source>Softness of the vignette transition. Low values = gentle, high values = sharp ring.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Suavidad de la transición del viñeteado.
Valores bajos lo hacen más suave, mientras que valores altos lo definen con más intensidad.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="219"/>
        <source>Film grain</source>
        <comment>Settings section</comment>
        <translation>Grano de película</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="221"/>
        <source>Enable grain</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Habilitar grano de película</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="226"/>
        <source>Simulated film grain look.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Apariencia de grano de película.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="240"/>
        <source>Grain intensity.
Recommended range: 0.10 - 0.20.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Intensidad del grano de película.
Rango recomendado: 0.10 - 0.20.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="248"/>
        <source>Size</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Tamaño</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="256"/>
        <source>Particle size of the grain.
Larger values produce coarser, more visible grain.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Tamaño de partícula del grano de película.
Valores más altos producen un grano más grueso y visible.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="265"/>
        <source>Color grading</source>
        <comment>Settings section</comment>
        <translation>Ajuste de color (3D LUT)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="267"/>
        <source>Enable LUT</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Habilitar LUT</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="272"/>
        <source>Apply a color grading preset (LUT) to change the look of the window.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Aplica un ajuste preestablecido de gradación de color (LUT) para cambiar el aspecto de la ventana.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="278"/>
        <source>Preset</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Ajuste preestablecido</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="284"/>
        <source>Built-in color grading preset (warm, cool, film, sepia, etc.).</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Ajuste preestablecido de gradación de color integrado (cálido (warm, frío (cool), cine (film), sepia, etc.).</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="292"/>
        <source>Intensity</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Intensidad</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/effects.py" line="300"/>
        <source>Blend between original and graded image.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Mezcla entre la imagen original y la gradación de color.</translation>
    </message>
</context>
<context>
    <name>ExtrasTab</name>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="25"/>
        <source>Extras</source>
        <comment>Name of a settings tab</comment>
        <translation>Extras</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="34"/>
        <source>Screenshot</source>
        <comment>Settings section</comment>
        <translation>Capturas de pantalla</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="36"/>
        <source>Directory</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Directorio</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="41"/>
        <source>Folder where screenshots are saved.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Directorio donde las capturas de pantalla son guardadas.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="47"/>
        <source>Template</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Plantilla</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="52"/>
        <source>Filename template for screenshots. You can use these placeholders:
• {timestamp}: capture time (supports strftime, for example {timestamp:%Y-%m-%d-%H-%M-%S})
• {title}: current window title
• {profile}: active profile name (or the window title if no profile)
• {model}: active upscaling model
• {width}: upscaled image width
• {height}: upscaled image height</source>
        <comment>Description of a setting (tooltip). Keep all placeholders exactly as they are, including braces, for example {timestamp} and the strftime format inside it.</comment>
        <translation>Plantilla de nombre de archivo para capturas de pantalla. Puedes utilizar estos marcadores de posición:
• {timestamp}: hora de la captura (admite strftime; por ejemplo, {timestamp:%Y-%m-%d-%H-%M-%S})
• {title}: título de la ventana actual
• {profile}: nombre del perfil activo (o el título de la ventana si no hay perfil)
• {model}: modelo de escalado activo
• {width}: anchura de la imagen escalada
• {height}: altura de la imagen escalada</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="68"/>
        <source>On-Screen Display</source>
        <comment>Settings section</comment>
        <translation>Mensajes en pantalla</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="70"/>
        <source>Show OSD</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Mostrar OSD</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="75"/>
        <source>Show on-screen messages when the model, window geometry, or zoom changes, or after taking a screenshot.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Muestra mensajes en pantalla cuando se cambia el modelo, la geometría de la ventana o el zoom, o al realizar una captura de pantalla.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="82"/>
        <source>Duration (s)</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Duración (s)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/extras.py" line="90"/>
        <source>How many seconds on-screen messages remain visible before fading out.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Cuántos segundos permanecen visibles los mensajes en pantalla antes de desvanecerse.</translation>
    </message>
</context>
<context>
    <name>FilterBar</name>
    <message>
        <location filename="../grid/filter.py" line="35"/>
        <source>Filter windows</source>
        <comment>Filter windows search bar placeholder</comment>
        <translation>Filtrar ventanas</translation>
    </message>
</context>
<context>
    <name>FontPickerDialog</name>
    <message>
        <location filename="../dialogs/font.py" line="36"/>
        <source>Select font</source>
        <comment>Font picker dialog title</comment>
        <translation>Seleccionar fuente</translation>
    </message>
    <message>
        <location filename="../dialogs/font.py" line="46"/>
        <source>Filter</source>
        <comment>Font picker filter placeholder</comment>
        <translation>Filtro</translation>
    </message>
    <message>
        <location filename="../dialogs/font.py" line="60"/>
        <source>Preview</source>
        <comment>Font picker preview label</comment>
        <translation>Previsualización</translation>
    </message>
    <message>
        <location filename="../dialogs/font.py" line="64"/>
        <source>The quick brown fox jumps over the lazy dog. 0123456789</source>
        <comment>Font picker preview text</comment>
        <translatorcomment>Used a common spanish pangram used by KDE and others.</translatorcomment>
        <translation>Jovencillo emponzoñado de whisky, ¡qué figurota exhibe!</translation>
    </message>
</context>
<context>
    <name>FontPickerRow</name>
    <message>
        <location filename="../sidebars/controls/font.py" line="66"/>
        <source>Reset to system font</source>
        <comment>Font row reset tooltip</comment>
        <translation>Restablecer a la fuente del sistema</translation>
    </message>
</context>
<context>
    <name>GeneralTab</name>
    <message>
        <location filename="../sidebars/tabs/general.py" line="32"/>
        <source>General</source>
        <comment>Name of a settings tab</comment>
        <translation>General</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="41"/>
        <source>Upscaling model</source>
        <comment>Settings section</comment>
        <translation>Modelo de escalado</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="43"/>
        <source>Model</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Modelo</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="49"/>
        <source>Upscaling SRCNN model to use.
All models upscale to 2x, and are ordered from lowest to highest quality.
Rightmost models are deeper and slower, but produce better results.
The value &apos;none&apos; disables SRCNN processing and uses only the selected scaler (upsampler/downsampler).</source>
        <comment>Description of a setting (tooltip). Do not translate &apos;none&apos;, since it&apos;s a model identifier</comment>
        <translation>Modelo SRCNN de escalado a utilizar.
Todos los modelos realizan un escalado 2x y están ordenados de menor a mayor calidad.
Los modelos más a la derecha son más profundos y lentos, pero ofrecen mejores resultados.
El valor &apos;none&apos; desactiva el procesamiento SRCNN y utiliza únicamente el remuestrador seleccionado (sobremuestrador/submuestrador).</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="59"/>
        <source>Double upscale (4x)</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Escalado doble (4x)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="64"/>
        <source>Perform two 2x upscales in a row for a total of 4x (for example, 720p to 2880p).
Useful for high-resolution screens (4K) and low-resolution sources.
Uses more GPU power.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Realiza dos escalados 2x consecutivos para obtener un total de 4x (por ejemplo, de 720p a 2880p).
Útil para pantallas de alta resolución (4K) y fuentes de baja resolución.
Consume más recursos de la GPU.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="74"/>
        <source>Focus tracking</source>
        <comment>Settings section</comment>
        <translation>Seguimiento del enfoque</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="76"/>
        <source>Follow focus</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Seguir enfoque</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="81"/>
        <source>Automatically upscale the window that currently has focus.
Useful when working with multiple windows.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Escala automáticamente la ventana que tenga el foco actualmente.
Útil al trabajar con varias ventanas.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="88"/>
        <source>Pause on focus loss</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Pausa al perder foco</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="93"/>
        <source>Hide the upscaled overlay when the target window loses focus, and show it again when focus returns.
Turn off to keep the overlay always visible.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Oculta la ventana de escalado cuando la ventana original pierde el foco, y vuelve a mostrarla cuando lo recupere.
Desactive esta opción para mantener la ventana de escalado siempre visible.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="101"/>
        <source>Automatic Upscaling</source>
        <comment>Settings section</comment>
        <translation>Escalado Automático</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="104"/>
        <source>Exclude from daemon mode</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Excluir de modo daemon</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="109"/>
        <source>When daemon mode is active, this profile will not be used to automatically upscale matching windows.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Cuando el modo daemon está activo, este perfil no se utilizará para escalar automáticamente las ventanas que coincidan.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="117"/>
        <source>Daemon mode</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Modo daemon</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/general.py" line="122"/>
        <source>When enabled, a background process automatically upscales any window that matches a profile.
Turn off to manually select a window from the grid.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Si esta opción está habilitada, un proceso en segundo plano escalará automáticamente cualquier ventana que coincida con un perfil.
Desactive esta opción para seleccionar manualmente una ventana de la cuadrícula.</translation>
    </message>
</context>
<context>
    <name>HotkeyCaptureButton</name>
    <message>
        <location filename="../sidebars/controls/hotkey.py" line="171"/>
        <source>Press keys…</source>
        <comment>Hotkey recording prompt</comment>
        <translation>Presione teclas…</translation>
    </message>
    <message>
        <location filename="../sidebars/controls/hotkey.py" line="214"/>
        <source>Needs a modifier</source>
        <comment>Hotkey recording error</comment>
        <translation>Requiere un modificador</translation>
    </message>
    <message>
        <location filename="../sidebars/controls/hotkey.py" line="255"/>
        <source>(unbound)</source>
        <comment>Displayed when no hotkey is bound</comment>
        <translation>(sin asignar)</translation>
    </message>
</context>
<context>
    <name>HotkeyRow</name>
    <message>
        <location filename="../sidebars/controls/hotkey.py" line="296"/>
        <source>Clear binding</source>
        <comment>Hotkey row clear button tooltip</comment>
        <translation>Borrar asignación</translation>
    </message>
</context>
<context>
    <name>HotkeysTab</name>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="28"/>
        <source>Hotkeys</source>
        <comment>Name of a settings tab</comment>
        <translation>Teclas de acceso rápido</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="38"/>
        <source>Session</source>
        <comment>Hotkey group title</comment>
        <translation>Sesión</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="39"/>
        <source>View</source>
        <comment>Hotkey group title</comment>
        <translation>Vista</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="40"/>
        <source>Zooming</source>
        <comment>Hotkey group title</comment>
        <translation>Zoom</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="41"/>
        <source>Panning</source>
        <comment>Hotkey group title</comment>
        <translation>Desplazamiento</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="48"/>
        <source>Show/hide</source>
        <comment>Hotkey action label</comment>
        <translation>Mostrar/ocultar</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="49"/>
        <source>Show or hide the upscaled overlay window.</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Mostrar u ocultar la ventana de escalado.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="55"/>
        <source>Exit session</source>
        <comment>Hotkey action label</comment>
        <translation>Cerrar sesión</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="56"/>
        <source>Close the overlay and end the current upscaling session.</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Cierra la ventana de escalado y finaliza la sesión.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="62"/>
        <source>Take screenshot</source>
        <comment>Hotkey action label</comment>
        <translation>Capturar pantalla</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="63"/>
        <source>Save the current upscaled output as an image.</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Guarda la salida escalada del modelo como una imagen.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="69"/>
        <source>Change model</source>
        <comment>Hotkey action label</comment>
        <translation>Cambiar modelo</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="70"/>
        <source>Switch to the next SRCNN upscaling model.</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Cambia al siguiente modelo de escalado SRCNN.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="76"/>
        <source>Change geometry</source>
        <comment>Hotkey action label</comment>
        <translation>Cambiar geometría</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="77"/>
        <source>Cycle through output sizing modes (fit, stretch, cover).</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Alterna entre las geometrías de salida (fit, stretch, cover).</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="83"/>
        <source>Restore view</source>
        <comment>Hotkey action label</comment>
        <translation>Restaurar vista</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="84"/>
        <source>Reset geometry, zoom and pan offsets to their initial values.</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Restablece la geometría, desplazamiento y zoom a sus valores iniciales.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="90"/>
        <source>Zoom in</source>
        <comment>Hotkey action label</comment>
        <translation>Acercar</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="91"/>
        <source>Increase the output zoom level.</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Aumenta el nivel de zoom.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="97"/>
        <source>Zoom out</source>
        <comment>Hotkey action label</comment>
        <translation>Alejar</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="98"/>
        <source>Decrease the output zoom level.</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Disminuye el nivel de zoom.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="104"/>
        <source>Pan up</source>
        <comment>Hotkey action label</comment>
        <translation>Hacia arriba</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="105"/>
        <source>Move the content up.</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Mueve el contenido hacia arriba.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="111"/>
        <source>Pan down</source>
        <comment>Hotkey action label</comment>
        <translation>Hacia abajo</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="112"/>
        <source>Move the content down.</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Mueve el contenido hacia abajo.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="118"/>
        <source>Pan left</source>
        <comment>Hotkey action label</comment>
        <translation>Hacia la izquierda</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="119"/>
        <source>Move the content to the left.</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Mueve el contenido hacia la izquierda.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="125"/>
        <source>Pan right</source>
        <comment>Hotkey action label</comment>
        <translation>Hacia la derecha</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/hotkeys.py" line="126"/>
        <source>Move the content to the right.</source>
        <comment>Hotkey action description (tooltip)</comment>
        <translation>Mueve el contenido hacia la derecha.</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../main.py" line="96"/>
        <source>Real-Time Upscaler</source>
        <comment>Name of the application</comment>
        <translation>Escalador en Tiempo Real</translation>
    </message>
    <message>
        <location filename="../main.py" line="155"/>
        <source>Enable/disable system tray</source>
        <comment>Tray toggle button</comment>
        <translation>Habilitar/Deshabilitar la bandeja del sistema</translation>
    </message>
    <message>
        <location filename="../main.py" line="167"/>
        <source>About Real-Time Upscaler</source>
        <comment>About dialog button</comment>
        <translation>Acerca de Escalador en Tiempo Real.</translation>
    </message>
    <message>
        <location filename="../main.py" line="417"/>
        <source>Error</source>
        <comment>Error starting pipeline</comment>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../main.py" line="418"/>
        <source>Could not start pipeline:
{0}</source>
        <comment>Error starting pipeline</comment>
        <translation>No se pudo inicializar el programa:
{0}</translation>
    </message>
    <message>
        <location filename="../main.py" line="614"/>
        <source>Save Error</source>
        <comment>Error while saving configuration</comment>
        <translation>Error al guardar</translation>
    </message>
    <message>
        <location filename="../main.py" line="615"/>
        <source>Could not save:
{0}</source>
        <comment>Error while saving configuration</comment>
        <translation>No se pudo guardar:
{0}</translation>
    </message>
</context>
<context>
    <name>PathPickerRow</name>
    <message>
        <location filename="../sidebars/controls/path.py" line="52"/>
        <source>Select directory</source>
        <comment>Path selector placeholder</comment>
        <translation>Seleccionar un directorio</translation>
    </message>
    <message>
        <location filename="../sidebars/controls/path.py" line="64"/>
        <source>Browse for directory.</source>
        <comment>Path selector placeholder</comment>
        <translation>Buscar directorio.</translation>
    </message>
    <message>
        <location filename="../sidebars/controls/path.py" line="112"/>
        <source>Choose screenshot directory</source>
        <comment>Screenshot directory dialog title</comment>
        <translation>Elegir directorio de capturas de pantalla</translation>
    </message>
</context>
<context>
    <name>PresentationTab</name>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="27"/>
        <source>Presentation</source>
        <comment>Name of a settings tab</comment>
        <translation>Presentación</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="36"/>
        <source>Overlay</source>
        <comment>Settings section</comment>
        <translation>Ventana de escalado</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="38"/>
        <source>Overlay mode</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Modo de ventana</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="44"/>
        <source>Overlay window behaviour:
• always-on-top: always visible above other windows, keeps focus on the target window (recommended)
• top-transparent: same as always-on-top, but click-through (mouse passes to window below)
• fullscreen: covers entire monitor, keyboard may not reach the target window
• windowed: normal window with decorations, keyboard may not reach the target window</source>
        <comment>Description of a setting (tooltip). Do not translate &apos;always-on-top&apos;, &apos;top-transparent&apos;, &apos;fullscreen&apos;, &apos;windowed&apos;: they are internal overlay mode identifiers.</comment>
        <translation>Comportamiento de la ventana de escalado:
• &apos;always-on-top&apos;: siempre visible encima de otras ventanas, mantiene el foco en la ventana de destino (recomendado)
• &apos;top-transparent&apos;: igual que &apos;always-on-top&apos;, pero los clicks del mouse pasan a la ventana debajo
• &apos;fullscreen&apos;: cubre todo el monitor, es posible que los eventos de teclado no lleguen a la ventana de destino
• &apos;windowed&apos;: ventana normal con decoraciones, es posible que los eventos de teclado no lleguen a la ventana de destino</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="56"/>
        <source>Output geometry</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Geometría de salida</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="62"/>
        <source>How the upscaled content fits the overlay:
• fit: show the entire image, adding black bars if necessary
• stretch: fill the whole area, aspect ratio may be distorted
• cover: fill the whole area and crop any excess</source>
        <comment>Description of a setting (tooltip). Do not translate &apos;fit&apos;, &apos;stretch&apos;, &apos;cover&apos;: they are internal output geometry identifiers.</comment>
        <translation>Cómo se ajusta el contenido a la ventana de escalado:
• ajustar (&apos;fit&apos;): mostrar la imagen completa, añadiendo franjas negras si es necesario
• estirar (&apos;stretch&apos;): llenar toda el área; aunque la relación de aspecto pueda verse distorsionada
• cubrir (&apos;cover&apos;): llenar toda el área y recortar el exceso</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="74"/>
        <source>Cursor</source>
        <comment>Settings section</comment>
        <translation>Cursor</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="76"/>
        <source>Hide cursor</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Esconder cursor</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="81"/>
        <source>Automatically hide the mouse cursor after a period of inactivity.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Ocultar automáticamente el cursor del ratón tras un periodo de inactividad.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="94"/>
        <source>Hide timeout (s)</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Periodo de inactividad (s)</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="102"/>
        <source>Time in seconds after which the cursor disappears.
Set to 0.00 to always hide the cursor.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Tiempo en segundos tras el cual desaparece el cursor.
Un valor de 0.00 mantiene el cursor siempre oculto.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="111"/>
        <source>Crop</source>
        <comment>Settings section</comment>
        <translation>Recorte de bordes</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="113"/>
        <source>Top</source>
        <comment>Crop border label</comment>
        <translation>Superior</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="120"/>
        <source>Pixels to crop from the top border of the target window.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Píxeles a recortar desde el borde superior de la ventana de destino.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="126"/>
        <source>Bottom</source>
        <comment>Crop border label</comment>
        <translation>Inferior</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="133"/>
        <source>Pixels to crop from the bottom border of the target window.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Píxeles a recortar desde el borde inferior de la ventana de destino.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="139"/>
        <source>Left</source>
        <comment>Crop border label</comment>
        <translation>Izquierdo</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="146"/>
        <source>Pixels to crop from the left border of the target window.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Píxeles a recortar desde el borde izquierdo de la ventana de destino.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="152"/>
        <source>Right</source>
        <comment>Crop border label</comment>
        <translation>Derecho</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="159"/>
        <source>Pixels to crop from the right border of the target window.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Píxeles a recortar desde el borde derecho de la ventana de destino.</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="166"/>
        <source>Offset</source>
        <comment>Settings section</comment>
        <translation>Desplazamiento</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="169"/>
        <source>X offset</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Eje X</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="174"/>
        <source>Y offset</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Eje Y</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="188"/>
        <source>Horizontal offset in pixels (positive moves right, negative moves left).</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Desplazamiento horizontal en píxeles (positivo mueve a la derecha, negativo mueve a la izquierda).</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="193"/>
        <source>Vertical offset in pixels (positive moves down, negative moves up).</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Desplazamiento vertical en píxeles (positivo mueve hacia abajo, negativo mueve hacia arriba).</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="201"/>
        <source>Background color</source>
        <comment>Settings section</comment>
        <translation>Color de fondo</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="205"/>
        <source>Color</source>
        <comment>Label of setting (must be short)</comment>
        <translation>Color</translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/presentation.py" line="210"/>
        <source>Background color behind the upscaled image (letterbox bars).
Supports transparency.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation>Color de fondo detrás de la imagen escalada (franjas tipo &quot;letterbox&quot;).
Admite transparencia.</translation>
    </message>
</context>
<context>
    <name>ProfileActions</name>
    <message>
        <location filename="../helpers/profiles.py" line="237"/>
        <location filename="../helpers/profiles.py" line="154"/>
        <location filename="../helpers/profiles.py" line="102"/>
        <source>Error</source>
        <comment>Error dialog title</comment>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="105"/>
        <source>Could not add profile.</source>
        <comment>Error while adding profile</comment>
        <translation>No se pudo añadir el perfil.</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="157"/>
        <source>Could not duplicate profile.</source>
        <comment>Error while duplicating profile</comment>
        <translation>No se pudo duplicar el perfil.</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="166"/>
        <source>{0} (copy)</source>
        <comment>Suggested name for a duplicated profile. {0} is the source name.</comment>
        <translation>{0} (copia)</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="175"/>
        <source>{0} (copy {1})</source>
        <comment>Suggested name for a duplicated profile when the plain &apos;copy&apos; name is taken. {0} is the source name, {1} is a counter.</comment>
        <translation>{0} (copia {1})</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="204"/>
        <source>Duplicate name</source>
        <comment>Error dialog title</comment>
        <translation>Nombre duplicado</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="207"/>
        <source>A profile named &apos;{0}&apos; already exists.</source>
        <comment>Error while adding profile</comment>
        <translation>Ya existe un perfil llamado &apos;{0}&apos;.</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="240"/>
        <source>Could not edit profile.</source>
        <comment>Error while editing profile</comment>
        <translation>No se pudo editar el perfil.</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="253"/>
        <source>Delete profile</source>
        <comment>Dialog title</comment>
        <translation>Eliminar perfil</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="258"/>
        <source>Delete the profile &apos;{0}&apos;?</source>
        <comment>Dialog main text</comment>
        <translation>¿Eliminar el perfil &apos;{0}&apos;?</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="265"/>
        <source>This action cannot be undone.</source>
        <comment>Dialog secondary text</comment>
        <translation>Esta acción no se puede deshacer.</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="273"/>
        <source>Delete</source>
        <comment>Dialog button</comment>
        <translation>Eliminar</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="277"/>
        <source>Cancel</source>
        <comment>Dialog button</comment>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="361"/>
        <location filename="../helpers/profiles.py" line="337"/>
        <location filename="../helpers/profiles.py" line="318"/>
        <location filename="../helpers/profiles.py" line="299"/>
        <source>Error</source>
        <comment>Error window title</comment>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="302"/>
        <source>Could not delete profile.</source>
        <comment>Error while deleting profile</comment>
        <translation>No se pudo eliminar el perfil.</translation>
    </message>
    <message>
        <location filename="../helpers/profiles.py" line="364"/>
        <location filename="../helpers/profiles.py" line="340"/>
        <location filename="../helpers/profiles.py" line="321"/>
        <source>Could not reorder profiles.</source>
        <comment>Error while reordering profiles</comment>
        <translation>No se pudo reordenar los perfiles.</translation>
    </message>
</context>
<context>
    <name>ProfileDialog</name>
    <message>
        <location filename="../dialogs/profile.py" line="68"/>
        <source>New profile</source>
        <comment>Window title of the profile creator</comment>
        <translation>Nuevo perfil</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="70"/>
        <source>Edit profile</source>
        <comment>Window title of the profile editor</comment>
        <translation>Editar perfil</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="108"/>
        <source>Name</source>
        <comment>Profile dialog label of profile &apos;Name&apos;</comment>
        <translation>Nombre</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="114"/>
        <source>Profile name</source>
        <comment>Profile name label</comment>
        <translation>Nombre de perfil</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="117"/>
        <source>A unique name for this profile. Required.</source>
        <comment>Tooltip of profile name text input</comment>
        <translation>Un nombre único para este perfil. Obligatorio.</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="127"/>
        <source>Icon</source>
        <comment>Label of Icon button</comment>
        <translation>Ícono</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="173"/>
        <source>Capture window</source>
        <comment>&apos;Capture window&apos; button</comment>
        <translation>Capturar ventana</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="188"/>
        <source>Fill name, icon, and match rules from a window.</source>
        <comment>Capture window tooltip</comment>
        <translation>Completa el nombre, el ícono y las reglas de coincidencia desde una ventana.</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="200"/>
        <source>Capture icon from window</source>
        <comment>Capture icon tooltip</comment>
        <translation>Capturar ícono desde una ventana</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="206"/>
        <source>Load icon from file</source>
        <comment>Load icon tooltip</comment>
        <translation>Cargar ícono desde un archivo</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="212"/>
        <source>Remove icon</source>
        <comment>Remove icon tooltip</comment>
        <translation>Eliminar ícono</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="218"/>
        <source>Match rules</source>
        <comment>Match rules group label</comment>
        <translation>Reglas de coincidencia</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="220"/>
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
        <translation>Todas las reglas definidas deben cumplirse para que se aplique el perfil (lógica AND).
Ejemplos:
• Coincide con cualquier ventana de Firefox de más de 1280 px de ancho:
    • Título (exacto): Firefox
    • Ancho: &gt;1280
• Coincide con cualquier ventana de VLC (independientemente de su tamaño):
    • Título contiene: VLC
• Coincide con ventanas de emuladores de entre 720 px y 1080 px de altura:
    • Título (regex): (Yuzu|Ryujinx).*
    • Alto: 720-1080</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="241"/>
        <source>Title (exact):</source>
        <comment>Match rule label</comment>
        <translation>Título (exacto):</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="242"/>
        <source>e.g., Steam</source>
        <comment>Match rule placeholder</comment>
        <translation>ej., Steam</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="244"/>
        <source>Match if the window title exactly equals this text (case-insensitive).</source>
        <comment>Match rule tooltip</comment>
        <translation>Coincide si el título de la ventana es exactamente igual a este texto (sin distinguir entre mayúsculas y minúsculas).</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="254"/>
        <source>Title contains:</source>
        <comment>Match rule label</comment>
        <translation>Título contiene:</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="255"/>
        <source>e.g., VLC</source>
        <comment>Match rule placeholder</comment>
        <translation>ej., VLC</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="257"/>
        <source>Match if the window title contains this text (case-insensitive).</source>
        <comment>Match rule tooltip</comment>
        <translation>Coincide si el título de la ventana contiene este texto (sin distinguir entre mayúsculas y minúsculas).</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="266"/>
        <source>Title (regex):</source>
        <comment>Match rule label</comment>
        <translation>Título (regex):</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="267"/>
        <source>e.g., (Yuzu|Ryujinx).*</source>
        <comment>Match rule placeholder</comment>
        <translation>ej., (Yuzu|Ryujinx).*</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="269"/>
        <source>Match if the window title matches this regular expression (case-insensitive).</source>
        <comment>Match rule tooltip</comment>
        <translation>Coincide si el título de la ventana coincide con esta expresión regular (sin distinguir entre mayúsculas y minúsculas).</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="280"/>
        <source>Width:</source>
        <comment>Match rule label</comment>
        <translation>Ancho:</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="281"/>
        <source>e.g., &gt;1280</source>
        <comment>Match rule placeholder</comment>
        <translation>ej., &gt;1280</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="283"/>
        <source>Match if the window width satisfies this condition:
• Exact: 1920
• Comparison: &lt;800, &gt;1024, &lt;=1366, &gt;=1920
• Range: 1280-1920, 720..1080, 1024,1366</source>
        <comment>Match rule tooltip</comment>
        <translation>Coincide si el ancho de la ventana cumple esta condición:
• Exacto: 1920
• Comparación: &lt;800, &gt;1024, &lt;=1366, &gt;=1920
• Rango: 1280-1920, 720..1080, 1024,1366</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="295"/>
        <source>Height:</source>
        <comment>Match rule label</comment>
        <translation>Alto:</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="296"/>
        <source>e.g., &gt;800</source>
        <comment>Match rule placeholder</comment>
        <translation>ej., &gt;800</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="298"/>
        <source>Match if the window height satisfies this condition:
• Exact: 1080
• Comparison: &lt;600, &gt;900, &lt;=768, &gt;=1440
• Range: 480-1080, 600..900, 720,1024</source>
        <comment>Match rule tooltip</comment>
        <translation>Coincide si la altura de la ventana cumple esta condición:
• Exacta: 1080
• Comparación: &lt;600, &gt;900, &lt;=768, &gt;=1440
• Rango: 480-1080, 600..900, 720,1024</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="310"/>
        <source>Profiles let you override settings for specific windows and setups.
A profile is applied automatically when the upscaled window matches all the rules defined here, or when manually selected before upscaling.
Profiles are checked top-to-bottom: the first match wins.
Leave a rule blank to ignore that property.</source>
        <comment>Profile note</comment>
        <translation>Los perfiles permiten cambiar la configuración para ventanas y configuraciones específicas.
Un perfil se aplica automáticamente cuando la ventana escalada cumple todas las reglas definidas aquí, o cuando se selecciona manualmente antes del escalado.
Los perfiles se evalúan de arriba a abajo: la primera coincidencia gana.
Deja una regla en blanco para ignorar esa propiedad.</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="459"/>
        <source>No icon</source>
        <comment>No icon warning</comment>
        <translation>Sin ícono</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="460"/>
        <source>The selected window has no icon.</source>
        <comment>No icon warning</comment>
        <translation>La ventana seleccionada no tiene icono.</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="478"/>
        <source>Select Icon</source>
        <comment>Select Icon dialog title</comment>
        <translation>Selecciona un ícono</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="487"/>
        <source>Invalid image</source>
        <comment>Invalid image warning</comment>
        <translation>Imagen no válida</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="488"/>
        <source>Could not load the selected file.</source>
        <comment>Invalid image warning</comment>
        <translation>No se pudo cargar el archivo seleccionado.</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="527"/>
        <source>Missing name</source>
        <comment>Warning while saving a profile without name</comment>
        <translation>Nombre faltante</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="528"/>
        <source>Profile name cannot be empty.</source>
        <comment>Warning while saving a profile without name</comment>
        <translation>El nombre del perfil no puede estar vacío.</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="540"/>
        <source>Duplicate name</source>
        <comment>Warning while saving a profile with an existing name</comment>
        <translation>Nombre duplicado</translation>
    </message>
    <message>
        <location filename="../dialogs/profile.py" line="544"/>
        <source>A profile named &apos;{0}&apos; already exists.
Please choose a different name.</source>
        <comment>Warning while saving a profile with an existing name</comment>
        <translation>Ya existe un perfil llamado &apos;{0}&apos;.
Por favor, elige un nombre diferente.</translation>
    </message>
</context>
<context>
    <name>ProfilesSidebar</name>
    <message>
        <location filename="../sidebars/profiles.py" line="119"/>
        <source>Profiles</source>
        <comment>Profiles sidebar title</comment>
        <translation>Perfiles</translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="181"/>
        <source>Add profile (Ctrl+N)</source>
        <comment>Profile add action tooltip</comment>
        <translation>Añadir perfil (Ctrl+N)</translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="187"/>
        <source>Duplicate profile (Ctrl+D)</source>
        <comment>Profile duplicate action tooltip</comment>
        <translation>Duplicar perfil (Ctrl+D)</translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="194"/>
        <source>Edit match criteria (Enter/F2)</source>
        <comment>Profile edit action tooltip</comment>
        <translation>Editar perfil (Intro/F2)</translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="201"/>
        <source>Delete profile (Del)</source>
        <comment>Profile delete action tooltip</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="209"/>
        <source>Move up (Ctrl+Shift+Up)</source>
        <comment>Profile move up action tooltip</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="216"/>
        <source>Move down (Ctrl+Shift+Down)</source>
        <comment>Profile move down action tooltip</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="334"/>
        <source>Global</source>
        <comment>Global entry profile name</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="340"/>
        <source>When selected, the settings panel on the right edits the global configuration.</source>
        <comment>Global entry profile tooltip</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="350"/>
        <source>Global settings apply to all windows.

You can create a profile to override settings for a specific window, matched by its title or size.</source>
        <comment>No profile message</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/profiles.py" line="398"/>
        <source>When selected, the settings panel on the right edits the settings overrides for &apos;{0}&apos;.</source>
        <comment>Profile selected tooltip</comment>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ScalingTab</name>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="32"/>
        <source>Scaling</source>
        <comment>Name of a settings tab</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="41"/>
        <source>Sampler algorithm</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="43"/>
        <source>Upsampler</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="49"/>
        <source>Applied after SRCNN upscaling to reach the target output size (for example, 1440p → 4K).
• Lanczos-2 — sharp, best for 2D art and text (recommended)
• AMD FSR 1.0 — fast, best for 3D but may introduce artifacts on fine details
• NVIDIA Image Scaling — oversharpens and introduces ringing, not recommended</source>
        <comment>Description of a setting (tooltip). Do not translate the filter names (Lanczos-2, Lanczos-3, FSR, NIS).</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="59"/>
        <source>Downsampler</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="67"/>
        <source>Applied after SRCNN upscaling to reduce the image to the target output size (e.g., 1440p → 1080p).
• Catmull-Rom (bicubic) — sharp and fast, excellent tradeoff for most cases (recommended)
• Adaptive Lanczos — slower, best overall quality, handles extreme downscaling well</source>
        <comment>Description of a setting (tooltip). Do not translate the filter names (Catmull-Rom, Adaptive Lanczos).</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="77"/>
        <source>Sampler options</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="79"/>
        <source>Blur</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="87"/>
        <source>Kernel width (blur factor) for Lanczos and Catmull-Rom.
Lower values are sharper but may ring; higher values are smoother.
Recommended range: 0.8 - 1.2.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="95"/>
        <source>Antiring strength</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="103"/>
        <source>Anti-ringing strength (0.0 - 1.0) for Adaptive Lanczos and Catmull-Rom.
Lower values preserve more detail but may allow ringing.
Recommended range: 0.7 - 1.0.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="112"/>
        <source>Lanczos options</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="114"/>
        <source>Tight antiring</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="119"/>
        <source>Use only the central 2x2 area for anti-ringing.
Keeps thin text and line art sharp. Turn off if you see ringing on high-contrast edges.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="126"/>
        <source>Override Lanczos radius</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="131"/>
        <source>Force a specific Lanczos kernel radius instead of automatic selection.
When off, the radius is chosen automatically (2 for upscaling, variable for downscaling).</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="138"/>
        <source>Radius</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/scaler.py" line="149"/>
        <source>Lanczos kernel radius (2 = standard Lanczos2, 3 = sharper 6-tap).
Higher radii reduce aliasing but increase GPU load.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>SettingsSidebar</name>
    <message>
        <location filename="../sidebars/settings.py" line="81"/>
        <source>General</source>
        <comment>Name of a settings tab</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="86"/>
        <source>Scaling</source>
        <comment>Name of a settings tab</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="91"/>
        <source>Display</source>
        <comment>Name of a settings tab</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="96"/>
        <source>Presentation</source>
        <comment>Name of a settings tab</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="101"/>
        <source>Effects</source>
        <comment>Name of a settings tab</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="106"/>
        <source>Advanced</source>
        <comment>Name of a settings tab</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="111"/>
        <source>Extras</source>
        <comment>Name of a settings tab</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="116"/>
        <source>Hotkeys</source>
        <comment>Name of a settings tab</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="126"/>
        <source>GUI Style</source>
        <comment>Name of a settings tab</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="407"/>
        <location filename="../sidebars/settings.py" line="265"/>
        <source>Save profile</source>
        <comment>Save button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="409"/>
        <location filename="../sidebars/settings.py" line="267"/>
        <source>Save</source>
        <comment>Save button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="411"/>
        <location filename="../sidebars/settings.py" line="277"/>
        <source>Reset</source>
        <comment>Reset button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="287"/>
        <source>Revert this tab</source>
        <comment>Reset menu</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="290"/>
        <source>Clear this tab profile overrides</source>
        <comment>Reset menu</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="292"/>
        <source>Restore this tab defaults</source>
        <comment>Reset menu</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="296"/>
        <source>Clear all profile overrides</source>
        <comment>Reset menu</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="319"/>
        <location filename="../sidebars/settings.py" line="298"/>
        <source>Restore all to system defaults</source>
        <comment>Reset menu</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="308"/>
        <source>Restore saved palette</source>
        <comment>Reset menu</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="312"/>
        <source>Restore saved interface</source>
        <comment>Reset menu</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="315"/>
        <source>Restore default interface</source>
        <comment>Reset menu</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="401"/>
        <source>Apply style</source>
        <comment>Apply button</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/settings.py" line="402"/>
        <source>Reset style</source>
        <comment>Reset button</comment>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StyleTab</name>
    <message>
        <location filename="../sidebars/tabs/style.py" line="91"/>
        <source>GUI Style</source>
        <comment>Name of a settings tab</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="104"/>
        <source>Background &amp; surfaces</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="108"/>
        <source>Primary background</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="111"/>
        <source>Main background color of the application window and dialogs.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="118"/>
        <source>Input background</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="119"/>
        <source>Background color of text fields, combo boxes, and editable areas.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="126"/>
        <source>Input background (hover)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="130"/>
        <source>Background color when the mouse hovers over an input field.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="137"/>
        <source>Input background (disabled)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="141"/>
        <source>Background color for disabled (greyed-out) input fields.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="148"/>
        <source>Button background</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="151"/>
        <source>Background color of buttons.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="158"/>
        <source>Button background (hover)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="162"/>
        <source>Background color of a button when the mouse hovers over it.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="169"/>
        <source>Caption background</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="172"/>
        <source>Semi-transparent background color of the central grid window titles.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="180"/>
        <source>Text &amp; icons</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="184"/>
        <source>Primary text</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="185"/>
        <source>Text color of body text and labels.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="192"/>
        <source>Primary text (hover)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="195"/>
        <source>Text color when the mouse hovers over clickable items.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="202"/>
        <source>Secondary text</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="203"/>
        <source>Text color for secondary information, captions, and section headers.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="210"/>
        <source>Icon fill</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="211"/>
        <source>Fill color of sidebar and toolbar icons.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="219"/>
        <source>Borders &amp; separators</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="223"/>
        <source>Border</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="224"/>
        <source>Border color for input fields, buttons, and panels.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="231"/>
        <source>Border (hover)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="232"/>
        <source>Border color when hovering over interactive elements.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="240"/>
        <source>Controls &amp; highlights</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="244"/>
        <source>Accent</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="245"/>
        <source>Primary accent color for checkboxes, sliders and other interactive controls.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="252"/>
        <source>Accent (hover)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="253"/>
        <source>Accent color when the mouse hovers over an interactive control.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="260"/>
        <source>Reset button</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="261"/>
        <source>Background color of the &apos;Reset&apos; button.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="268"/>
        <source>Reset button (hover)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="271"/>
        <source>&apos;Reset&apos; button background color on hover.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="278"/>
        <source>Handle</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="279"/>
        <source>Fill color of scrollbar handles and other small controls.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="286"/>
        <source>Handle (hover)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="287"/>
        <source>Fill color of scrollbar handles when hovered.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="303"/>
        <source>Interface</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="305"/>
        <source>Zoom (%)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="311"/>
        <source>Scales the entire interface.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="317"/>
        <source>Font scale (%)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="323"/>
        <source>Multiplies every text size in the interface. Unlike zoom, this affects only fonts, not layout.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="330"/>
        <source>Font family</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="335"/>
        <source>Interface font. Leave at the system default for the best integration with your desktop.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="343"/>
        <source>Palette</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="345"/>
        <source>Preset</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="349"/>
        <source>Select a pre-built color scheme for the GUI.</source>
        <comment>Description of a setting (tooltip). Preset names are not translated.</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="375"/>
        <source>Sidebars</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="377"/>
        <source>Profiles sidebar width</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="383"/>
        <source>Width in pixels of the left profiles sidebar.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="389"/>
        <source>Settings sidebar width</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="395"/>
        <source>Width in pixels of the right settings sidebar.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="402"/>
        <source>Window Grid</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="404"/>
        <source>Columns</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="410"/>
        <source>Number of window preview tiles per row.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="416"/>
        <source>Aspect ratio</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="421"/>
        <source>Shape of each window preview tile.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="428"/>
        <source>Performance</source>
        <comment>Settings section</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="430"/>
        <source>Refresh (ms)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="436"/>
        <source>How often the window list is rescanned for new or closed windows.
Lower values are more responsive but use more CPU.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="443"/>
        <source>Preview (ms)</source>
        <comment>Label of setting (must be short)</comment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../sidebars/tabs/style.py" line="449"/>
        <source>How often each tile&apos;s live preview is refreshed.
Lower values result in smoother previews but use more CPU.</source>
        <comment>Description of a setting (tooltip)</comment>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>TrayController</name>
    <message>
        <location filename="../helpers/tray.py" line="409"/>
        <location filename="../helpers/tray.py" line="73"/>
        <source>Real-Time Upscaler</source>
        <comment>Name of the application</comment>
        <translation>Escalador en Tiempo Real</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="219"/>
        <source>Unknown</source>
        <comment>Fallback if no window title was found</comment>
        <translation>Desconocido</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="236"/>
        <source>Stop</source>
        <comment>Stop action for tray icon menu</comment>
        <translation>Detener</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="250"/>
        <source>Hide</source>
        <comment>Hide action for tray icon menu</comment>
        <translation>Esconder</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="254"/>
        <source>Show</source>
        <comment>Show action for tray icon menu</comment>
        <translation>Mostrar</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="274"/>
        <source>Daemon mode</source>
        <comment>Daemon mode toggle for tray icon menu</comment>
        <translation>Modo daemon</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="288"/>
        <source>Close to tray</source>
        <comment>Tray menu option</comment>
        <translation>Cerrar a la bandeja</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="297"/>
        <source>Minimize to tray</source>
        <comment>Tray menu option</comment>
        <translation>Minimizar a la bandeja</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="306"/>
        <source>Start hidden</source>
        <comment>Tray menu option</comment>
        <translation>Empezar oculto</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="317"/>
        <source>Keep running after exit</source>
        <comment>Tray menu option</comment>
        <translation>Seguir ejecutándose tras salir</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="334"/>
        <source>Exit</source>
        <translation>Salir</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="396"/>
        <source>Upscaling: &apos;{0}&apos;.
Use Stop from the tray menu to return.</source>
        <comment>Tray message if a window was already being upscaled. {0} is the window title placeholder.</comment>
        <translation>Escalando: &apos;{0}&apos;.
Utilice «Detener» en el menú de la bandeja para volver.</translation>
    </message>
    <message>
        <location filename="../helpers/tray.py" line="402"/>
        <source>Upscaling in progress.
Use Stop from the tray menu to return.</source>
        <comment>Tray message if a window was already being upscaled and no window title was available to show.</comment>
        <translation>Escalado en curso.
Utilice «Detener» en el menú de la bandeja para volver.</translation>
    </message>
</context>
<context>
    <name>WindowGridManager</name>
    <message>
        <location filename="../helpers/grid.py" line="128"/>
        <source>Error</source>
        <comment>Error warning while enumerating windows</comment>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../helpers/grid.py" line="133"/>
        <source>Could not enumerate windows.</source>
        <comment>Error warning while enumerating windows</comment>
        <translation>No se pudieron enumerar las ventanas.</translation>
    </message>
</context>
<context>
    <name>WindowPickerDialog</name>
    <message>
        <location filename="../dialogs/window.py" line="40"/>
        <source>Select Window</source>
        <comment>Select Window dialog title</comment>
        <translation>Selección de ventana</translation>
    </message>
    <message>
        <location filename="../dialogs/window.py" line="53"/>
        <source>Filter windows</source>
        <comment>Filter windows placeholder</comment>
        <translation>Filtrar ventanas</translation>
    </message>
    <message>
        <location filename="../dialogs/window.py" line="98"/>
        <source>Error</source>
        <comment>Could not list windows error</comment>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../dialogs/window.py" line="99"/>
        <source>Could not list windows.</source>
        <comment>Could not list windows error</comment>
        <translation>No se pudieron listar ventanas.</translation>
    </message>
    <message>
        <location filename="../dialogs/window.py" line="150"/>
        <source>No selection</source>
        <comment>No window selected warning title</comment>
        <translation>Ventana no seleccionada</translation>
    </message>
    <message>
        <location filename="../dialogs/window.py" line="151"/>
        <source>Select a window first.</source>
        <comment>No window selected warning</comment>
        <translation>Seleccione una ventana primero.</translation>
    </message>
</context>
</TS>
