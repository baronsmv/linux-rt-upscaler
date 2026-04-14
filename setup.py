#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class BuildCaptureLib(build_ext):
    """Custom build_ext that compiles capture_x11.c before normal build."""

    def run(self):
        # Prevent multiple runs (setuptools may call this twice)
        if getattr(self, "_capture_lib_built", False):
            super().run()
            return

        print("=" * 50, file=sys.stderr)
        print("BuildCaptureLib.run() started", file=sys.stderr)

        # Use absolute paths
        project_root = Path(__file__).parent
        capture_dir = project_root / "src" / "upscaler" / "capture"
        lib_dir = capture_dir / "lib"

        if self.inplace:
            target_dir = capture_dir
        else:
            target_dir = Path(self.build_lib) / "upscaler" / "capture"
        target_dir.mkdir(parents=True, exist_ok=True)

        src_files = list(lib_dir.glob("*.c"))
        if not src_files:
            sys.stderr.write(f"No C source files found in {lib_dir}\n")
            sys.exit(1)

        so_file = target_dir / "capture_x11.so"

        cmd = [
            "gcc",
            "-shared",
            "-fPIC",
            "-O3",
            "-mtune=generic",
            f"-I{lib_dir}",
            *[str(f) for f in src_files],
            "-o",
            str(so_file),
            "-lX11",
            "-lXext",
            "-lXdamage",
            "-lXfixes",
            "-lpthread",
        ]

        print(f"Running: {' '.join(cmd)}", file=sys.stderr)
        try:
            subprocess.check_call(cmd, stdout=sys.stderr, stderr=sys.stderr)
        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"gcc failed with code {e.returncode}\n")
            raise
        except FileNotFoundError:
            sys.stderr.write("gcc not found.\n")
            sys.exit(1)

        print("capture_x11.so compiled successfully.", file=sys.stderr)
        self._capture_lib_built = True
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
