"""Dialogs public module."""

from .about import AboutDialog
from .confirm import confirm_pending_changes
from .font import FontPickerDialog
from .profile import ProfileDialog

__all__ = [
    "AboutDialog",
    "FontPickerDialog",
    "ProfileDialog",
    "confirm_pending_changes",
]
