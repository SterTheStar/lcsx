"""
Structured logging for LCSX.
Provides logging functionality with file rotation and configurable levels.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Default log directory
DEFAULT_LOG_DIR = os.path.join(os.path.expanduser("~"), ".lcsx", "logs")
DEFAULT_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "lcsx.log")
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 backup files

# Logger instance
_logger = None


def setup_logger(log_level=logging.INFO, log_file=None, enable_console=False):
    """
    Setup the global logger with file and console handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses default location.
        enable_console: Whether to enable console output (default: False to avoid duplicates).
    
    Returns:
        Configured logger instance.
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    # Create logger
    _logger = logging.getLogger('lcsx')
    _logger.setLevel(log_level)
    
    # Prevent duplicate handlers
    if _logger.handlers:
        return _logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler with rotation
    if log_file is None:
        log_file = DEFAULT_LOG_FILE
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    _logger.addHandler(file_handler)
    
    # Console handler - disabled by default to avoid duplicate output
    # The formatted print functions in ui/logger.py handle console output
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        _logger.addHandler(console_handler)
    
    return _logger


def get_logger():
    """Get the global logger instance, creating it if necessary."""
    if _logger is None:
        return setup_logger()
    return _logger


def set_log_level(level):
    """
    Set the logging level.
    
    Args:
        level: Logging level string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
               or logging constant.
    """
    logger = get_logger()
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)

