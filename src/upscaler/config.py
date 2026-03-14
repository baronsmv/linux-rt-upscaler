import argparse
import os
from typing import Optional, List

import yaml


class Config:
    def __init__(self):
        # Default values
        self.select: bool = False
        self.model: str = "8x32"
        self.double_upscale: bool = False
        self.disable_forwarding: bool = False
        self.config_file: Optional[str] = None
        self.target_delay: int = 5
        self.pid_timeout: int = 5
        self.class_timeout: int = 5
        self.total_timeout: Optional[int] = 60
        self.starting_phase: int = 1
        self.program: Optional[List[str]] = None

    @classmethod
    def from_cli(cls):
        parser = argparse.ArgumentParser(description="Real‑Time Upscaler for Linux")
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
            default="8x32",
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
        parser.add_argument("-c", "--config", help="Path to config file (YAML)")
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

    def _load_config_file(self, custom_path: Optional[str] = None):
        """Load settings from YAML file. If custom_path is None, look in default locations."""
        paths = []
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
                    print(f"Loaded config from {path}")
                except Exception as e:
                    print(f"Warning: Failed to load config {path}: {e}")
                break  # use first found

    def _update_from_dict(self, data: dict):
        """Update config attributes from a dictionary (YAML contents)."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def _apply_args(self, args):
        """Override config with command‑line arguments."""
        if args.program:
            self.program = args.program
        if args.select:
            self.select = True
        if args.model:
            self.model = args.model
        if args.double_upscale:
            self.double_upscale = True
        if args.disable_forwarding:
            self.disable_forwarding = True
        if args.target_delay != 5:
            self.target_delay = args.target_delay
        if args.pid_timeout != 5:
            self.pid_timeout = args.pid_timeout
        if args.class_timeout != 5:
            self.class_timeout = args.class_timeout
        if args.total_timeout != 60:
            self.total_timeout = args.total_timeout
        if args.starting_phase != 1:
            self.starting_phase = args.starting_phase
