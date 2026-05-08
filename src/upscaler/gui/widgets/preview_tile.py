from typing import Optional

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
    QRectF,
    Property,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtGui import (
    QPainter,
    QPixmap,
    QImage,
    QLinearGradient,
    QColor,
    QFont,
    QPen,
    QPainterPath,
)
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect

from ...capture import FrameGrabber
from ...window import WindowInfo


class PreviewTile(QWidget):
    """
    A live window preview tile that scales up slightly when hovered or
    selected, with a drop shadow for depth.

    All visual parameters are taken from `GUIConfig`.
    """

    clicked = Signal(WindowInfo)

    def __init__(self, win_info: WindowInfo, gui_config, parent=None):
        super().__init__(parent)
        self._win_info = win_info
        self._cfg = gui_config

        # Fixed size from config
        self.setFixedSize(gui_config.tile_width, gui_config.tile_height)
        self.setCursor(Qt.PointingHandCursor)

        # Drop shadow (initialized to resting state)
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(gui_config.shadow_blur_radius)
        self._shadow.setOffset(*gui_config.shadow_offset)
        self._shadow.setColor(QColor(*gui_config.shadow_color))
        self.setGraphicsEffect(self._shadow)

        # Internal state
        self._grabber: Optional[FrameGrabber] = None
        self._pixmap: Optional[QPixmap] = None
        self._full_w = 0
        self._full_h = 0
        self._hover = False
        self._selected = False
        self._pop_scale = 1.0  # 1.0 = normal, > 1.0 = popped

        # Live preview timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.setInterval(gui_config.tile_preview_interval_ms)

        self._init_grabber()
        self._timer.start()

        # Enable painting outside the widget’s bounding rect
        self.setAttribute(Qt.WA_PaintUnclipped)

    # ------------------------------------------------------------------
    #  Pop‑out property (used by QPropertyAnimation)
    # ------------------------------------------------------------------
    def get_pop_scale(self) -> float:
        return self._pop_scale

    def set_pop_scale(self, value: float) -> None:
        self._pop_scale = value
        self.update()
        # update shadow while animating
        alpha = int(
            self._cfg.shadow_color[3]
            + (self._cfg.shadow_hover_color[3] - self._cfg.shadow_color[3])
            * (value - 1.0)
        )
        blur = int(
            self._cfg.shadow_blur_radius
            + (self._cfg.shadow_hover_blur_radius - self._cfg.shadow_blur_radius)
            * (value - 1.0)
        )
        self._shadow.setBlurRadius(blur)
        self._shadow.setColor(
            QColor(
                self._cfg.shadow_hover_color[0],
                self._cfg.shadow_hover_color[1],
                self._cfg.shadow_hover_color[2],
                alpha,
            )
        )

    pop_scale = Property(float, get_pop_scale, set_pop_scale)

    def animate_pop_in(self) -> None:
        """Smoothly pop out to `pop_scale`."""
        self._stop_pop_animation()
        self._pop_anim = QPropertyAnimation(self, b"pop_scale", self)
        self._pop_anim.setDuration(self._cfg.pop_duration)
        self._pop_anim.setStartValue(self._pop_scale)
        self._pop_anim.setEndValue(self._cfg.pop_scale)
        self._pop_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._pop_anim.start()

    def animate_pop_out(self) -> None:
        """Smoothly return to normal scale."""
        self._stop_pop_animation()
        self._pop_anim = QPropertyAnimation(self, b"pop_scale", self)
        self._pop_anim.setDuration(self._cfg.pop_duration)
        self._pop_anim.setStartValue(self._pop_scale)
        self._pop_anim.setEndValue(1.0)
        self._pop_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._pop_anim.start()

    def _stop_pop_animation(self) -> None:
        if hasattr(self, "_pop_anim") and self._pop_anim is not None:
            self._pop_anim.stop()
            self._pop_anim = None

    # ------------------------------------------------------------------
    #  Frame grabber (unchanged, uses GUIConfig for tile_size)
    # ------------------------------------------------------------------
    def _init_grabber(self) -> None:
        try:
            self._grabber = FrameGrabber(
                self._win_info,
                crop_left=0,
                crop_top=0,
                crop_right=0,
                crop_bottom=0,
                tile_size=64,  # TODO: possibly configurable
            )
            self._full_w = self._win_info.width
            self._full_h = self._win_info.height
        except Exception:
            self._grabber = None

    def _refresh(self) -> None:
        if self._grabber is None:
            return
        try:
            frame, _, _ = self._grabber.grab()
        except RuntimeError:
            self.stop()
            return
        if len(frame) != self._full_w * self._full_h * 4:
            return

        data = bytearray(frame)
        for i in range(3, len(data), 4):
            data[i] = 255

        qimg = QImage(
            bytes(data),
            self._full_w,
            self._full_h,
            self._full_w * 4,
            QImage.Format_RGBA8888,
        ).rgbSwapped()

        avail_w = self.width() - 8
        avail_h = self.height() - 8
        scaled = qimg.scaled(
            avail_w, avail_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._pixmap = QPixmap.fromImage(scaled)
        self.update()

    def stop(self) -> None:
        self._timer.stop()
        if self._grabber:
            self._grabber.close()
            self._grabber = None

    # ------------------------------------------------------------------
    #  Mouse events for hover and click
    # ------------------------------------------------------------------
    def enterEvent(self, event) -> None:
        self._hover = True
        self.update()
        # Notify the grid so it can trigger an animation
        if self.parent() and hasattr(self.parent(), "_tile_enter"):
            self.parent()._tile_enter(self)
        self.animate_pop_in()

    def leaveEvent(self, event) -> None:
        self._hover = False
        self.update()
        if self.parent() and hasattr(self.parent(), "_tile_leave"):
            self.parent()._tile_leave(self)
        self.animate_pop_out()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            if self.parent():
                self.parent().setFocus()
            self.clicked.emit(self._win_info)

    # ------------------------------------------------------------------
    #  Painting with scale and rounded clipping
    # ------------------------------------------------------------------
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        scale = self._pop_scale
        # Transform to scale from centre
        if abs(scale - 1.0) > 0.001:
            cx = self.width() / 2
            cy = self.height() / 2
            painter.translate(cx, cy)
            painter.scale(scale, scale)
            painter.translate(-cx, -cy)

        # Rounded clipping
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(self.rect()), self._cfg.tile_radius, self._cfg.tile_radius
        )
        painter.setClipPath(path)
        painter.fillPath(path, QColor(self._cfg.tile_background))

        # Live preview image (centered)
        if self._pixmap and not self._pixmap.isNull():
            x = (self.width() - self._pixmap.width()) // 2
            y = (self.height() - self._pixmap.height()) // 2
            painter.drawPixmap(x, y, self._pixmap)

        # Gradient overlay at bottom
        gradient = QLinearGradient(0, self.height() - 40, 0, self.height())
        gradient.setColorAt(0, QColor(*self._cfg.tile_title_overlay_start))
        gradient.setColorAt(0.7, QColor(*self._cfg.tile_title_overlay_mid))
        gradient.setColorAt(1.0, QColor(*self._cfg.tile_title_overlay_end))
        painter.fillRect(0, self.height() - 40, self.width(), 40, gradient)

        # Title text
        painter.setPen(QColor(self._cfg.title_text_color))
        font = QFont(self._cfg.title_font_family, self._cfg.title_font_size)
        font.setBold(self._cfg.title_font_bold)
        painter.setFont(font)
        painter.drawText(10, self.height() - 12, self._win_info.title)

        # Border: selected > hover > none
        if self._selected:
            pen = QPen(
                QColor(self._cfg.tile_selected_border), self._cfg.selection_border_width
            )
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(
                QRectF(self.rect()).adjusted(1, 1, -1, -1),
                self._cfg.tile_radius,
                self._cfg.tile_radius,
            )
        elif self._hover:
            pen = QPen(
                QColor(self._cfg.tile_hover_border), self._cfg.hover_border_width
            )
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(
                QRectF(self.rect()).adjusted(1, 1, -1, -1),
                self._cfg.tile_radius,
                self._cfg.tile_radius,
            )

        painter.end()

    # ------------------------------------------------------------------
    #  Properties accessed by WindowGrid
    # ------------------------------------------------------------------
    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        if self._selected != value:
            self._selected = value
            self.update()
            # If just selected, ensure the tile is popped out
            if value:
                self.animate_pop_in()
            elif not self._hover:
                self.animate_pop_out()

    @property
    def window_info(self) -> WindowInfo:
        return self._win_info
