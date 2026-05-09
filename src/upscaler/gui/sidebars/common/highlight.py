from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel

from ...config import GUIConfig


def apply_row_highlight(
    widget,
    indicator: QFrame,
    label: QLabel | None,
    highlighted: bool,
    cfg: GUIConfig,
) -> None:
    """Show/hide the indicator frame and optionally recolor the label."""
    indicator.setVisible(highlighted)
    if label is not None:
        label.setStyleSheet(
            f"color: {cfg.highlight_label_color if highlighted else cfg.sidebar_tab_text_color};"
        )
