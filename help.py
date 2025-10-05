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
    lcsx [PATH]

ARGUMENTS:
    PATH                    The path to the data directory where LCSX will store downloaded files,
                            configurations, and root filesystems. If not specified, defaults to
                            './data' relative to the binary location.
                            
LICENSE:
    GPL-3.0

SOURCE:
    https://github.com/SterTheStar/lcsx
"""
    print(help_text)
