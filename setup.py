#!/usr/bin/env python3

import sys
from pathlib import Path

from setuptools import setup, Extension


def _get_version_from_pyproject():
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


capture_extension = Extension(
    "upscaler.capture.capture",
    sources=[str(f) for f in (Path("src/upscaler/capture/lib")).glob("*.c")],
    libraries=["X11", "X11-xcb", "Xext", "Xdamage", "Xfixes", "xcb", "pthread"],
    extra_compile_args=["-O3", "-mtune=generic"],
    language="c",
)

vulkan_extension = Extension(
    "upscaler.vulkan.vulkan",
    sources=[str(f) for f in Path("src/upscaler/vulkan/lib").glob("*.cpp")],
    libraries=["vulkan"],
    extra_compile_args=["-std=c++17", "-O3", "-mtune=generic"],
    language="c++",
)

setup(
    name="linux-rt-upscaler",
    version=_get_version_from_pyproject(),
    ext_modules=[capture_extension, vulkan_extension],
)
