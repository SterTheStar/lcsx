"""
CLI interface for LCSX.
Handles user prompts.
"""

import platform
import os
import urllib.request
import subprocess
import sys
from lcsx.ui.logger import print_main, print_prompt, print_error, print_warning
from lcsx.core.gotty import setup_gotty
from lcsx.core.sshx import setup_sshx
from .auto import auto_setup
from lcsx.config.constants import (
    DEFAULT_PORT, PROOT_DISTRO_VERSION, PROOT_DISTRO_BASE_URL, ALPINE_DISTRO_BASE_URL
)
from lcsx.core.validation import (
    validate_username, validate_password, validate_port,
    validate_directory_path, validate_hostname, sanitize_input
)

def prompt_setup(pre_data_dir=None, force_gotty=False, force_sshx=False, force_native=False, force_port=None, enable_auth=None):
    """Prompt user for setup information."""
    # Username validation
    while True:
        print_prompt("Enter username to create:")
        user = sanitize_input(input().strip(), max_length=32)
        is_valid, error_msg = validate_username(user)
        if is_valid:
            break
        print_error(error_msg)
        print_main("Please try again.")
    
    # Hostname validation
    while True:
        print_prompt("Enter hostname:")
        hostname = sanitize_input(input().strip(), max_length=253)
        is_valid, error_msg = validate_hostname(hostname)
        if is_valid:
            break
        print_error(error_msg)
        print_main("Please try again.")
    
    # Password validation
    while True:
        print_prompt("Enter password for user:")
        password = input().strip()
        is_valid, error_msg = validate_password(password, min_length=6, require_complexity=False)
        if is_valid:
            break
        print_error(error_msg)
        print_main("Please try again.")

    # Ask for custom data directory with validation
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    default_data_dir = os.path.join(base_dir, 'data')
    if pre_data_dir:
        is_valid, error_msg, abs_path = validate_directory_path(pre_data_dir, must_exist=False, must_be_writable=True)
        if not is_valid:
            print_error(error_msg)
            print_warning(f"Falling back to default data directory: {default_data_dir}")
            data_dir = default_data_dir
        else:
            data_dir = abs_path
    else:
        print_prompt(f"Do you want to use a custom path for the data folder? (default: {default_data_dir}) (y/n):")
        custom = input().strip().lower()
        if custom == 'y':
            while True:
                print_prompt("Enter the path for the data folder (relative to binary or absolute):")
                data_dir_input = sanitize_input(input().strip())
                is_valid, error_msg, abs_path = validate_directory_path(data_dir_input, must_exist=False, must_be_writable=True)
                if is_valid:
                    data_dir = abs_path
                    if os.path.isabs(data_dir_input):
                        print(f"\033[97mIn the next run, use './lcsx -a \"{data_dir}\"' to start with this data directory.\033[0m")
                    else:
                        relative = os.path.relpath(data_dir, base_dir)
                        print_prompt(f"In the next run, use './lcsx {relative}' to start with this data directory.")
                    break
                else:
                    print_error(error_msg)
                    print_main("Please try again.")
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

        # Define available distros with compatibility levels and shells
        distros = {
            'Debian': {
                'url': f"{PROOT_DISTRO_BASE_URL}/debian-trixie-{arch}-pd-{PROOT_DISTRO_VERSION}.tar.xz",
                'compat': 'Stable',
                'shell': '/bin/bash'
            },
            'Arch Linux': {
                'url': f"{PROOT_DISTRO_BASE_URL}/archlinux-{arch}-pd-{PROOT_DISTRO_VERSION}.tar.xz",
                'compat': 'Bleeding',
                'shell': '/bin/bash'
            },
            'Void': {
                'url': f"{PROOT_DISTRO_BASE_URL}/void-{arch}-pd-{PROOT_DISTRO_VERSION}.tar.xz",
                'compat': 'Balanced',
                'shell': '/bin/bash'
            },
            'Alpine': {
                'url': f"{ALPINE_DISTRO_BASE_URL}/alpine-{arch}-pd-v4.30.1.tar.xz",
                'compat': 'Balanced',
                'shell': '/bin/sh'
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
                shell = distros[selected_distro]['shell']
            else:
                print("\033[1;91mInvalid choice, defaulting to Debian.\033[0m")
                distro_url = distros['Debian']['url']
                shell = distros['Debian']['shell']
        except ValueError:
            print("\033[1;91mInvalid input, defaulting to Debian.\033[0m")
            distro_url = distros['Debian']['url']
            shell = distros['Debian']['shell']
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
            if force_port is None:
                while True:
                    print_prompt(f"Enter the port for gotty (default: {DEFAULT_PORT}):")
                    port_input = input().strip()
                    if not port_input:
                        terminal_port = DEFAULT_PORT
                        break
                    is_valid, error_msg, port_int = validate_port(port_input)
                    if is_valid:
                        terminal_port = port_int
                        break
                    else:
                        print_error(error_msg)
                        print_main("Please try again.")
            else:
                is_valid, error_msg, port_int = validate_port(force_port)
                if not is_valid:
                    print_error(error_msg)
                    print_warning(f"Using default port {DEFAULT_PORT}")
                    terminal_port = DEFAULT_PORT
                else:
                    terminal_port = port_int
            
            # Check if enable_auth was provided via --credential argument
            if enable_auth is not None:
                # Use argument value (True/False)
                if enable_auth:
                    gotty_credential = f"{user}:{password}"
                    print_main(f"GoTTY will use system credentials ({user}:****) for Basic Authentication.")
                else:
                    gotty_credential = None
                    print_main("GoTTY will run without authentication.")
            else:
                # Ask if user wants to enable Basic Authentication
                print_prompt("Do you want to enable Basic Authentication for gotty? (y/n, default: n):")
                user_enable_auth = input().strip().lower()
                if user_enable_auth == 'y':
                    # Use system username and password for GoTTY Basic Authentication
                    gotty_credential = f"{user}:{password}"
                    print_main(f"GoTTY will use system credentials ({user}:****) for Basic Authentication.")
                else:
                    gotty_credential = None
                    print_main("GoTTY will run without authentication.")
            
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
        'shell': shell,
        'terminal_service': terminal_service,
        'terminal_port': terminal_port,
        'sshx_path': sshx_path,
        'gotty_path': gotty_path,
        'gotty_credential': gotty_credential if 'gotty_credential' in locals() else None,
        'data_dir': data_dir
    }


