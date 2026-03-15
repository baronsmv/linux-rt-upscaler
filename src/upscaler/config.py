import argparse
import logging
import os
from typing import Optional, List, Any

import yaml

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration container that loads defaults, then a YAML file,
    then overrides with command‑line arguments.
    """

    def __init__(self) -> None:
        # Default values
        self.select: bool = False
        self.model: str = "fast"
        self.double_upscale: bool = False
        self.disable_forwarding: bool = False
        self.config_file: Optional[str] = None
        self.target_delay: int = 5
        self.pid_timeout: int = 5
        self.class_timeout: int = 5
        self.total_timeout: Optional[int] = 60
        self.starting_phase: int = 1
        self.program: Optional[List[str]] = None

        logger.debug("Config object created with default values")

    @classmethod
    def from_cli(cls) -> Config:
        """Parse command line and config files, returning a fully populated Config."""
        parser = argparse.ArgumentParser(
            description="Real‑Time Upscaler for Linux",
            epilog="See source code for details: https://github.com/baronsmv/linux-rt-upscaler",
        )
        parser.add_argument("program", nargs="*", help="Program to launch and scale")
        parser.add_argument(
            "-s",
            "--select",
            action="store_true",
            help="Select a window from the list of open windows",
        )
        parser.add_argument(
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
            help="Upscaling model to use (ordered from best to worst quality)",
        )
        parser.add_argument(
            "-d",
            "--disable-forwarding",
            action="store_true",
            help="Disable mouse forwarding (overlay becomes transparent to input)",
        )
        parser.add_argument(
            "-2",
            "--double-upscale",
            action="store_true",
            help="EXPERIMENTAL: Perform two 2× passes (total 4×) for higher"
            " resolutions screens (4k, 1440p) or low‑resolution sources",
        )
        parser.add_argument(
            "-c",
            "--config",
            help="Path to config file (YAML)",
        )
        parser.add_argument(
            "--target-delay",
            type=int,
            default=5,
            help="Seconds to wait before capturing active window",
        )
        parser.add_argument(
            "--pid-timeout",
            type=int,
            default=5,
            help="Seconds to try PID‑based window detection",
        )
        parser.add_argument(
            "--class-timeout",
            type=int,
            default=5,
            help="Seconds to try class‑based window detection",
        )
        parser.add_argument(
            "--total-timeout",
            type=int,
            default=60,
            help="Total seconds before giving up",
        )
        parser.add_argument(
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
