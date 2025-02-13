import os
from loguru import logger as loguru_logger
from typing import Any, Generator
from contextlib import contextmanager

# Define log configuration
LOG_DIRECTORY = "logs"
LOG_FILENAME = "application.log"
LOG_PATH = f"{LOG_DIRECTORY}/{LOG_FILENAME}"

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIRECTORY, exist_ok=True)

# Configure Loguru with enhanced format
loguru_logger.add(
    LOG_PATH,
    rotation="1 day",
    retention="10 days",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

class ApplicationLogger:
    """
    Enhanced logging utility class using Loguru for structured logging.
    Provides both synchronous and asynchronous logging capabilities with
    consistent formatting and error handling.
    """

    def __init__(self):
        """Initialize the ApplicationLogger instance."""
        pass

    def log_info(self, *args: Any, **kwargs: Any) -> None:
        """
        Log informational messages synchronously.
        
        Args:
            *args: Variable positional arguments for the message
            **kwargs: Additional keyword arguments including log level
        """
        log_level = kwargs.pop("level", "INFO")
        log_message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).log(log_level, log_message, **kwargs)

    async def log_info_async(self, *args: Any, **kwargs: Any) -> None:
        """
        Log informational messages asynchronously.
        
        Args:
            *args: Variable positional arguments for the message
            **kwargs: Additional keyword arguments including log level
        """
        log_level = kwargs.pop("level", "INFO")
        log_message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).log(log_level, log_message, **kwargs)

    def log_error(self, *args: Any, **kwargs: Any) -> None:
        """
        Log error messages synchronously.
        
        Args:
            *args: Variable positional arguments for the error message
            **kwargs: Additional keyword arguments for logging
        """
        error_message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).error(error_message, **kwargs)

    async def log_error_async(self, *args: Any, **kwargs: Any) -> None:
        """
        Log error messages asynchronously.
        
        Args:
            *args: Variable positional arguments for the error message
            **kwargs: Additional keyword arguments for logging
        """
        error_message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).error(error_message, **kwargs)

    def log_debug(self, *args: Any, **kwargs: Any) -> None:
        """
        Log debug messages synchronously.
        
        Args:
            *args: Variable positional arguments for the debug message
            **kwargs: Additional keyword arguments for logging
        """
        debug_message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).debug(debug_message, **kwargs)

    async def log_debug_async(self, *args: Any, **kwargs: Any) -> None:
        """
        Log debug messages asynchronously.
        
        Args:
            *args: Variable positional arguments for the debug message
            **kwargs: Additional keyword arguments for logging
        """
        debug_message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).debug(debug_message, **kwargs)

    def log_warning(self, *args: Any, **kwargs: Any) -> None:
        """
        Log warning messages synchronously.
        
        Args:
            *args: Variable positional arguments for the warning message
            **kwargs: Additional keyword arguments for logging
        """
        warning_message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).warning(warning_message, **kwargs)

    async def log_warning_async(self, *args: Any, **kwargs: Any) -> None:
        """
        Log warning messages asynchronously.
        
        Args:
            *args: Variable positional arguments for the warning message
            **kwargs: Additional keyword arguments for logging
        """
        warning_message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).warning(warning_message, **kwargs)


# Create global logger instance
application_logger = ApplicationLogger()