import platform
import os
import urllib.request
import subprocess
from lcsx.ui.logger import print_main
from lcsx.core.gotty import setup_gotty
from lcsx.core.sshx import setup_sshx
from lcsx.config.constants import (
    DEFAULT_USER, DEFAULT_HOSTNAME, DEFAULT_PASSWORD,
    DEFAULT_PORT, PROOT_DISTRO_VERSION, PROOT_DISTRO_BASE_URL, ALPINE_DISTRO_BASE_URL
)

def auto_setup(pre_data_dir=None, force_gotty=False, force_sshx=False, force_native=False, force_port=None, enable_auth=None, distro_name=None):
    """Automatic setup with predefined values."""
    user = DEFAULT_USER
    # Use a default hostname and override once the distro is chosen so the shell
    # prompt reflects the selected rootfs (e.g., alpine -> lcsx@alpine).
    hostname = DEFAULT_HOSTNAME
    password = DEFAULT_PASSWORD
    if force_port is None:
        force_port = DEFAULT_PORT

    # Set data directory
    base_dir = os.path.dirname(os.path.abspath(__import__('sys').argv[0]))
    data_dir = pre_data_dir if pre_data_dir else os.path.join(base_dir, 'data')

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

        # Select distro
        if distro_name and distro_name in distros:
            selected_distro = distro_name
        else:
            selected_distro = 'Debian'  # Default

        # Map distro name to a short hostname used in the shell prompt
        hostname_map = {
            'Debian': 'debian',
            'Arch Linux': 'arch',
            'Void': 'void',
            'Alpine': 'alpine',
        }

        distro_info = distros[selected_distro]
        distro_url = distro_info['url']
        shell = distro_info['shell']
        hostname = hostname_map.get(selected_distro, DEFAULT_HOSTNAME)
        print_main(f"Selected distribution: {selected_distro}")
    else:
        print(f"\033[1;91mUnsupported architecture: {arch}\033[0m")
        exit(1)

    terminal_service = None
    terminal_port = None
    sshx_path = None
    gotty_path = None # Initialize gotty_path

    if force_gotty:
        terminal_service = 'gotty'
        terminal_port = force_port
        print_main(f"Terminal service forced to gotty on port {terminal_port}.")
        # Check if enable_auth was provided via --credential argument
        if enable_auth is not None:
            if enable_auth:
                gotty_credential = f"{user}:{password}"
                print_main(f"GoTTY will use system credentials ({user}:****) for Basic Authentication.")
            else:
                gotty_credential = None
                print_main("GoTTY will run without authentication.")
        else:
            # Auto setup: authentication disabled by default
            gotty_credential = None
            print_main("GoTTY will run without authentication.")
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
        # Default to sshx for auto setup if no force flag is provided
        terminal_service = 'sshx'
        terminal_port = None
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
