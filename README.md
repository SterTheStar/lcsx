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

## Installation

### Prerequisites

* Python 3.6+
* Internet connection

### Quick Install

```bash
git clone https://github.com/SterTheStar/lcsx.git
cd lcsx
python3 -m lcsx.lcsx
```

### Building

```bash
./build.sh
```

## Usage

```bash
# Run default
python3 -m lcsx.lcsx

# Automatic setup with custom data directory
python3 -m lcsx.lcsx --auto /path/to/custom/data

# Custom data directory (interactive setup)
python3 -m lcsx.lcsx /path/to/custom/data

# Show help
python3 -m lcsx.lcsx --help
```

### Arguments

* `--auto`: Run automatic setup without user prompts, using predefined values.
* `--help` or `-h`: Display help information.
* `/path/to/custom/data`: Specify a custom data directory for configuration and files.

### Automatic Setup

When using `--auto`, LCSX uses the following default values:

* Username: `lcsx`
* Hostname: `debian`
* Password: `123456`
* Distribution: Debian (latest stable)
* Architecture: Auto-detected (x86-64 or ARM64)
* Data Directory: `/path/to/custom/data` (if provided) or `./data`
* SSHX: Enabled

### First Run

LCSX will guide you to configure:

* Username, hostname, password
* Distribution and architecture
* Data directory

## Building

```bash
pip install pyinstaller staticx psutil
./build.sh
```

## Contributing

Fork the repo, create a branch, commit, push, and open a Pull Request.

## License

GPL-3.0 License - see [LICENSE](LICENSE)

---

Made by [SterTheStar](https://github.com/SterTheStar)
