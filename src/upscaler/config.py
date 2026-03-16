import argparse
import logging
import os
from importlib.metadata import version, PackageNotFoundError
from typing import Any, List, Optional, Self

import yaml

logger = logging.getLogger(__name__)


def get_version() -> str:
    """Return the package version, with a fallback for development."""
    try:
        return version("linux-rt-upscaler")
    except PackageNotFoundError:
        try:
            from . import __version__

            return __version__
        except ImportError:
            return "unknown (development mode)"


class Config:
    """
    Configuration container that loads defaults, then a YAML file,
    then overrides with command‑line arguments.
    """

    def __init__(self) -> None:
        # General
        self.program: Optional[List[str]] = None
        self.select: bool = False
        self.disable_forwarding: bool = False

        # Display
        self.monitor: str = "primary"

        # Upscaling
        self.model: str = "fast"
        self.double_upscale: bool = False

        # Search window
        self.target_delay: int = 5
        self.pid_timeout: int = 5
        self.class_timeout: int = 5
        self.total_timeout: Optional[int] = 60
        self.starting_phase: int = 1

        # Logging
        self.log_level: str = "WARNING"
        self.log_file: Optional[str] = None

        # Configuration
        self.config_file: Optional[str] = None

        logger.debug("Config object created with default values")

    @classmethod
    def from_cli(cls) -> Self:
        """Parse command line and config files, returning a fully populated Config."""
        parser = argparse.ArgumentParser(
            description="Real‑Time Upscaler for Linux",
            epilog="See source code for details: https://github.com/baronsmv/linux-rt-upscaler",
        )
        parser._positionals.title = "POSITIONAL ARGUMENTS"
        parser._optionals.title = "GENERAL OPTIONS"
        parser.add_argument(
            "-v", "--version", action="version", version=f"%(prog)s {get_version()}"
        )
        parser.add_argument(
            "-c",
            "--config",
            help="Path to config file (YAML)",
        )

        # Program argument
        parser.add_argument("program", nargs="*", help="Program to launch and scale")

        # General section
        general_group = parser.add_argument_group("INTERACTION OPTIONS")
        general_group.add_argument(
            "-s",
            "--select",
            action="store_true",
            help="Select a window from the list of open windows",
        )
        general_group.add_argument(
            "-d",
            "--disable-forwarding",
            action="store_true",
            help="Disable mouse forwarding (overlay becomes transparent to input)",
        )

        # Display section
        display_group = parser.add_argument_group("DISPLAY OPTIONS")
        display_group.add_argument(
            "--monitor",
            type=str,
            default="primary",
            help="Monitor to cover: 'primary', 'all', or monitor name/index "
            "(e.g., 'HDMI-1', 0). Default: primary.",
        )

        # Upscaling section
        upscaling_group = parser.add_argument_group("UPSCALING OPTIONS")
        upscaling_group.add_argument(
            "-m",
            "--model",
            choices=(
                "8x32",
                "4x32",
                "4x24",
                "4x16",
                "4x12",
                "3x12",
                "fast",
                "faster",
                "veryfast",
            ),
            default="fast",
            help="Upscaling model to use (ordered from best to worst quality)."
            " Default: fast",
        )
        upscaling_group.add_argument(
            "-2",
            "--double-upscale",
            action="store_true",
            help="EXPERIMENTAL: Perform two 2× passes (total 4×) for higher"
            " resolution screens (4k, 1440p) or low‑resolution sources",
        )

        # Logging section
        log_group = parser.add_argument_group("LOGGING OPTIONS")
        log_group.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="Decrease log verbosity (ERROR level)",
        )
        log_group.add_argument(
            "--debug",
            action="store_true",
            help="Increase log verbosity (DEBUG level)",
        )
        log_group.add_argument(
            "--log-file",
            help="Write logs to this file (parent directories are created)",
        )

        # Timeout / window detection section
        timeout_group = parser.add_argument_group("WINDOW DETECTION OPTIONS")
        timeout_group.add_argument(
            "--target-delay",
            type=int,
            default=5,
            help="Seconds to wait before capturing active window",
        )
        timeout_group.add_argument(
            "--pid-timeout",
            type=int,
            default=5,
            help="Seconds to try PID‑based window detection",
        )
        timeout_group.add_argument(
            "--class-timeout",
            type=int,
            default=5,
            help="Seconds to try class‑based window detection",
        )
        timeout_group.add_argument(
            "--total-timeout",
            type=int,
            default=60,
            help="Total seconds before giving up",
        )
        timeout_group.add_argument(
            "--starting-phase",
            type=int,
            choices=[1, 2],
            default=1,
            help="Start with phase 1 (PID) or 2 (class)",
        )

        args = parser.parse_args()

        config = cls()

        # Load config file if specified or default
        config._load_config_file(args.config)

        # Override with CLI arguments
        config._apply_args(args)

        # Log level and file
        if args.debug:
            config.log_level = "DEBUG"
        elif args.quiet:
            config.log_level = "ERROR"
        if args.log_file:
            config.log_file = args.log_file

        return config

    def _load_config_file(self, custom_path: Optional[str] = None) -> None:
        """
        Load settings from a YAML file.
        If custom_path is given, try that path; otherwise search default locations.
        Only the first found file is loaded.
        """
        paths: List[str] = []
        if custom_path:
            paths.append(custom_path)
        else:
            # Default: ~/.config/linux-rt-upscaler/config.yaml
            xdg_config = os.environ.get(
                "XDG_CONFIG_HOME", os.path.expanduser("~/.config")
            )
            default_path = os.path.join(xdg_config, "linux-rt-upscaler", "config.yaml")
            paths.append(default_path)
            # Also check current directory for convenience
            paths.append("./config.yaml")

        for path in paths:
            if os.path.isfile(path):
                try:
                    with open(path, "r") as f:
                        data = yaml.safe_load(f)
                        if data:
                            self._update_from_dict(data)
                    logger.info(f"Loaded config from {path}")
                except Exception as e:
                    logger.warning(f"Failed to load config {path}: {e}")
                break  # use first found

    def _update_from_dict(self, data: dict[str, Any]) -> None:
        """Update config attributes from a dictionary (YAML contents)."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.debug(f"Config set from file: {key} = {value!r}")
            else:
                logger.debug(f"Ignoring unknown config key: {key}")

    def _apply_args(self, args: argparse.Namespace) -> None:
        """Override config with command‑line arguments."""
        # Note: args.program can be an empty list; we preserve None if not set
        if args.program:
            self.program = args.program
            logger.debug(f"CLI set program = {self.program}")
        if args.select:
            self.select = True
            logger.debug("CLI set select = True")
        if args.model != "fast":
            self.model = args.model
            logger.debug(f"CLI set model = {self.model}")
        if args.double_upscale:
            self.double_upscale = True
            logger.debug("CLI set double_upscale = True")
        if args.disable_forwarding:
            self.disable_forwarding = True
            logger.debug("CLI set disable_forwarding = True")
        if args.monitor != "primary":
            self.monitor = args.monitor
            logger.debug(f"CLI set monitor = {self.monitor}")
        if args.target_delay != 5:
            self.target_delay = args.target_delay
            logger.debug(f"CLI set target_delay = {self.target_delay}")
        if args.pid_timeout != 5:
            self.pid_timeout = args.pid_timeout
            logger.debug(f"CLI set pid_timeout = {self.pid_timeout}")
        if args.class_timeout != 5:
            self.class_timeout = args.class_timeout
            logger.debug(f"CLI set class_timeout = {self.class_timeout}")
        if args.total_timeout != 60:
            self.total_timeout = args.total_timeout
            logger.debug(f"CLI set total_timeout = {self.total_timeout}")
        if args.starting_phase != 1:
            self.starting_phase = args.starting_phase
            logger.debug(f"CLI set starting_phase = {self.starting_phase}")
