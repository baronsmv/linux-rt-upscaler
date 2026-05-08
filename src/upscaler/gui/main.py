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
    Main window that presents a filterable list of X11 application windows.

    Double‑clicking an entry or pressing the “Start” button will:
    1. Activate (raise+focus) the selected window.
    2. Hide this window and launch the upscaling overlay + pipeline.
    """

    def __init__(self, config: Config, profiles: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.profiles = profiles
        self.selected_index: Optional[QModelIndex] = None

        self.setWindowTitle("Linux RT Upscaler – Select Window")
        self.setMinimumSize(600, 400)
        # Use a simple application icon (optional)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        self._setup_ui()
        self._populate_list()

    def _setup_ui(self):
        """Build the central widget layout."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # --- Filter bar ------------------------------------------------
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Fi<er:")
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Type to filter by title…")
        self.filter_edit.textChanged.connect(self._on_filter_changed)
        filter_label.setBuddy(self.filter_edit)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_edit)
        layout.addLayout(filter_layout)

        # --- List view ------------------------------------------------
        self.list_view = QListView()
        self.list_view.setEditTriggers(QListView.NoEditTriggers)
        self.list_view.setSelectionMode(QListView.SingleSelection)
        self.list_view.doubleClicked.connect(self._on_start)
        layout.addWidget(self.list_view)

        self.model = WindowListModel()
        self.list_view.setModel(self.model)

        # --- Buttons -------------------------------------------------
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("&Refresh")
        self.refresh_btn.clicked.connect(self._populate_list)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()
        self.start_btn = QPushButton("&Start")
        self.start_btn.setDefault(True)
        self.start_btn.clicked.connect(self._on_start)
        btn_layout.addWidget(self.start_btn)
        layout.addLayout(btn_layout)

    def _populate_list(self, filter_text: str = ""):
        """Re‑enumerate windows and rebuild the model."""
        self.model.clear()
        try:
            windows: List[WindowInfo] = list_windows()
        except Exception:
            QMessageBox.warning(self, "Error", "Could not enumerate windows.")
            return

        filter_lower = filter_text.lower().strip()
        for win in windows:
            if filter_lower and filter_lower not in win.title.lower():
                continue
            item = QStandardItem(f"{win.title}   ({win.width}×{win.height})")
            item.setData(win, Qt.UserRole)
            item.setToolTip(f"Handle: 0x{win.handle:x}")
            # Use a generic icon – we could later fetch the window’s real icon
            item.setIcon(self.style().standardIcon(QStyle.SP_TitleBarNormalButton))
            self.model.appendRow(item)

        if self.model.rowCount() > 0 and not self.list_view.currentIndex().isValid():
            self.list_view.setCurrentIndex(self.model.index(0, 0))

    @Slot()
    def _on_filter_changed(self, text: str):
        self._populate_list(text)

    @Slot()
    def _on_start(self):
        """Activate the selected window and launch the pipeline."""
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

        # Create the overlay and pipeline.
        # If an error occurs, we show a message and close the app.
        try:
            session = create_pipeline_session(self.config, win_info)
        except Exception as e:
            logger.exception("Failed to start pipeline")
            QMessageBox.critical(None, "Error", f"Could not start pipeline:\n{e}")
            QApplication.instance().quit()
            return

        # Store the session somewhere so it isn’t garbage collected.
        # The session’s overlay will keep the application alive.
        self._session = session  # Keep reference
