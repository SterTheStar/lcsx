"""
Logger utilities for LCSX UI.
Centralized print functions for consistent styling.
"""

def print_main(msg):
    """Print a main message with [!] prefix."""
    prefix = "\033[94m[\033[97m!\033[94m]\033[0m"
    print(f"{prefix} \033[97m{msg}\033[0m")

def print_error(msg):
    """Print an error message with [⨯] prefix."""
    prefix = "\033[1;91m[\033[97m⨯\033[91m]\033[0m"
    print(f"{prefix} \033[1m{msg}\033[0m")

def print_prompt(msg):
    """Print a prompt message with [!] prefix, ending with space."""
    prefix = "\033[94m[\033[97m!\033[94m]\033[0m"
    print(f"{prefix} \033[97m{msg}\033[0m ", end="")

def download_progress(block_num, block_size, total_size):
    """Progress callback for download."""
    if total_size > 0:
        percent = (block_num * block_size / total_size) * 100
        prefix = "\033[94m[\033[97m!\033[94m]\033[0m"
        print(f"\r{prefix} \033[97mDownloading rootfs... {percent:.2f}%\033[0m", end='', flush=True)
