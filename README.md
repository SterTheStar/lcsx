<div align="center">

# LCSX

LCSX automates setup and management of PRoot environments, simplifying the download of root filesystems, configuration, and shell integration for Linux distributions.

</div>

---

## Features

* Multi-architecture (x86-64, ARM64)
* Interactive first-time setup
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

# Custom data directory
python3 -m lcsx.lcsx -p mydata

# Show help
python3 -m lcsx.lcsx --help
```

### Options

| Option                 | Description            |
| ---------------------- | ---------------------- |
| `-h, --help`           | Show help message      |
| `-p PATH, --path PATH` | Specify data directory |

### First Run

LCSX will guide you to configure:

* Username, hostname, password
* Distribution and architecture
* Data directory

## Building

```bash
pip install pyinstaller staticx
./build.sh
```

## Contributing

Fork the repo, create a branch, commit, push, and open a Pull Request.

## License

GPL-3.0 License - see [LICENSE](LICENSE)

---

Made by [SterTheStar](https://github.com/SterTheStar)
