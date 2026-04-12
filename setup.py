#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class BuildCaptureLib(build_ext):
    """Custom build_ext that compiles capture_x11.c before normal build."""

    def run(self):
        # Logging to stderr (visible in CI)
        print("=" * 50, file=sys.stderr)
        print("BuildCaptureLib.run() started", file=sys.stderr)
        print("Current directory:", os.getcwd(), file=sys.stderr)

        capture_dir = Path(__file__).parent / "src" / "upscaler" / "capture"
        print("Contents of capture dir:", list(capture_dir.iterdir()), file=sys.stderr)

        # Determine target directory for the .so file
        if self.inplace:
            target_dir = capture_dir
        else:
            target_dir = Path(self.build_lib) / "upscaler" / "capture"
        target_dir.mkdir(parents=True, exist_ok=True)

        src_file = capture_dir / "capture_x11.c"
        so_file = target_dir / "capture_x11.so"

        # Compiler command
        cmd = [
            "gcc",
            "-shared",
            "-fPIC",
            "-O3",
            "-mtune=generic",
            str(src_file),
            "-o",
            str(so_file),
            "-Wl,-Bdynamic",
            "-lX11",
            "-lXext",
            "-lXdamage",
            "-lXfixes",
        ]

        print(f"Running: {' '.join(cmd)}", file=sys.stderr)
        try:
            subprocess.check_call(cmd, stdout=sys.stderr, stderr=sys.stderr)
        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"❌ gcc failed with code {e.returncode}\n")
            sys.stderr.write(f"Command: {' '.join(cmd)}\n")
            sys.stderr.write(
                "Make sure libX11-devel is installed and gcc is available.\n"
            )
            raise
        except FileNotFoundError:
            sys.stderr.write(
                "❌ gcc not found. Please install a C compiler (build-essential).\n"
            )
            sys.exit(1)

        print("✅ capture_x11.so compiled successfully.", file=sys.stderr)
        print("BuildCaptureLib.run() finished", file=sys.stderr)

        # Now compile the dummy extension (triggers the normal build_ext)
        super().run()


# Ensure a tiny dummy C source exists (in the repo or created on the fly)
dummy_c_path = Path("src/upscaler/capture/dummy.c")
if not dummy_c_path.exists():
    dummy_c_path.parent.mkdir(parents=True, exist_ok=True)
    dummy_c_path.write_text(
        "/* dummy file to force extension build */\nvoid dummy(void) {}\n"
    )

# Dummy extension – source path is relative to setup.py (required by setuptools)
dummy_extension = Extension(
    "upscaler.capture.dummy",
    sources=["src/upscaler/capture/dummy.c"],
)

setup(
    name="linux-rt-upscaler",
    version="0.2.4",
    cmdclass={"build_ext": BuildCaptureLib},
    ext_modules=[dummy_extension],
)
