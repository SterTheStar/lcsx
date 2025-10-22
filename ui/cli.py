"""
CLI interface for LCSX.
Handles user prompts.
"""

import platform
import os
import urllib.request
import subprocess
import sys
from lcsx.ui.logger import print_main, print_prompt
from lcsx.core.gotty import setup_gotty # Import the new setup_gotty function
from lcsx.core.sshx import setup_sshx # Import setup_sshx
from .auto import auto_setup

def prompt_setup(pre_data_dir=None, force_gotty=False, force_sshx=False, force_native=False, force_port=6040):
    """Prompt user for setup information."""
    print_prompt("Enter username to create:")
    user = input().strip()
    print_prompt("Enter hostname:")
    hostname = input().strip()
    print_prompt("Enter password for user:")
    password = input().strip()

    # Ask for custom data directory
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    default_data_dir = os.path.join(base_dir, 'data')
    if pre_data_dir:
        data_dir = pre_data_dir
    else:
        print_prompt(f"Do you want to use a custom path for the data folder? (default: {default_data_dir}) (y/n):")
        custom = input().strip().lower()
        if custom == 'y':
            print_prompt("Enter the path for the data folder (relative to binary or absolute):")
            data_dir_input = input().strip()
            if os.path.isabs(data_dir_input):
                data_dir = os.path.abspath(data_dir_input)
                print(f"\033[97mIn the next run, use './lcsx -a \"{data_dir}\"' to start with this data directory.\033[0m")
            else:
                data_dir = os.path.join(base_dir, data_dir_input)
                relative = os.path.relpath(data_dir, base_dir)
                print_prompt(f"In the next run, use './lcsx {relative}' to start with this data directory.")
        else:
            data_dir = default_data_dir

    rootfs = 'rootfs'  # Default rootfs directory

    # Detect architecture
    arch = platform.machine()
    if arch in ('x86_64', 'aarch64'):
        if arch == 'x86_64':
            proot_bin = 'proot'
        elif arch == 'aarch64':
            proot_bin = 'prootarm64'

        # Define available distros with compatibility levels
        distros = {
            'Debian': {
                'url': f"https://github.com/termux/proot-distro/releases/download/v4.29.0/debian-trixie-{arch}-pd-v4.29.0.tar.xz",
                'compat': 'Stable'
            },
            'Arch Linux': {
                'url': f"https://github.com/termux/proot-distro/releases/download/v4.29.0/archlinux-{arch}-pd-v4.29.0.tar.xz",
                'compat': 'Bleeding'
            },
            'Void': {
                'url': f"https://github.com/termux/proot-distro/releases/download/v4.29.0/void-{arch}-pd-v4.29.0.tar.xz",
                'compat': 'Balanced'
            },
        }

        def get_compat_color(compat):
            if compat == 'Stable':
                return '\033[92m'  # green
            elif compat == 'Balanced':
                return '\033[93m'  # yellow
            elif compat == 'Bleeding':
                return '\033[91m'  # red
            return '\033[0m'

        # Prompt user to choose distro
        print_main("Choose a Linux distribution:")
        for i, distro in enumerate(distros.keys(), 1):
            compat = distros[distro]['compat']
            color = get_compat_color(compat)
            reset = '\033[0m'
            badge = f"{color}[{compat}]{reset}"
            print(f"\033[97m{i}. {distro} {badge}\033[0m")
        print_prompt("Enter the number of your choice (default: 1 for Debian):")
        choice = input().strip()
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(distros):
                selected_distro = list(distros.keys())[choice_num - 1]
                distro_url = distros[selected_distro]['url']
            else:
                print("\033[1;91mInvalid choice, defaulting to Debian.\033[0m")
                distro_url = distros['Debian']['url']
        except ValueError:
            print("\033[1;91mInvalid input, defaulting to Debian.\033[0m")
            distro_url = distros['Debian']['url']
    else:
        print(f"\033[1;91mUnsupported architecture: {arch}\033[0m")
        exit(1)

    terminal_service = None
    terminal_port = None
    sshx_path = None
    gotty_path = None

    if force_gotty:
        terminal_service = 'gotty'
        terminal_port = force_port
        print_main(f"Terminal service forced to gotty on port {terminal_port}.")
        print_main("Setting up gotty...")
        gotty_path = setup_gotty(data_dir)
    elif force_sshx:
        terminal_service = 'sshx'
        terminal_port = None
        print_main("Terminal service forced to sshx.")
        print_main("Setting up sshx...")
        sshx_path = setup_sshx(data_dir)
    elif force_native:
        terminal_service = 'native'
        terminal_port = None
        print_main("Terminal service forced to native.")
    else:
        print_prompt("Choose a terminal service: (1) sshx (2) gotty (3) native (default: 1):")
        service_choice = input().strip()

        if service_choice == '2':
            terminal_service = 'gotty'
            print_prompt("Enter the port for gotty (default: 6040):")
            port_input = input().strip()
            terminal_port = int(port_input) if port_input.isdigit() else 6040
            print_main("Setting up gotty...")
            gotty_path = setup_gotty(data_dir)
        elif service_choice == '3':
            terminal_service = 'native'
            terminal_port = None
            sshx_path = None
            gotty_path = None
            print_main("Using native terminal.")
        else:
            terminal_service = 'sshx'
            terminal_port = None # sshx doesn't use a fixed port in this context
            print_main("Setting up sshx...")
            sshx_path = setup_sshx(data_dir)

    return {
        'user': user,
        'hostname': hostname,
        'password': password,
        'rootfs': rootfs,
        'arch': arch,
        'proot_bin': proot_bin,
        'distro_url': distro_url,
        'terminal_service': terminal_service,
        'terminal_port': terminal_port,
        'sshx_path': sshx_path,
        'gotty_path': gotty_path, # Add gotty_path to config
        'data_dir': data_dir
    }


