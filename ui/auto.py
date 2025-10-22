import platform
import os
import urllib.request
import subprocess
from lcsx.ui.logger import print_main
from lcsx.core.gotty import setup_gotty # Import setup_gotty for potential future use or consistency
from lcsx.core.sshx import setup_sshx # Import setup_sshx

def auto_setup(pre_data_dir=None, force_gotty=False, force_sshx=False, force_native=False, force_port=6040):
    """Automatic setup with predefined values."""
    user = 'lcsx'
    hostname = 'debian'
    password = '123456'

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

        # Select Debian
        distros = {
            'Debian': {
                'url': f"https://github.com/termux/proot-distro/releases/download/v4.29.0/debian-trixie-{arch}-pd-v4.29.0.tar.xz",
                'compat': 'Stable'
            },
        }
        distro_url = distros['Debian']['url']
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
        'terminal_service': terminal_service,
        'terminal_port': terminal_port,
        'sshx_path': sshx_path,
        'gotty_path': gotty_path,
        'data_dir': data_dir
    }
