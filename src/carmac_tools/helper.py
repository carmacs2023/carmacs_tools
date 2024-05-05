import logging
import os
from typing import Deque
from collections import deque
import time
import locale
from typing import NoReturn
from logging import Logger

# region logging

# functions in helper.py are decoupled from the logger configuration in config.py to avoid circular dependencies
# therefore the functions in this module require a logger instance to be passed as parameter for ex; set_locale


# def set_logger(logger_instance):
#     # Function set_logger used to pass a logger instance from main program
#     global logger
#     logger = logger_instance
#     logger.debug(f'logger instance passed to module {__name__}')


def create_logger(filename: str, name: str, level=10, log_format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s') -> logging.Logger:
    """
    Creates and configures a logger for both file and console output.

    This function initializes a logger with specified logging level and format. It configures the logger
    to output logs to both a file and the console. The file to log to is derived from the provided filename,
    with logs being overwritten each time the logger is created.

    :param filename: The filename for the log file. The logger will use this name with a ".log" extension.
    :param name: The name of the logger. This can be __name__ to use the module's name.
    :param level: The logging level to capture. Default is logging. DEBUG (10).
                  Other levels include logging.INFO (20), logging. WARNING (30),
                  logging. ERROR (40), and logging. CRITICAL (50).
    :param log_format: The format for log messages. Default format includes timestamp, logger name,
                       log level, and the log message.

    The logger is configured to:
    - Write logs to a file named after the provided filename, with a ".log" extension, overwriting existing logs.
    - Output logs to the console.
    - Apply the same logging level and format to both file and console output.

    Example Usage:
    logger = create_logger('app', 'my_logger')
    logger.info('This is an info message')

    This will log 'This is an info message' to both the 'app.log' file and the console with the specified format.

    :returns: A configured logging.Logger object ready for logging messages.
    """

    # Creates a logger object with a file and console handler

    # logging.DEBUG(10)
    # logging.INFO(20)
    # logging.WARNING(30)
    # logging.ERROR(40)
    # logging.CRITICAL(50)

    # Creating a logging object
    new_logger = logging.getLogger(name)

    if new_logger.hasHandlers():
        new_logger.handlers.clear()  # Clear existing handlers to avoid duplicates if called multiple times

    new_logger.setLevel(level)

    # Create file handler (log to file)
    log_file = os.path.splitext(filename)[0] + ".log"       # to use this file´s name as log filename
    file_handler = logging.FileHandler(log_file, mode='w')  # to create a handler with filename and mode; w for always new or a for append

    # Create console handler (log to console)
    console_handler = logging.StreamHandler()

    # Set file handler log level (severity : DEBUG, INFO, WARNING, ERROR, CRITICAL)
    file_handler.setLevel(level)                    # set file handler level
    console_handler.setLevel(level)                 # set console handler level

    # Set file handler log format
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger object
    new_logger.addHandler(file_handler)
    new_logger.addHandler(console_handler)

    return new_logger

# endregion

# region rate limiter class


class RateLimiter:

    def __init__(self, max_requests: int, interval_seconds: int):
        """
        Initializes a RateLimiter object with a maximum number of requests allowed over a specified interval in seconds.

        :param max_requests: The maximum number of requests allowed.
        :param interval_seconds: The time interval in seconds over which the maximum number of requests is calculated.
        """
        self.max_requests = max_requests
        self.interval_seconds = interval_seconds
        self.timestamps: Deque[float] = deque()

    def wait_for_request_slot(self):
        """
        Waits for an available request slot based on the rate limit configuration.
        This method blocks execution until a request slot is available.
        """
        current_time = time.time()
        # Clear out timestamps outside the current interval
        while self.timestamps and current_time - self.timestamps[0] > self.interval_seconds:
            self.timestamps.popleft()

        # Wait for a slot to become available if max requests are reached
        while len(self.timestamps) >= self.max_requests:
            time_to_wait = self.interval_seconds - (current_time - self.timestamps[0])
            time.sleep(time_to_wait)
            current_time = time.time()
            while self.timestamps and current_time - self.timestamps[0] > self.interval_seconds:
                self.timestamps.popleft()

        self.timestamps.append(current_time)

# endregion


# region locale


def set_locale(logger: Logger) -> NoReturn:

    """
    Sets the application's locale to US English with UTF-8 encoding.

    This function attempts to change the system locale settings to US English (UTF-8 encoding) for all categories.
    It logs the current locale before the change and the new locale after the attempt. If the locale setting fails,
    the function logs the error and re-raises the exception to be handled by the caller.

    Raises:
        locale.Error: If setting the locale fails, the error is logged and the exception is raised to the caller.
    """

    try:
        # Log current locale before attempting to change
        current_locale = locale.getlocale()  # Get and store current locale
        logger.debug(f'Current Locale : {current_locale}')

        # Attempt to set new locale
        new_locale = locale.setlocale(locale.LC_ALL, ("en_US", "UTF-8"))
        logger.info(f'Set Locale to: {new_locale}')

    except locale.Error as e:
        logger.error(f'Failed to set locale: {e}')
        # Include error handling to manage scenarios where setting locale fails due to OS-level restrictions, incorrect locale identifiers...etc.
        raise RuntimeError(f"Failed to set locale due to: {e}")

# endregion
