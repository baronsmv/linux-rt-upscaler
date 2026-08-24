from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket


class InstanceManager(QObject):
    """
    Manages single‑instance behavior using a local server.

    The first instance starts a `QLocalServer` and listens for commands.
    Any subsequent instance connects to that server, sends a "show"
    command, and exits. The primary instance emits `show_requested`
    when such a command is received.
    """

    show_requested = Signal()

    def __init__(
        self,
        key: str = "linux-rt-upscaler-gui",
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._key = key
        self._server: Optional[QLocalServer] = None
        self._is_primary: bool = False

        # Try to connect to an existing server (secondary instance)
        socket = QLocalSocket()
        socket.connectToServer(self._key)
        if socket.waitForConnected(300):
            # Secondary instance
            socket.write(b"show")
            socket.flush()
            socket.waitForBytesWritten(100)
            socket.disconnectFromServer()
            self._is_primary = False
            return

        # No existing server, become primary
        socket.abort()
        socket.deleteLater()
        QLocalServer.removeServer(self._key)
        self._server = QLocalServer(self)
        self._server.listen(self._key)
        self._server.newConnection.connect(self._on_new_connection)
        self._is_primary = True

    @property
    def is_primary(self) -> bool:
        return self._is_primary

    def _on_new_connection(self) -> None:
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(1000):
            data = socket.readAll().data().decode()
            if data == "show":
                self.show_requested.emit()
        socket.disconnectFromServer()
        socket.deleteLater()
