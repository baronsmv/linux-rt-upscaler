# Localization

## Quick Start

The upscaler uses [Weblate](https://hosted.weblate.org/engage/linux-rt-upscaler/) to manage translations.

No coding knowledge is required, you can start translating directly in your browser:

1. Visit the translation page [here](https://hosted.weblate.org/engage/linux-rt-upscaler/).
2. Choose your language (or start a new one if it doesn’t exist yet).
3. Begin translating strings. Your changes are saved automatically.

## Translation Guidelines

### Consistency

- Try to keep text concise and clear.
- Check existing translations for similar strings and use the same terminology.
- If you are unsure, you can leave the translation empty or add a comment in Weblate.

### Don't translate technical identifiers

The following terms must remain in English, as they are internal identifiers:

- Monitor identifiers `primary` and `all`
- Scaling filters such as `Lanczos-2` or `Catmull-Rom`
- Overlay modes `always-on-top`, `top-transparent`, `fullscreen` and `windowed`
- Output geometries `fit`, `stretch` and `cover`
- Vulkan present modes: `fifo`, `mailbox`, `immediate`

### Preserve placeholders

Some strings contain placeholders like `{0}`. 

Keep them as they are, as they are replaced with dynamic values at runtime.

## And thank you!

Thank you for helping make the upscaler accessible to more users!
