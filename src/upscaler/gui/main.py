import logging
from typing import List, Optional

from PySide6.QtCore import Qt, Slot, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListView,
    QPushButton,
    QLabel,
    QMessageBox,
    QApplication,
    QStyle,
)

from .widgets import PreviewWidget
from ..config import Config
from ..pipeline import create_pipeline_session
from ..window import WindowInfo, activate_window, list_windows

logger = logging.getLogger(__name__)


class WindowListModel(QStandardItemModel):
    """Model that stores WindowInfo in UserRole."""

    def window_at(self, row: int) -> Optional[WindowInfo]:
        if row < 0 or row >= self.rowCount():
            return None
        return self.item(row, 0).data(Qt.UserRole)


class SelectorWindow(QMainWindow):
    """
    Main window that presents a filterable list of X11 application windows
    together with a live preview of the currently selected window.

    Double‑clicking an entry or pressing the “Start” button will:
    1. Activate (raise+focus) the selected window.
    2. Hide this window and launch the upscaling overlay + pipeline.
    """

    def __init__(self, config: Config, profiles: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.profiles = profiles
        self._session = None  # will hold the pipeline session reference

        self.setWindowTitle("Linux RT Upscaler – Select Window")
        self.setMinimumSize(800, 450)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        self._setup_ui()
        self._populate_list()

    # ------------------------------------------------------------------
    #  UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        """Build the central widget layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # --- Filter bar ----------------------------------------------------
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Fi<er:")
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Type to filter by title…")
        self.filter_edit.textChanged.connect(self._on_filter_changed)
        filter_label.setBuddy(self.filter_edit)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_edit)

        # --- List view ----------------------------------------------------
        self.list_view = QListView()
        self.list_view.setEditTriggers(QListView.NoEditTriggers)
        self.list_view.setSelectionMode(QListView.SingleSelection)
        self.list_view.doubleClicked.connect(self._on_start)
        self.model = WindowListModel()
        self.list_view.setModel(self.model)

        # --- Preview widget -----------------------------------------------
        self.preview = PreviewWidget(self, preview_width=260)

        # --- Horizontal panel: list + preview ----------------------------
        content_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_layout.addLayout(filter_layout)
        left_layout.addWidget(self.list_view)
        content_layout.addLayout(left_layout, stretch=1)
        content_layout.addWidget(self.preview, stretch=0)

        main_layout.addLayout(content_layout)

        # --- Buttons ------------------------------------------------------
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("&Refresh")
        self.refresh_btn.clicked.connect(self._refresh)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()
        self.start_btn = QPushButton("&Start")
        self.start_btn.setDefault(True)
        self.start_btn.clicked.connect(self._on_start)
        btn_layout.addWidget(self.start_btn)
        main_layout.addLayout(btn_layout)

        # Connect selection changes for preview update
        self.list_view.selectionModel().currentChanged.connect(
            self._on_selection_changed
        )

    # ------------------------------------------------------------------
    #  Window list management
    # ------------------------------------------------------------------

    def _populate_list(self, filter_text: str = "") -> None:
        """
        Re‑enumerate all visible application windows and rebuild the list.
        The selector’s own window is excluded, as well as windows with
        empty titles.
        """
        self.model.clear()
        try:
            windows: List[WindowInfo] = list_windows()
        except Exception:
            logger.exception("Failed to enumerate windows")
            QMessageBox.warning(self, "Error", "Could not enumerate windows.")
            return

        # Ignore the selector’s own window
        own_handle = int(self.winId())
        filter_lower = filter_text.lower().strip()

        for win in windows:
            if win.handle == own_handle:
                continue
            # Skip windows with empty titles (usually invisible or useless)
            if not win.title.strip():
                continue
            if filter_lower and filter_lower not in win.title.lower():
                continue

            item = QStandardItem(f"{win.title}   ({win.width}×{win.height})")
            item.setData(win, Qt.UserRole)
            item.setToolTip(f"Handle: 0x{win.handle:x}")
            item.setIcon(self.style().standardIcon(QStyle.SP_TitleBarNormalButton))
            self.model.appendRow(item)

        if self.model.rowCount() > 0 and not self.list_view.currentIndex().isValid():
            self.list_view.setCurrentIndex(self.model.index(0, 0))
        else:
            # No item selected → clear preview
            self.preview.set_target(None)

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------

    @Slot()
    def _refresh(self) -> None:
        """Refresh the list while keeping the current filter text."""
        self._populate_list(self.filter_edit.text())

    @Slot(str)
    def _on_filter_changed(self, text: str) -> None:
        self._populate_list(text)

    @Slot(QModelIndex, QModelIndex)
    def _on_selection_changed(
        self, current: QModelIndex, previous: QModelIndex
    ) -> None:
        """Update the preview when the selection changes."""
        if current.isValid():
            win_info = self.model.window_at(current.row())
            self.preview.set_target(win_info)
        else:
            self.preview.set_target(None)

    @Slot()
    def _on_start(self) -> None:
        """Activate the chosen window and launch the upscaling pipeline."""
        index = self.list_view.currentIndex()
        if not index.isValid():
            QMessageBox.information(
                self, "No Selection", "Please select a window first."
            )
            return

        win_info = self.model.window_at(index.row())
        if win_info is None:
            return

        # Raise and focus the target
        activate_window(win_info.handle)
        logger.info("Starting upscale for: %s", win_info.title)

        # Hide this window (it will be closed when the application exits)
        self.hide()
        self.preview.set_target(None)  # stop preview

        # Create the overlay and pipeline.
        try:
            session = create_pipeline_session(self.config, win_info)
        except Exception as e:
            logger.exception("Failed to start pipeline")
            QMessageBox.critical(None, "Error", f"Could not start pipeline:\n{e}")
            QApplication.instance().quit()
            return

        self._session = session  # keep reference

    # ------------------------------------------------------------------
    #  Cleanup
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        self.preview.set_target(None)
        super().closeEvent(event)
