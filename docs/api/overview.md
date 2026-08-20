# API Overview

Want to embed upscaling into your own Python applications, scripts and game launchers?

**Use the API of the upscaler!**

!!! tip "To Be or Not to Be"
    
    If you only need to run the upscaler from a terminal, the [Command-Line Interface](../user/cli.md) is often simpler.

    The API is best when you need programmatic control.

!!! tip "Missing an API feature?"

    If you need something that isn’t exposed in the API yet (for example, a different window acquisition method, a runtime setting or a new Qt signal) please [open an issue](https://github.com/baronsmv/linux-rt-upscaler/issues/new?template=feature_request.md) and describe your use case.

## Components

### Classes

| Class                                            | Description                                                    |
|--------------------------------------------------|----------------------------------------------------------------|
| [`UpscalerSession`](classes/upscaler_session.md) | Session class that manages the upscaling lifecycle.            |
| [`WindowInfo`](classes/window_info.md)           | Immutable dataclass describing the properties of a X11 window. |
| [`Config`](classes/config.md)                    | Dataclass containing all settings for the upscaler.            |

### Modules

| Module                                       | Description                                                    |
|----------------------------------------------|----------------------------------------------------------------|
| [Window Acquisition](modules/acquisition.md) | Functions for finding, listing, and acquiring target windows.  |
| [Exceptions](modules/exceptions.md)          | Exceptions raised by the API.                                  |

## Quick start

Ready? Let's go then!

The simplest way to use the API is to find a window and run an upscaling session (optionally inside a `with` block):

```py
from upscaler import UpscalerSession
from upscaler.acquisition import find_window_by_title

win = find_window_by_title(contains="A Game")
with UpscalerSession(window=win) as session:
    session.run()
```

This starts the pipeline and enters the Qt event loop. When the window closes or the session is stopped, the instance cleans up the subresources used automatically.

## Embedded mode

If your application already has a Qt event loop running, do not call `run()`. Instead, use `start()` and `wait()`:

```python
from upscaler import UpscalerSession
from upscaler.acquisition import find_window_by_title

win = find_window_by_title(contains="A Game")
session = UpscalerSession(window=win, enable_hotkeys=False)
session.start()

# do other things...
session.wait(10.0)   # blocks until session finishes or timeout
```

In embedded mode, you can also connect to the session’s signals: `finished`, `error`, `window_changed`, and `daemon_match`.

## Error handling

All API errors derive from `UpscalerError`. Common ones include `WindowNotFound` and `ConfigError`.

Always wrap your calls in a `try`
block when there is a chance of failure:

```python
from upscaler import UpscalerSession
from upscaler.acquisition import find_window_by_title
from upscaler.exceptions import UpscalerError, WindowNotFound

try:
    win = find_window_by_title(contains="My Game")
    session = UpscalerSession(window=win)
    session.run()
except WindowNotFound:
    print("Window not found")
except UpscalerError as exc:
    print(f"Upscaler error: {exc}")
```

## What to read next

- Learn more details of the session in [`UpscalerSession`](classes/upscaler_session.md).
- Review all window acquisition helpers in [Window Acquisition](modules/acquisition.md).
- See available options to adjust in [`Config`](classes/config.md).
