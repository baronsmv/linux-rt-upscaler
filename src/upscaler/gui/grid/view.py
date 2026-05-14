from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QKeyEvent, QPainter, QKeySequence
from PySide6.QtWidgets import QGraphicsView

from .scene import WindowGridScene
from ..styles import graphics_view_style


class WindowGridView(QGraphicsView):
    """
    A scrollable viewport for the :class:`WindowGridScene`.

    Responsibilities:
        - Provide antialiased rendering with transparent background.
        - Propagate resize events to trigger scene relayout (debounced).
        - Forward key presses (arrows, Enter, Escape) to the scene for
          keyboard navigation.
        - Accept focus and allow the scene to handle focus changes.
        - Support smooth scrolling (built into QGraphicsView).
        - (Optional) emit a signal to request filter focus, e.g. via
          Ctrl+F, but this can be handled at a higher level.

    All visual parameters are taken from :class:`GUIConfig`.
    """

    # Emitted when the user presses Ctrl+F (can be connected to focus filter bar)
    focus_filter_requested = Signal()

    def __init__(self, scene: WindowGridScene, gui_config, parent=None) -> None:
        super().__init__(scene, parent)
        self._cfg = gui_config
        self._scene = scene

        # Rendering quality
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.setBackgroundBrush(Qt.NoBrush)

        # No drag mode - tiles are not draggable
        self.setDragMode(QGraphicsView.NoDrag)

        # Scrollbar policy
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Transparent background and no frame
        self.setStyleSheet(graphics_view_style(self._cfg))

        # Accept focus (needed for keyboard navigation)
        self.setFocusPolicy(Qt.StrongFocus)

        # Attach scene to this view so the scene can access viewport dimensions
        scene.attach_view(self)

        # Debounced relayout on resize
        self._resize_timer_id = -1

    # ------------------------------------------------------------------
    #  View resize -> scene relayout
    # ------------------------------------------------------------------

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # Debounce to avoid excessive relayouts during interactive resize
        if self._resize_timer_id >= 0:
            self.killTimer(self._resize_timer_id)
        self._resize_timer_id = self.startTimer(50)  # 50 ms coalescing

    def timerEvent(self, event) -> None:
        if event.timerId() == self._resize_timer_id:
            self.killTimer(self._resize_timer_id)
            self._resize_timer_id = -1
            self._scene.schedule_relayout()
        else:
            super().timerEvent(event)

    # ------------------------------------------------------------------
    #  Background
    # ------------------------------------------------------------------

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        """
        Do nothing - leave the background completely transparent so that
        the parent widget’s background shows through.
        """
        pass

    # ------------------------------------------------------------------
    #  Keyboard event forwarding
    # ------------------------------------------------------------------

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # Ctrl+F -> request focus on filter bar
        if event.matches(QKeySequence.Find):
            self.focus_filter_requested.emit()
            event.accept()
            return

        # All other keys are forwarded to the scene
        self._scene.keyPressEvent(event)
