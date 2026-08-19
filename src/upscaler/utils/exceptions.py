"""Exception classes used by the upscaler."""


class UpscalerError(Exception):
    """Base class for all errors raised by the upscaler."""


class WindowNotFound(UpscalerError):
    """Raised when a target window cannot be found or acquired."""


class ConfigError(UpscalerError):
    """Raised when configuration loading, merging, or validation fails."""


class SessionError(UpscalerError):
    """Base class for session lifecycle errors."""


class SessionAlreadyRunning(SessionError):
    """Raised when trying to start an already running session."""


class EventLoopError(UpscalerError):
    """Raised when Qt event loop handling is invalid (e.g., run() while
    another loop is already running)."""
