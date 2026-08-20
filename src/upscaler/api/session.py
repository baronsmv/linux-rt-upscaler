from __future__ import annotations

from ..env import setup_environment

setup_environment()

import copy
import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import QEventLoop, QObject, QThread, QTimer, Signal
from PySide6.QtWidgets import QApplication

from ..config import Config, finalize_config, load_config, setup_logging
from ..pipeline.session import PipelineSession, create_pipeline_session
from ..utils import (
    ConfigError,
    EventLoopError,
    SessionAlreadyRunning,
    UpscalerError,
    WindowNotFound,
)
from ..window import WindowInfo, activate_window

logger = logging.getLogger(__name__)


class UpscalerSession(QObject):
    """
    Manage an upscaling instance.

    The session handles configuration loading, target window acquisition,
    Qt event loop ownership, pipeline creation and cleanup.

    **Qt modes**

    - **Script mode (session owns the Qt event loop)**:

        ```py
        from upscaler import UpscalerSession
        from upscaler.acquisition import find_window_by_title

        win = find_window_by_title(contains="A Game")
        with UpscalerSession(window=win) as session:
            session.run()
        ```

    - **Embedded mode (host already has a Qt event loop)**:

        ```py
        from upscaler import UpscalerSession
        from upscaler.acquisition import find_window_by_title

        win = find_window_by_title(contains="A Game")
        session = UpscalerSession(window=win, enable_hotkeys=False)
        session.start()

        # later...
        session.wait(10.0)
        ```

    **Errors**

    All errors derive from [``UpscalerError``](../modules/exceptions.md#upscaler.exceptions.UpscalerError):

    - ``WindowNotFound``: target window could not be found/acquired.
    - ``ConfigError``: configuration loading/validation failed.
    - ``SessionAlreadyRunning``: `start()` called twice.
    - ``EventLoopError``: `run()` called from the wrong thread or while
      another Qt event loop is active.

    Example with error handling:

    ```py
    from upscaler import UpscalerSession
    from upscaler.window import find_window_by_title
    from upscaler.exceptions import UpscalerError, WindowNotFound

    try:
        win = find_window_by_title(contains="A Game")
        session = UpscalerSession(window=win)
        session.start()
        session.run()
    except WindowNotFound:
        print("Window not found")
    except UpscalerError as exc:
        print(f"Upscaler error: {exc}")
    ```

    **Signals**

    - ``finished``: emitted when the pipeline stops (normally or by error).
    - ``error(str)``: emitted when a fatal error occurs.
    - ``window_changed(WindowInfo)``: emitted when the target window changes
      (follow focus mode).
    - ``daemon_match(WindowInfo)``: emitted when daemon mode finds a new window.
    """

    finished = Signal()
    error = Signal(str)
    window_changed = Signal(WindowInfo)
    daemon_match = Signal(WindowInfo)

    def __init__(
        self,
        window: Optional[WindowInfo] = None,
        *,
        config: Optional[Config] = None,
        config_path: Optional[str] = None,
        profile_name: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
        enable_hotkeys: bool = True,
        enable_daemon: Optional[bool] = None,
        enable_follow_focus: Optional[bool] = None,
        auto_profile_match: bool = True,
    ) -> None:
        """
        Initialize the session and prepare the configuration.

        Args:
            window: Target window to upscale. If ``None`` and daemon mode
                is enabled, the session will wait for a window matching a
                profile.
            config: A validated :class:`upscaler.Config` object. If provided,
                it is used as the base configuration (still subject to
                ``overrides``). Loading from ``config_path`` is then skipped.
            config_path: Path to a YAML configuration file. Defaults to the
                user configuration directory.
            profile_name: Name of an explicit profile to apply.
            overrides: Additional key/value overrides, taking precedence over
                everything else.
            enable_hotkeys: If ``True``, global hotkeys are registered.
                Defaults to ``True`` for script mode, but could be set to
                ``False`` when embedding to avoid conflicts.
            enable_daemon: Override the ``daemon`` flag in the final config.
            enable_follow_focus: Override the ``follow_focus`` flag.
            auto_profile_match: If ``True``, automatically apply a matching
                profile for the target window after acquisition.

        Raises:
            ConfigError: If configuration cannot be loaded or validated.
            WindowNotFound: If a window is required but not provided and
                daemon mode is not enabled.
        """
        QObject.__init__(self)

        # Internal state
        self._app_owned = False
        self._session: Optional[PipelineSession] = None
        self._started = False
        self._finished = False
        self._enable_hotkeys = enable_hotkeys

        # Configuration and window info
        self._base_config: Optional[Config] = None
        self._profiles: Dict[str, Any] = {}
        self._profile_name: Optional[str] = None
        self._window_info: Optional[WindowInfo] = None
        self._proc = None

        # ------------------------------------------------------------------
        # Load and prepare configuration
        # ------------------------------------------------------------------
        try:
            if config is not None:
                # Use provided config as starting point
                self._config = copy.deepcopy(config)
                # Still load profiles if a config_path is given (optional)
                if config_path is not None:
                    from ..config import load_yaml_config

                    _, self._profiles = load_yaml_config(config_path)
                # Apply overrides on top of provided config
                if overrides:
                    from ..config import apply_overrides

                    apply_overrides(self._config, overrides)
            else:
                # Load from file / defaults
                self._config, self._profiles = load_config(
                    profile_name=profile_name,
                    config_path=config_path,
                    overrides=overrides,
                )
                self._base_config = copy.deepcopy(self._config)

            # Apply explicit flags if provided
            if enable_daemon is not None:
                self._config.daemon = enable_daemon
            if enable_follow_focus is not None:
                self._config.follow_focus = enable_follow_focus

            # Ensure daemon mode is consistent with provided window
            if window is None and not self._config.daemon:
                raise WindowNotFound(
                    "No target window provided and daemon mode is not enabled."
                )

            # If a window is provided, we can optionally activate it and
            # apply auto-profile matching.
            self._window_info = window
            if window is not None:
                if auto_profile_match:
                    # Apply auto-profile based on window
                    self._profile_name = finalize_config(
                        self._config,
                        win_info=window,
                        profiles=self._profiles,
                        profile_name=profile_name,
                        extra_overrides=overrides,
                    )
                # Ensure the window is actually present (activation)
                activate_window(window.handle)

            setup_logging(self._config.log_level, self._config.log_file)

        except UpscalerError:
            raise
        except Exception as e:
            raise ConfigError(f"Failed to initialise session: {e}") from e

        logger.debug("UpscalerSession initialised")

    # ------------------------------------------------------------------
    # Public lifecycle methods
    # ------------------------------------------------------------------
    def start(self) -> None:
        """
        Create the pipeline session and start background threads.

        This method does **not** enter the Qt event loop. It will create a
        QApplication if none exists, but it is the caller's responsibility to
        later run the event loop (e.g., via :meth:`run` or by already having
        one in the host application).

        Raises:
            SessionAlreadyRunning: If the session is already running.
            UpscalerError: If pipeline creation fails.
        """
        if self._started:
            raise SessionAlreadyRunning("Session is already running.")

        # Ensure QApplication exists
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
            self._app_owned = True
            logger.debug("Created QApplication for session")

        # For daemon mode with no initial window, create a dummy WindowInfo
        win_info = self._window_info
        if win_info is None and self._config.daemon:
            win_info = WindowInfo(0, 0, 0, "daemon-pending")
            self._window_info = win_info

        # Create the pipeline session
        try:
            self._session = create_pipeline_session(
                config=self._config,
                win_info=win_info,
                base_config=self._base_config,
                profiles=self._profiles,
                profile_name=self._profile_name,
                on_exit=self._on_hotkey_exit,
            )
        except Exception as e:
            error_msg = f"Failed to create pipeline session: {e}"
            logger.error(error_msg)
            self.error.emit(error_msg)
            raise UpscalerError(error_msg) from e

        # Connect internal signals
        self._session.pipeline.finished.connect(self._on_pipeline_finished)
        self._session.overlay.closed.connect(self._on_overlay_closed)
        if self._config.follow_focus and self._session.monitor is not None:
            self._session.monitor.focus_changed.connect(self.window_changed)
        if self._config.daemon and self._session.daemon_monitor is not None:
            self._session.daemon_monitor.match_found.connect(self.daemon_match)

        # If hotkeys are disabled, stop the hotkey manager and discard it
        if not self._enable_hotkeys and self._session.hotkey_manager is not None:
            self._session.hotkey_manager.stop()
            self._session.hotkey_manager = None

        self._started = True
        self._finished = False
        logger.debug("Session started")

    def run(self) -> int:
        """
        Enter the Qt event loop and block until the session finishes.

        This method is intended for script mode, where the session owns the
        Qt event loop. It must be called from the main thread.

        Returns:
            Exit code (0 on normal termination).

        Raises:
            UpscalerError: If the session has not been started.
            EventLoopError: If no QApplication is available, or if an event
                loop is already running (use :meth:`wait` instead).
        """
        if not self._started:
            raise UpscalerError("Session has not been started.")
        app = QApplication.instance()
        if app is None:
            raise EventLoopError("No QApplication available.")
        if QThread.currentThread() != app.thread():
            raise EventLoopError("QApplication must run on the main thread.")
        if app.property("_is_executing"):
            raise EventLoopError(
                "Qt event loop is already running; use wait() instead."
            )

        app.setProperty("_is_executing", True)
        try:
            exit_code = app.exec()
        finally:
            app.setProperty("_is_executing", False)
            self.close()
        return exit_code

    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        Block until the session finishes or the timeout expires.

        This method uses a local QEventLoop, so it is safe to call even if
        the host application already has a running event loop. It is useful
        in embedded mode.

        Args:
            timeout: Maximum time to wait in seconds. ``None`` means wait
                indefinitely.

        Returns:
            ``True`` if the session finished within the timeout, ``False``
                if the timeout was reached.
        """
        if not self._started:
            raise UpscalerError("Session has not been started.")
        if self._finished:
            return True

        loop = QEventLoop()
        self.finished.connect(loop.quit)
        timer = None
        if timeout is not None:
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(loop.quit)
            timer.start(int(timeout * 1000))
        try:
            loop.exec()
        finally:
            if timer:
                timer.stop()
            self.finished.disconnect(loop.quit)
        return self._finished

    def close(self) -> None:
        """
        Stop the pipeline and release all resources.

        This method is idempotent and safe to call multiple times.
        """
        if self._session is not None:
            # Stop the pipeline thread first
            if self._session.pipeline is not None:
                self._session.pipeline.stop()

            # Stop monitors and hotkeys if they exist
            if self._session.monitor is not None:
                self._session.monitor.stop()
            if self._session.daemon_monitor is not None:
                self._session.daemon_monitor.stop()
            if self._session.hotkey_manager is not None:
                self._session.hotkey_manager.stop()

            # Terminate any launched process if we have one
            if self._proc is not None:
                try:
                    self._proc.terminate()
                    self._proc.wait(timeout=2.0)
                except Exception as e:
                    logger.debug(f"Error terminating launched process: {e}")

            self._session = None

        self._started = False
        self._finished = True
        logger.debug("Session closed")

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------
    def __enter__(self) -> UpscalerSession:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.close()
        return False

    # ------------------------------------------------------------------
    # Internal slots / callbacks
    # ------------------------------------------------------------------
    def _on_pipeline_finished(self) -> None:
        """Called when the pipeline thread finishes (normally or by error)."""
        self._finished = True
        self.finished.emit()

    def _on_overlay_closed(self) -> None:
        """Called when the user closes the overlay window."""
        self._finished = True
        self.finished.emit()

    def _on_hotkey_exit(self) -> None:
        """Called when the exit hotkey is pressed."""
        self._finished = True
        self.finished.emit()
        if self._app_owned and QApplication.instance() is not None:
            QApplication.instance().quit()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def running(self) -> bool:
        """True if the session is currently running."""
        return self._started and not self._finished

    @property
    def config(self) -> Config:
        """The active configuration object."""
        return self._config

    @property
    def window_info(self) -> Optional[WindowInfo]:
        """The current target window, or None if daemon waiting."""
        if self._session is not None:
            return self._session.window_info
        return self._window_info

    @property
    def profiles(self) -> Dict[str, Any]:
        """Loaded profile definitions."""
        return self._profiles

    @property
    def profile_name(self) -> Optional[str]:
        """Name of the currently applied profile, if any."""
        return self._profile_name
