"""
Help module for LCSX.
Provides comprehensive help information.
"""

def print_help():
    help_text = """
LCSX - GUI CLI for Proot Automation

DESCRIPTION:
    LCSX is a tool for automating Proot environments, allowing you to run Linux distributions
    inside a containerized environment on your system. It downloads and sets up root filesystems
    and provides a shell interface.

USAGE:
    lcsx [OPTIONS] [PATH]

OPTIONS:
    -h, --help              Show this help message and exit
    -p PATH, --path PATH    Specify the data directory path (relative or absolute)
    -a, --absolute          Treat the specified path as absolute (must be used with -p)
    PATH                    Positional argument for data directory path (relative to binary)

ARGUMENTS:
    PATH                    The path to the data directory where LCSX will store downloaded files,
                            configurations, and root filesystems. If not specified, defaults to
                            './data' relative to the binary location.

EXAMPLES:
    lcsx                    Run LCSX with default data directory './data'
    lcsx mydata             Run LCSX with relative data directory './mydata'
    lcsx -p mydata          Same as above, using -p flag
    lcsx -a -p /home/user/data  Run LCSX with absolute data directory '/home/user/data'
    lcsx /tmp/lcsx_data     Run LCSX with absolute data directory '/tmp/lcsx_data' (if starts with /)

CONFIGURATION:
    On first run, LCSX will prompt for setup information including:
    - Username and hostname for the proot environment
    - Password for the user
    - Custom data directory path (optional)
    - Distribution URL and architecture

    Configuration is stored in the data directory as 'config.json'.

DATA DIRECTORY:
    The data directory contains:
    - config.json: Configuration file
    - rootfs/: Downloaded root filesystem
    - Other temporary files and logs

    By default, the data directory is './data' relative to the binary.
    You can specify a custom path using the options above.

BUILDING:
    To build a static binary, run the 'build.sh' script in the project root.
    This creates a self-contained executable that can be run on compatible systems.

LICENSE:
    GPL-3.0

SOURCE:
    https://github.com/SterTheStar/lcsx
"""
    print(help_text)
