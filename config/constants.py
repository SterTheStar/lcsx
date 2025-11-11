"""
Constants for LCSX configuration.
Centralized configuration values to improve maintainability.
"""

# Default values
DEFAULT_PORT = 6040
DEFAULT_SHELL = '/bin/bash'
DEFAULT_USER = 'lcsx'
DEFAULT_HOSTNAME = 'debian'
DEFAULT_PASSWORD = '123456'

# File permissions
PROOT_PERMISSIONS = 0o755

# DNS servers
DNS_SERVERS = ['8.8.8.8', '1.1.1.1', '9.9.9.9']

# Proot binary URLs (using specific commit for stability)
PROOT_BASE_URL = "https://raw.githubusercontent.com/SterTheStar/lcsx/8d13901c99e8a222838999e11682ea0a7d797940/libs"
PROOT_X86_64_URL = f"{PROOT_BASE_URL}/proot"
PROOT_ARM64_URL = f"{PROOT_BASE_URL}/prootarm64"

# Proot-distro version
PROOT_DISTRO_VERSION = "v4.29.0"
PROOT_DISTRO_BASE_URL = f"https://github.com/termux/proot-distro/releases/download/{PROOT_DISTRO_VERSION}"

# GoTTY version and URL
GOTTY_VERSION = "v1.0.1"
GOTTY_BASE_URL = f"https://github.com/yudai/gotty/releases/download/{GOTTY_VERSION}"

# SSHX URLs
SSHX_X86_64_URL = "https://sshx.s3.amazonaws.com/sshx-x86_64-unknown-linux-musl.tar.gz"
SSHX_ARM64_URL = "https://sshx.s3.amazonaws.com/sshx-aarch64-unknown-linux-musl.tar.gz"

# Network timeouts (in seconds)
DOWNLOAD_TIMEOUT = 300  # 5 minutes
CONNECTION_TIMEOUT = 30  # 30 seconds

# Retry configuration
MAX_DOWNLOAD_RETRIES = 3
RETRY_DELAY = 5  # seconds

