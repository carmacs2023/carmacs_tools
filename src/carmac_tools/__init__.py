# init.py
from .config import get_global_logger
# initializing the logger before importing other modules.
# Python executes module-level code at import time.
# if any module logs a message as it is imported, the logger needs to be configured first.
# Ignore warning <PEP 8:E402 module level import not a top of file> for this specific case.

# This will ensure the logger is configured at the time of package import
get_global_logger()

from . import file_tools
from .file_tools import match_names_to_filenames
from . import df_tools
from . import helper
from . import dat_tools