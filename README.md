<div align="center">

# LCSX

LCSX simplifies PRoot setup, managing root filesystems, configuration, and shell integration.

</div><img width="1328" height="665" alt="sshxlcsx" src="https://github.com/user-attachments/assets/0045b977-0dac-41ad-af78-cfc83eceae51" />


---

## Features

* Multi-architecture (x86-64, ARM64)
* Interactive first-time setup
* Automatic setup mode
* Custom data directories
* Automatic root filesystem setup
* Supports static builds
* Input validation (username, password, hostname, ports, paths)
* Structured logging with file rotation
* Disk space verification before downloads
* GoTTY Basic Authentication support
* Retry logic for downloads
* Error handling and recovery

## Installation

### Prerequisites

* Python 3.6+
* Internet connection

### Quick Install

```bash
git clone https://github.com/SterTheStar/lcsx.git
cd lcsx
python3 lcsx.py
```

### Building

```bash
./build.sh
```

## Usage

```bash
# Run default (interactive setup)
python3 lcsx.py

# Automatic setup
python3 lcsx.py --auto

# Custom data directory (interactive setup)
python3 lcsx.py /path/to/custom/data

# Automatic setup with custom data directory
python3 lcsx.py --auto /path/to/custom/data

# Show help
python3 lcsx.py --help

# Use sshx terminal service
python3 lcsx.py --sshx

# Use gotty terminal service on default port (6040)
python3 lcsx.py --gotty

# Use gotty terminal service on a custom port (e.g., 3000)
python3 lcsx.py --gotty --port 3000

# Use gotty with Basic Authentication (using system credentials)
python3 lcsx.py --gotty --credential yes

# Use gotty without authentication
python3 lcsx.py --gotty --credential no

# Use gotty with custom credentials
python3 lcsx.py --gotty --gotty-credential "username:password"

# Use native terminal service
python3 lcsx.py --native

# Set logging level
python3 lcsx.py --log-level DEBUG

# Custom log file location
python3 lcsx.py --log-file /path/to/logfile.log
```

### Arguments

* `--auto`: Run automatic setup without user prompts, using predefined values.
* `--help` or `-h`: Display help information.
* `/path/to/custom/data`: Specify a custom data directory for configuration and files.
* `--gotty`: Use GoTTY as the terminal service. Can be combined with `--port` to specify the port.
* `--sshx`: Use sshx as the terminal service.
* `--native`: Use the native terminal service (no external terminal multiplexer).
* `--port <number>`: Specify the port for GoTTY (default: 6040). Only applicable when `--gotty` is used.
* `--credential <yes|no>`: Enable or disable Basic Authentication for GoTTY using system credentials. Only applicable with `--gotty`. If not specified, you will be prompted during setup.
* `--gotty-credential <user:pass>`: Set custom Basic Authentication credentials for GoTTY in format `username:password`. Only applicable with `--gotty`. Overrides `--credential`.
* `--log-level <DEBUG|INFO|WARNING|ERROR>`: Set logging level (default: INFO). Logs are saved to `~/.lcsx/logs/lcsx.log`.
* `--log-file <path>`: Specify custom log file location (default: `~/.lcsx/logs/lcsx.log`).

### Automatic Setup

When using `--auto`, LCSX uses the following default values. Note that the terminal service can be overridden by `--gotty`, `--sshx`, or `--native` command-line arguments.

* Username: `lcsx`
* Hostname: `debian`
* Password: `123456`
* Distribution: Debian (latest stable)
* Architecture: Auto-detected (x86-64 or ARM64)
* Data Directory: `/path/to/custom/data` (if provided) or `./data`
* Terminal Service: `sshx` (default, but can be overridden by command-line arguments)
* GoTTY Authentication: Disabled by default when using `--gotty` in auto setup. Can be enabled with `--credential yes`.

### GoTTY Basic Authentication

LCSX supports Basic Authentication for GoTTY terminal service:

* **System Credentials**: When enabled, GoTTY uses the same username and password configured during setup.
* **Automatic Setup**: During initial setup, you'll be asked if you want to enable authentication.
* **Command Line Control**: Use `--credential yes` to enable or `--credential no` to disable without prompts.
* **Custom Credentials**: Use `--gotty-credential "user:pass"` to set custom credentials.

Examples:
```bash
# Enable authentication using system credentials
python3 lcsx.py --gotty --credential yes

# Disable authentication
python3 lcsx.py --gotty --credential no

# Use custom credentials
python3 lcsx.py --gotty --gotty-credential "admin:secret123"
```

### First Run

LCSX will guide you to configure:

* Username, hostname, password (with validation)
* Distribution and architecture
* Data directory
* Terminal service (sshx, gotty, or native)
* GoTTY authentication (if using gotty)

### Logging

LCSX includes structured logging with the following features:

* **Log Location**: Logs are saved to `~/.lcsx/logs/lcsx.log` by default
* **Log Rotation**: Automatic rotation when log file reaches 10MB (keeps 5 backup files)
* **Log Levels**: DEBUG, INFO, WARNING, ERROR
* **Custom Log File**: Use `--log-file` to specify a custom location

Example:
```bash
# Run with DEBUG logging
python3 lcsx.py --log-level DEBUG

# Use custom log file
python3 lcsx.py --log-file /var/log/lcsx.log
```

### Input Validation

LCSX validates all user inputs:

* **Username**: 3-32 characters, alphanumeric with underscores/hyphens
* **Password**: Minimum length validation
* **Hostname**: RFC 1123 compliant hostname validation
* **Ports**: Valid range (1024-65535)
* **Paths**: Directory existence and writability checks
* **Disk Space**: Automatic verification before large downloads

## Building

```bash
python -m venv venv
source venv/bin/activate
pip install pyinstaller staticx psutil
./build.sh
```

## Contributing

Fork the repo, create a branch, commit, push, and open a Pull Request.

## License

GPL-3.0 License - see [LICENSE](LICENSE)

---

Made by [SterTheStar](https://github.com/SterTheStar)
