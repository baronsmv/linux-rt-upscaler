import logging
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def setup_logging(level: str, log_file: Optional[str]) -> None:
    """Configure logging with the given level and optional file output.

    The console handler respects the specified level, while the file handler
    (if enabled) always logs at DEBUG level.
    """
    log_level = getattr(logging, level.upper(), logging.WARNING)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Clear any existing handlers to avoid duplicates
    root = logging.getLogger()
    root.handlers.clear()

    # Console handler
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(log_level)
    console.setFormatter(formatter)
    root.addHandler(console)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
        root_level = min(log_level, logging.DEBUG)
    else:
        root_level = log_level

    root.setLevel(root_level)
