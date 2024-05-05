import logging
from .helper import set_locale, create_logger

# Do NOT directly import any other modules that use the logger in config.py
# It could lead to circular dependencies and/or other initialization problems.
# Any logging activities inside other modules should use the global logger, by adding the following:
# from .config import get_global_logger
# logger = get_global_logger()

# global_logger = create_logger(filename=__file__, name='common_logger')  # Create a single logger for all modules
global_logger = create_logger(filename=__package__, name='common_logger')  # Create a single logger for all modules


def get_global_logger() -> logging.Logger:
    """
    Accessor function to retrieve the central logger instance.

    This function provides a centralized access point to the pre-configured global logger
    instance, ensuring that all modules within the package can use a consistent logging
    configuration.

    Returns:
        logging.Logger: The configured global logger instance.
    """
    return global_logger


# Set locale across all modules using the global logger
set_locale(logger=global_logger)
