from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...config import GUIConfig


def sidebar_container(cfg: GUIConfig) -> str:
    """The outermost sidebar widget with rounded corners."""
    return f"""
        QWidget#sidebar_container {{
            background-color: {cfg.sidebar_background};
            border-radius: 12px;
        }}
    """


def tab_widget(cfg: GUIConfig) -> str:
    """Styles the QTabWidget and its tab bar."""
    return f"""
        QTabWidget::pane {{
            border: none;
            background: {cfg.sidebar_background};
            border-radius: 0px 0px 12px 12px;
        }}
        QTabBar::tab {{
            background: transparent;
            color: {cfg.sidebar_tab_text_color};
            font-size: {cfg.sidebar_tab_font_size}px;
            font-weight: 500;
            padding: 10px 20px;
            margin-right: 4px;
            border: none;
            border-bottom: 2px solid transparent;
            min-width: 80px;
        }}
        QTabBar::tab:selected {{
            color: {cfg.sidebar_tab_text_color_active};
            border-bottom: 2px solid {cfg.sidebar_tab_indicator_color};
        }}
        QTabBar::tab:hover {{
            color: {cfg.sidebar_tab_text_color_active};
        }}
        QTabBar::tab:disabled {{
            color: {cfg.palette.text_disabled};
        }}
    """


def scroll_area() -> str:
    """Transparent scroll area that blends into the sidebar background."""
    return """
        QScrollArea {
            background: transparent;
            border: none;
        }
        QScrollArea > QWidget > QWidget {
            background: transparent;
        }
    """


def section_label(cfg: GUIConfig) -> str:
    """Uppercase section title with subtle separator color."""
    return f"""
        font-size: {cfg.sidebar_section_title_size}px;
        font-weight: bold;
        color: {cfg.sidebar_section_title_color};
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 12px 0px 4px 0px;
    """


def row_label(cfg: GUIConfig) -> str:
    """Label used next to controls in a row."""
    return f"color: {cfg.sidebar_tab_text_color}; font-size: {cfg.sidebar_tab_font_size}px;"


def separator_line(cfg: GUIConfig) -> str:
    """Thin horizontal line used under section headers."""
    return f"color: {cfg.separator_line_color};"


def scrollbar(cfg: GUIConfig) -> str:
    return f"""
        QScrollBar:vertical {{
            background: {cfg.sidebar_background};
            width: 8px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {cfg.scrollbar_handle_color};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {cfg.scrollbar_handle_hover_color};
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{
            background: none;
        }}
    """
