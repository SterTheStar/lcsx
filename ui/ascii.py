"""
ASCII art display for LCSX.
"""

def display_ascii():
    """Display ASCII art for LCSX."""
    art_lines = [
        "      __    ____________  __",
        "     / /   / ____/ ___/ |/ /",
        "    / /   / /    \\__ \\|   /",
        "   / /___/ /___ ___/ /   |",
        "  /_____/\\____//____/_/|_|",
        "",
        "   \033[1;92m[x86-64]\033[0m \033[1;94m[ARM64]\033[0m \033[1;93m[GPL-3.0]\033[0m \033[1;95m[v1.0.1]\033[0m",
        "   \033[1;96m[github.com/SterTheStar/lcsx]\033[0m",
        ""
    ]

    # Rainbow colors for ASCII art
    colors = [
        "\033[91m",  # Red
        "\033[93m",  # Yellow
        "\033[92m",  # Green
        "\033[94m",  # Blue
        "\033[95m",  # Magenta
        "\033[0m",   # Reset for empty line
        "\033[0m",   # Reset for badges line
        "\033[0m",   # Reset for empty line
        "\033[0m"    # Reset for github line
    ]

    for i, line in enumerate(art_lines):
        color = colors[i % len(colors)]
        print(f"{color}{line}\033[0m")
