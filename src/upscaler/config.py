import argparse
from dataclasses import dataclass
from typing import List


@dataclass
class Config:
    program: List[str]
    map_clicks: bool = True
    pid_timeout: int = 5
    class_timeout: int = 5
    target_delay: int = 5
    model: str = "fast"  # new field

    @classmethod
    def from_cli(cls):
        parser = argparse.ArgumentParser(
            description="Real‑time window upscaler using CuNNy (2×) + full‑screen scaling."
        )
        parser.add_argument(
            "-d",
            "--disable-forwarding",
            action="store_true",
            help="Disable mouse forwarding (overlay becomes transparent to input)",
        )
        parser.add_argument(
            "-m",
            "--model",
            default="8x32",
            choices=("8x32", "fast", "veryfast"),
            help="Upscaling model to use (ordered from best to worst quality)",
        )
        parser.add_argument(
            "program", nargs="*", help="Program to launch and scale (optional)"
        )
        args = parser.parse_args()

        return cls(
            program=args.program,
            map_clicks=not args.disable_forwarding,
            pid_timeout=5,
            class_timeout=5,
            target_delay=5,
            model=args.model,
        )
