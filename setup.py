#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


def get_version_from_pyproject():
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    if not pyproject_path.exists():
        return "0.0.0"
    try:
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            import tomli as tomllib
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("version") or "0.0.0"
    except Exception:
        return "0.0.0"


class BuildSharedLibs(build_ext):
    """Compile capture.so (plain C) then continue with Python extensions."""

    def run(self):
        if getattr(self, "_capture_lib_built", False):
            super().run()
            return

        print("=" * 50, file=sys.stderr)
        print("BuildSharedLibs.run() started", file=sys.stderr)

        project_root = Path(__file__).parent

        # --- capture.so ---
        capture_dir = project_root / "src" / "upscaler" / "capture"
        capture_lib_dir = capture_dir / "lib"

        if self.inplace:
            capture_target_dir = capture_dir
        else:
            capture_target_dir = Path(self.build_lib) / "upscaler" / "capture"
        capture_target_dir.mkdir(parents=True, exist_ok=True)

        capture_src = list(capture_lib_dir.glob("*.c"))
        if not capture_src:
            sys.stderr.write(f"No C source files found in {capture_lib_dir}\n")
            sys.exit(1)

        capture_so = capture_target_dir / "capture.so"
        capture_cmd = [
            "gcc",
            "-shared",
            "-fPIC",
            "-O3",
            "-mtune=generic",
            f"-I{capture_lib_dir}",
            *[str(f) for f in capture_src],
            "-o",
            str(capture_so),
            "-lxcb",
            "-lxcb-shm",
            "-lxcb-damage",
            "-lxcb-xfixes",
            "-lxcb-aux",
            "-lpthread",
        ]

        print(f"Running: {' '.join(capture_cmd)}", file=sys.stderr)
        subprocess.check_call(capture_cmd, stdout=sys.stderr, stderr=sys.stderr)
        print("capture.so compiled successfully.", file=sys.stderr)

        self._capture_lib_built = True
        super().run()


# Vulkan extension
vulkan_lib_dir = Path("src/upscaler/vulkan/lib")
vulkan_sources = [str(f) for f in vulkan_lib_dir.glob("*.cpp")]

vulkan_extension = Extension(
    "upscaler.vulkan.vulkan",
    sources=vulkan_sources,
    libraries=["vulkan"],
    extra_compile_args=["-std=c++14", "-O3", "-mtune=generic"],
    language="c++",
)

setup(
    name="linux-rt-upscaler",
    version=get_version_from_pyproject(),
    cmdclass={"build_ext": BuildSharedLibs},
    ext_modules=[vulkan_extension],
)
