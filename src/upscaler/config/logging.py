import logging
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ConsoleFormatter(logging.Formatter):
    """Minimal console formatter: plain message for INFO, 'LEVEL: message' otherwise."""

    COLORS = {
        logging.DEBUG: "\033[36m",  # cyan
        logging.WARNING: "\033[33m",  # yellow
        logging.ERROR: "\033[31m",  # red
        logging.CRITICAL: "\033[1;31m",  # bold red
    }
    RESET = "\033[0m"

    def __init__(self, fmt=None, use_color=True):
        super().__init__(fmt)
        self.use_color = use_color

    def format(self, record):
        msg = super().format(record)
        if not self.use_color:
            return msg

        if record.levelno == logging.INFO:
            return msg
        color = self.COLORS.get(record.levelno, "")
        if color:
            return f"{color}{record.levelname}:{self.RESET} {msg}"
        return f"{record.levelname}: {msg}"


def setup_logging(level: str, log_file: Optional[str]) -> None:
    """Configure logging with the given level and optional file output.

    Console uses a minimal format; file output always includes full timestamps
    and module names at DEBUG level.
    """
    log_level = getattr(logging, level.upper(), logging.WARNING)

    # Clear any existing handlers to avoid duplicates
    root = logging.getLogger()
    root.handlers.clear()

    # ---- Console handler (minimal) ----------------------------------------
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(log_level)
    console_formatter = ConsoleFormatter("%(message)s")  # base format yields plain text
    console.setFormatter(console_formatter)
    root.addHandler(console)

    # ---- File handler (full detail) ---------------------------------------
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        root.addHandler(file_handler)
        root_level = min(log_level, logging.DEBUG)
    else:
        root_level = log_level

    root.setLevel(root_level)
