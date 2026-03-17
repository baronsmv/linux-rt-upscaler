import logging
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def setup_logging(level: str, log_file: Optional[str]) -> None:
    """Configure logging with the given level and optional file output."""

    handlers = [logging.StreamHandler(sys.stderr)]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.WARNING),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
