import logging
from rich.logging import RichHandler
import os


logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X.%f]",
    handlers=[RichHandler()],
)


def set_log_level(log: logging.Logger, level: str) -> None:
    """Set the logging level of the logger.

    Parameters:
        log: The logging object
        level: The desired logging level: {DEBUG, INFO, WARN, ERROR, CRITICAL}
    """
    log.setLevel(getattr(logging, level.upper()))


def get_logger() -> logging.Logger:
    """Create a basic logger object.

    Returns:
        The logger object
    """
    log = logging.getLogger(__name__)
    level = os.environ.get("LOG_LEVEL", "DEBUG")
    set_log_level(log, level)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)
    return log


LOG = get_logger()
