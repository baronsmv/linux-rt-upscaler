from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QIcon
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle


class WindowItemDelegate(QStyledItemDelegate):
    """Paints a window list item with an icon, title, and size."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon_size = 32
        self.padding = 8

    def sizeHint(self, option, index):
        return QSize(200, self.icon_size + 2 * self.padding)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)  # draws selection background

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        rect = option.rect
        x = rect.x() + self.padding
        y = rect.y() + self.padding

        # Icon
        icon = index.data(Qt.DecorationRole)
        if isinstance(icon, QIcon):
            icon.paint(painter, QRect(x, y, self.icon_size, self.icon_size))
        else:
            # Fallback generic icon
            opt = QStyleOptionViewItem()
            opt.rect = QRect(x, y, self.icon_size, self.icon_size)
            option.widget.style().drawControl(QStyle.CE_ItemViewItem, opt, painter)

        # Text
        title = index.data(Qt.DisplayRole)
        size_str = index.data(Qt.UserRole + 1)  # we'll store size as "WxH"

        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)

        text_x = x + self.icon_size + self.padding
        text_y = y + 4
        painter.setPen(Qt.white)
        painter.drawText(text_x, text_y, title)

        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(Qt.gray)
        painter.drawText(text_x, text_y + 18, size_str)

        painter.restore()
