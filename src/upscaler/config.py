import argparse
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Config:
    program: List[str]
    map_clicks: bool
    starting_phase: int  # 1: Search by PID; 2: Class‑based search
    pid_timeout: int  # Timeout for PID search
    class_timeout: int  # Timeout for class search
    total_timeout: Optional[int]  # Timeout to stop searching (infinite if None)
    target_delay: int  # Delay to upscale active window
    model: str  # Model to use to upscale

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
            help="Upscaling model to use (ordered from best to worst quality)",
        )
        parser.add_argument(
            "program", nargs="*", help="Program to launch and scale (optional)"
        )
        args = parser.parse_args()

        return cls(
            program=args.program,
            map_clicks=not args.disable_forwarding,
            starting_phase=1,
            pid_timeout=5,
            class_timeout=5,
            total_timeout=5,
            target_delay=5,
            model=args.model,
        )
