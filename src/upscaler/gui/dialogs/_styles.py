from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import GUIConfig


def list_stylesheet(gui_config: GUIConfig) -> str:
    c = gui_config
    return f"""
        QDialog {{
            background-color: {c.dialog_background};
            color: {c.dialog_text_color};
        }}
        QLabel {{
            color: {c.dialog_label_color};
            font-size: {c.dialog_label_font_size}px;
        }}
        QLineEdit {{
            background: {c.dialog_input_background};
            border: 1px solid {c.dialog_input_border};
            border-radius: {c.dialog_input_border_radius}px;
            padding: {c.dialog_input_padding};
            color: {c.dialog_text_color};
        }}
        QLineEdit:focus {{
            border-color: {c.dialog_input_focus_border};
        }}
        QComboBox {{
            background: {c.dialog_input_background};
            border: 1px solid {c.dialog_input_border};
            border-radius: {c.dialog_input_border_radius}px;
            padding: {c.dialog_input_padding};
            color: {c.dialog_text_color};
            min-width: {c.dialog_combo_min_width}px;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 0px;
        }}
        QComboBox QAbstractItemView {{
            background: {c.dialog_input_background};
            border: none;
            color: {c.dialog_text_color};
            selection-background-color: {c.dialog_input_focus_border};
        }}
        QPushButton {{
            background: {c.dialog_button_background};
            border: 1px solid {c.dialog_button_border};
            border-radius: {c.dialog_button_border_radius}px;
            padding: {c.dialog_button_padding};
            color: {c.dialog_text_color};
        }}
        QPushButton:hover {{
            background: {c.dialog_button_hover_background};
            border-color: {c.dialog_button_hover_border_color};
        }}
        QPushButton:pressed {{
            background: {c.dialog_button_pressed_background};
        }}
        QPushButton:disabled {{
            color: {c.dialog_button_disabled_color};
        }}
        QGroupBox {{
            font-size: {c.dialog_label_font_size}px;
            font-weight: bold;
            color: {c.dialog_groupbox_title_color};
            border: 1px solid {c.dialog_groupbox_border};
            border-radius: {c.dialog_groupbox_border_radius}px;
            margin-top: 8px;
            padding-top: 16px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 6px;
        }}
        QListWidget {{
            background: {c.dialog_list_background};
            border: 1px solid {c.dialog_list_border};
            border-radius: {c.dialog_list_border_radius}px;
            outline: none;
            color: {c.dialog_text_color};
        }}
        QListWidget::item {{
            padding: {c.dialog_list_item_padding};
            border-radius: {c.dialog_list_item_border_radius}px;
        }}
        QListWidget::item:hover {{
            background: {c.dialog_list_item_hover_background};
            color: {c.palette.text_primary};
        }}
        QListWidget::item:selected {{
            background: {c.dialog_list_item_selected_background};
            color: {c.palette.text_primary};
        }}
    """
