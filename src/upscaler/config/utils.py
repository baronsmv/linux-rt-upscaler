from __future__ import annotations

import unicodedata
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..window import WindowInfo


def _display_width(text: str) -> int:
    """Return the terminal display width of `text`.

    CJK full‑width characters count as 2; most other characters count as 1.
    This is a simple implementation that covers the common cases.
    """
    width = 0
    for ch in text:
        ea = unicodedata.east_asian_width(ch)
        if ea in ("W", "F"):  # Wide or Fullwidth
            width += 2
        else:
            width += 1
    return width


def print_windows(windows: List[WindowInfo]):
    if not windows:
        print("No visible windows found.")
        return

    header = ("XID", "Width", "Height", "Title")
    # Prepare rows
    rows = []
    for w in windows:
        title = w.title[:47] + "..." if len(w.title) > 50 else w.title
        row = (f"0x{w.handle:x}", str(w.width), str(w.height), title)
        rows.append(row)

    # Compute display widths for header and each row
    col_widths = [_display_width(h) for h in header]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], _display_width(val))

    # Print header
    header_line = "  ".join(
        h.ljust(w) if (w - _display_width(h) >= 0) else h
        for h, w in zip(header, col_widths)
    )
    print(header_line)

    # Separator line
    total_width = sum(col_widths) + 2 * (len(header) - 1)
    print("-" * total_width)

    # Print rows
    for row in rows:
        line = "  ".join(
            v.ljust(w) if (w - _display_width(v) >= 0) else v
            for v, w in zip(row, col_widths)
        )
        print(line)
