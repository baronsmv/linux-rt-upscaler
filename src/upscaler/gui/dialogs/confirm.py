from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMessageBox, QWidget

from ..styles import message_box_style

if TYPE_CHECKING:
    from ..config import GUIConfig


def confirm_pending_changes(
    parent: QWidget,
    gui_config: GUIConfig,
    has_pending: Callable[[], bool],
    save_pending: Callable[[], None],
    closing: bool = False,
) -> bool:
    """
    Show the unsaved-changes dialog and act on the user's choice.

    Parameters
    ----------
    parent: QWidget
        Parent for the dialog. Typically the main window.
    gui_config: GUIConfig
        Active GUI configuration, used for styling the dialog.
    has_pending: Callable[[], bool]
        Returns True if there are unsaved changes. Called once, before
        the dialog is shown.
    save_pending: Callable[[], None]
        Invoked when the user picks Save. Responsible for persisting
        every pending change.
    closing: bool
        True when the changes would be lost to application closure,
        False when they would be lost to a profile switch. Affects
        only the wording of the buttons and the informational text.

    Returns
    -------
    bool
        True if the caller should proceed (Save or Discard chosen),
        False if the user canceled.
    """
    if not has_pending():
        return True

    if closing:
        informative = QCoreApplication.translate(
            "ConfirmDialog",
            "Save them before closing, discard them, or cancel to stay.",
            "Dialog secondary text",
        )
        save_label = QCoreApplication.translate(
            "ConfirmDialog", "Save and close", "Dialog button"
        )
        discard_label = QCoreApplication.translate(
            "ConfirmDialog", "Discard and close", "Dialog button"
        )
    else:
        informative = QCoreApplication.translate(
            "ConfirmDialog",
            "Save them before switching, discard them, or cancel to stay.",
            "Dialog secondary text",
        )
        save_label = QCoreApplication.translate(
            "ConfirmDialog", "Save and switch", "Dialog button"
        )
        discard_label = QCoreApplication.translate(
            "ConfirmDialog", "Discard and switch", "Dialog button"
        )

    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(
        QCoreApplication.translate("ConfirmDialog", "Unsaved changes", "Dialog title")
    )
    box.setText(
        QCoreApplication.translate(
            "ConfirmDialog",
            "You have unsaved changes in the current configuration.",
            "Dialog main text",
        )
    )
    box.setInformativeText(informative)

    save_btn = box.addButton(save_label, QMessageBox.AcceptRole)
    discard_btn = box.addButton(discard_label, QMessageBox.DestructiveRole)
    cancel_btn = box.addButton(
        QCoreApplication.translate("ConfirmDialog", "Cancel", "Dialog button"),
        QMessageBox.RejectRole,
    )
    box.setDefaultButton(save_btn)
    box.setEscapeButton(cancel_btn)
    box.setStyleSheet(message_box_style(gui_config))

    box.exec()
    clicked = box.clickedButton()
    if clicked is save_btn:
        save_pending()
        return True
    if clicked is discard_btn:
        return True
    return False
