from __future__ import annotations

import unicodedata
from typing import List, Tuple


def _display_width(text: str) -> int:
    """Return the terminal display width of `text`.

    CJK full‑width characters count as 2; most other characters count as 1.
    """
    return sum(
        2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text
    )


def _print_table(
    header: Tuple[str, ...],
    rows: List[Tuple[str, ...]],
    empty_message: str = "No items found.",
):
    """Print a formatted table with automatic column widths.

    Args:
        header: tuple of column titles.
        rows:   list of tuples, each tuple containing the cell strings for one row.
        empty_message: printed if `rows` is empty.
    """
    if not rows:
        print(empty_message)
        return

    # Column display widths
    col_widths = [_display_width(h) for h in header]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], _display_width(cell))

    def pad(value, width):
        """Pad a string to the given display width (left‑justified)."""
        return value.ljust(width) if _display_width(value) <= width else value

    # Header
    print("  ".join(pad(h, w) for h, w in zip(header, col_widths)))

    # Separator
    total_width = sum(col_widths) + 2 * (len(header) - 1)
    print("-" * total_width)

    # Rows
    for row in rows:
        print("  ".join(pad(v, w) for v, w in zip(row, col_widths)))


def print_windows():
    from ..window import list_windows

    windows = list_windows()
    header = ("XID", "Width", "Height", "Title")
    rows = []
    for w in windows:
        title = w.title[:47] + "..." if len(w.title) > 50 else w.title
        rows.append((f"0x{w.handle:x}", str(w.width), str(w.height), title))
    _print_table(header, rows, "No visible windows found.")


def print_devices():
    from ..vulkan import get_discovered_devices

    devices = get_discovered_devices()
    header = ("Idx", "Name", "Type", "VRAM")
    rows = []
    for i, d in enumerate(devices):
        dtype = (
            "Discrete" if d.is_discrete else "Integrated" if d.is_hardware else "CPU"
        )
        vram = (
            f"{d.dedicated_video_memory // (1024**2)} MB"
            if d.dedicated_video_memory
            else "N/A"
        )
        rows.append((str(i), d.name, dtype, vram))
    _print_table(header, rows, "No Vulkan devices found.")


def print_monitors():
    from ..utils import list_monitors

    monitors = list_monitors()
    if not monitors:
        print("No monitors detected.")
        return

    header = ("Name",)
    rows = [(m,) for m in monitors]
    _print_table(header, rows)
