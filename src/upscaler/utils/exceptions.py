class UpscalerError(Exception):
    """Base class for all errors raised by the upscaler."""


class WindowNotFound(UpscalerError):
    """Raised when a requested window cannot be found or acquired."""


class ConfigError(UpscalerError):
    """Raised when configuration loading, merging, or validation fails."""


class SessionAlreadyRunning(UpscalerError):
    """Raised when trying to start an already running session."""


class EventLoopError(UpscalerError):
    """Raised when Qt event loop handling is invalid (e.g., run() while
    another loop is already running)."""
