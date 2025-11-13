"""
Logger utilities for LCSX UI.
Centralized print functions for consistent styling.
Provides backward compatibility with old print functions while supporting structured logging.
"""

import logging
from lcsx.core.logger import get_logger, setup_logger

# Initialize logger if not already done
_logger = None

def _get_logger():
    """Get or initialize the logger."""
    global _logger
    if _logger is None:
        _logger = get_logger()
    return _logger

def print_main(msg):
    """Print a main message with [!] prefix."""
    prefix = "\033[94m[\033[97m!\033[94m]\033[0m"
    print(f"{prefix} \033[97m{msg}\033[0m")
    _get_logger().info(msg)

def print_error(msg):
    """Print an error message with [⨯] prefix."""
    prefix = "\033[1;91m[\033[97m⨯\033[91m]\033[0m"
    print(f"{prefix} \033[1m{msg}\033[0m")
    _get_logger().error(msg)

def print_prompt(msg):
    """Print a prompt message with [!] prefix, ending with space."""
    prefix = "\033[94m[\033[97m!\033[94m]\033[0m"
    print(f"{prefix} \033[97m{msg}\033[0m ", end="")
    _get_logger().debug(f"Prompt: {msg}")

def print_warning(msg):
    """Print a warning message."""
    prefix = "\033[93m[\033[97m⚠\033[93m]\033[0m"
    print(f"{prefix} \033[93m{msg}\033[0m")
    _get_logger().warning(msg)

def download_progress(block_num, block_size, total_size):
    """Progress callback for download."""
    if total_size > 0:
        percent = (block_num * block_size / total_size) * 100
        prefix = "\033[94m[\033[97m!\033[94m]\033[0m"
        print(f"\r{prefix} \033[97mDownloading rootfs... {percent:.2f}%\033[0m", end='', flush=True)
        # Log progress every 10%
        if int(percent) % 10 == 0:
            _get_logger().debug(f"Download progress: {percent:.2f}%")
