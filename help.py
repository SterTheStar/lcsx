"""
Help module for LCSX.
Provides comprehensive help information.
"""

def print_help():
    help_text = """
LCSX

DESCRIPTION:
    LCSX is a tool for automating Proot environments, allowing you to run Linux distributions
    inside a containerized environment on your system. It downloads and sets up root filesystems
    and provides a shell interface.

USAGE:
    ./lcsx [OPTIONS] [PATH]

OPTIONS:
    --auto                  Run automatic setup without user prompts, using predefined values.
    --help, -h              Display this help information.

ARGUMENTS:
    PATH                    The path to the custom data directory. If not specified, defaults to
                            './data' relative to the binary location.
                            
LICENSE:
    GPL-3.0

SOURCE:
    https://github.com/SterTheStar/lcsx
"""
    print(help_text)
