from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QMessageBox


def fit_message_box(box: QMessageBox) -> None:
    """
    Force a styled QMessageBox to size itself around its content.

    Must be called after ``setStyleSheet`` and before ``exec``. Re-polishes
    the box and its buttons, then recomputes the frame size. Without this
    the message text is truncated and the buttons clip their labels, because
    the layout was sized against the pre-stylesheet font metrics.
    """
    box.ensurePolished()
    for button in box.buttons():
        button.ensurePolished()
        metrics = QFontMetrics(button.font())
        button.setMinimumWidth(metrics.horizontalAdvance(button.text()) + 32)
    box.layout().invalidate()
    box.adjustSize()
