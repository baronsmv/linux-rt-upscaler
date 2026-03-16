import subprocess
import sys
from pathlib import Path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class BuildCaptureLib(build_ext):
    def run(self):
        if self.inplace:
            target_dir = Path(__file__).parent / "src" / "upscaler" / "capture"
        else:
            target_dir = Path(self.build_lib) / "upscaler" / "capture"

        target_dir.mkdir(parents=True, exist_ok=True)
        src_file = (
            Path(__file__).parent / "src" / "upscaler" / "capture" / "captureRGBX.c"
        )
        so_file = target_dir / "captureRGBX.so"

        cmd = [
            "gcc",
            "-shared",
            "-fPIC",
            "-O3",
            str(src_file),
            "-o",
            str(so_file),
            "-Wl,-Bdynamic",  # dynamic linking
            "-lX11",
        ]

        print(f"Running: {' '.join(cmd)}")
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"Failed to compile capture library: {e}\n")
            raise

        super().run()


# Dummy extension to force build_ext to run
dummy_extension = Extension("dummy", sources=[])

setup(
    cmdclass={"build_ext": BuildCaptureLib},
    ext_modules=[dummy_extension],  # build_ext
)
