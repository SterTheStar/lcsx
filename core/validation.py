"""
Input validation utilities for LCSX.
Provides validation functions for user inputs.
"""

import os
import re
import shutil
from pathlib import Path


def validate_username(username):
    """
    Validate username.
    
    Rules:
    - 3-32 characters
    - Only alphanumeric characters, underscores, and hyphens
    - Must start with a letter or underscore
    - Must not end with hyphen or underscore
    
    Args:
        username: Username to validate.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty."
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    
    if len(username) > 32:
        return False, "Username must be at most 32 characters long."
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens, and must start with a letter or underscore."
    
    # Check that it doesn't end with hyphen or underscore
    if username.endswith('-') or username.endswith('_'):
        return False, "Username cannot end with a hyphen or underscore."
    
    # Reserved names
    reserved = ['root', 'admin', 'administrator', 'system', 'bin', 'daemon', 'mail', 'nobody']
    if username.lower() in reserved:
        return False, f"Username '{username}' is reserved and cannot be used."
    
    return True, None


def validate_password(password, min_length=6, require_complexity=False):
    """
    Validate password.
    
    Args:
        password: Password to validate.
        min_length: Minimum password length.
        require_complexity: Whether to require complexity (uppercase, lowercase, number).
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "Password cannot be empty."
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long."
    
    if require_complexity:
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "Password must contain at least one uppercase letter, one lowercase letter, and one number."
    
    return True, None


def validate_port(port):
    """
    Validate port number.
    
    Args:
        port: Port number to validate (can be int or string).
    
    Returns:
        tuple: (is_valid, error_message, port_int)
    """
    try:
        port_int = int(port)
    except (ValueError, TypeError):
        return False, "Port must be a valid number.", None
    
    if port_int < 1024:
        return False, "Port must be 1024 or higher (privileged ports are not allowed).", None
    
    if port_int > 65535:
        return False, "Port must be 65535 or lower (maximum port number).", None
    
    return True, None, port_int


def validate_directory_path(path, must_exist=False, must_be_writable=False):
    """
    Validate directory path.
    
    Args:
        path: Directory path to validate.
        must_exist: Whether the directory must already exist.
        must_be_writable: Whether the directory must be writable.
    
    Returns:
        tuple: (is_valid, error_message, absolute_path)
    """
    if not path:
        return False, "Path cannot be empty.", None
    
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(os.path.expanduser(path))
        
        # Check if path exists
        if must_exist:
            if not os.path.exists(abs_path):
                return False, f"Directory does not exist: {abs_path}", None
            
            if not os.path.isdir(abs_path):
                return False, f"Path is not a directory: {abs_path}", None
        else:
            # Check if parent directory exists and is writable
            parent_dir = os.path.dirname(abs_path)
            if parent_dir and not os.path.exists(parent_dir):
                return False, f"Parent directory does not exist: {parent_dir}", None
        
        # Check if writable
        if must_be_writable:
            if must_exist:
                if not os.access(abs_path, os.W_OK):
                    return False, f"Directory is not writable: {abs_path}", None
            else:
                parent_dir = os.path.dirname(abs_path)
                if parent_dir and not os.access(parent_dir, os.W_OK):
                    return False, f"Parent directory is not writable: {parent_dir}", None
        
        return True, None, abs_path
        
    except (OSError, ValueError) as e:
        return False, f"Invalid path: {str(e)}", None


def validate_hostname(hostname):
    """
    Validate hostname.
    
    Rules:
    - 1-253 characters
    - Only alphanumeric characters, hyphens, and dots
    - Cannot start or end with hyphen or dot
    - Each label (between dots) max 63 characters
    
    Args:
        hostname: Hostname to validate.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not hostname:
        return False, "Hostname cannot be empty."
    
    if len(hostname) > 253:
        return False, "Hostname must be at most 253 characters long."
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', hostname):
        return False, "Hostname contains invalid characters or format."
    
    # Check labels
    labels = hostname.split('.')
    for label in labels:
        if len(label) > 63:
            return False, f"Hostname label '{label}' exceeds 63 characters."
        if label.startswith('-') or label.endswith('-'):
            return False, "Hostname labels cannot start or end with a hyphen."
    
    return True, None


def check_disk_space(path, required_bytes):
    """
    Check if there's enough disk space available.
    
    Args:
        path: Path to check disk space for.
        required_bytes: Required space in bytes.
    
    Returns:
        tuple: (has_space, available_bytes, error_message)
    """
    try:
        abs_path = os.path.abspath(path)
        # Get the mount point
        while not os.path.ismount(abs_path) and abs_path != os.path.dirname(abs_path):
            abs_path = os.path.dirname(abs_path)
        
        stat = shutil.disk_usage(abs_path)
        available = stat.free
        
        if available < required_bytes:
            return False, available, f"Insufficient disk space. Required: {required_bytes / (1024**3):.2f} GB, Available: {available / (1024**3):.2f} GB"
        
        return True, available, None
        
    except (OSError, ValueError) as e:
        return False, 0, f"Error checking disk space: {str(e)}"


def sanitize_input(input_str, max_length=None):
    """
    Sanitize user input by removing dangerous characters.
    
    Args:
        input_str: Input string to sanitize.
        max_length: Maximum length (truncate if longer).
    
    Returns:
        Sanitized string.
    """
    if not input_str:
        return ""
    
    # Remove control characters except newline and tab
    sanitized = ''.join(c for c in input_str if ord(c) >= 32 or c in '\n\t')
    
    # Strip whitespace
    sanitized = sanitized.strip()
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

