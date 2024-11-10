import logging
from datetime import date
from pathlib import Path

from app.core.config import settings


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Creates and configures a logger with both stream and file handlers.

    Args:
        name (str | None): The name of the logger. If None, the default module name is used.

    Returns:
        logging.Logger: Configured logger instance.
    """

    # Determine the logger name
    if name is None:
        name = __name__.split(".")[0]

    # Set logging level based on the environment
    log_level = logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG

    # Create the logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Prevent log messages from propagating to the root logger
    logger.propagate = False

    # Define log message format
    log_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-7s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create a stream handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_formatter)

    # Create a file handler for log files
    today = date.today()
    log_directory = Path(settings.LOG_DIR) / str(today.year) / str(today.month) / str(today.day)
    if not log_directory.exists():
        log_directory.mkdir(parents=True)

    access_file_handler = logging.FileHandler(log_directory / "access.log", encoding="utf-8")
    access_file_handler.setLevel(log_level)
    access_file_handler.setFormatter(log_formatter)

    # Create a separate file handler for error logs
    error_file_handler = logging.FileHandler(log_directory / "error.log", encoding="utf-8")
    error_file_handler.setLevel(logging.WARNING)
    error_file_handler.setFormatter(log_formatter)

    # Add handlers to the logger if not already present
    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(access_file_handler)
        logger.addHandler(error_file_handler)

    # Set up SQLAlchemy logging
    if log_level == logging.DEBUG:
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        sqlalchemy_logger.setLevel(logging.INFO)
        sqlalchemy_logger.propagate = False  # Prevent propagation to parent handlers

        # Create a file handler for SQLAlchemy logs
        sqlalchemy_file_handler = logging.FileHandler(log_directory / "sqlalchemy.log", encoding="utf-8")
        sqlalchemy_file_handler.setLevel(logging.INFO)
        sqlalchemy_file_handler.setFormatter(log_formatter)

        if not sqlalchemy_logger.hasHandlers():
            sqlalchemy_logger.addHandler(sqlalchemy_file_handler)

    return logger
