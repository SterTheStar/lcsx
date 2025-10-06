"""
Automatic setup for LCSX.
Handles automatic setup with predefined values.
"""

import platform
import os
import urllib.request
import subprocess
from lcsx.ui.logger import print_main

def auto_setup(pre_data_dir=None):
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
            sshx_url = "https://sshx.s3.amazonaws.com/sshx-x86_64-unknown-linux-musl.tar.gz"
            proot_url = "https://raw.githubusercontent.com/SterTheStar/lcsx/8d13901c99e8a222838999e11682ea0a7d797940/libs/proot"
        elif arch == 'aarch64':
            proot_bin = 'prootarm64'
            sshx_url = "https://sshx.s3.amazonaws.com/sshx-aarch64-unknown-linux-musl.tar.gz"
            proot_url = "https://raw.githubusercontent.com/SterTheStar/lcsx/8d13901c99e8a222838999e11682ea0a7d797940/libs/prootarm64"

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

    # Download proot binary if not exists
    proot_dir = os.path.join(data_dir, 'libs')
    os.makedirs(proot_dir, exist_ok=True)
    proot_path = os.path.join(proot_dir, proot_bin)
    if not os.path.exists(proot_path):
        print_main(f"Downloading {proot_bin}...")
        urllib.request.urlretrieve(proot_url, proot_path)
        os.chmod(proot_path, 0o755)
        print_main(f"{proot_bin} downloaded and set executable.")

    # Use sshx
    use_sshx = True
    sshx_path = None
    print_main("Downloading sshx...")
    sshx_dir = os.path.join(data_dir, 'libs', 'sshx')
    os.makedirs(sshx_dir, exist_ok=True)
    tar_path = os.path.join(sshx_dir, 'sshx.tar.gz')
    urllib.request.urlretrieve(sshx_url, tar_path)
    subprocess.run(['tar', '-xf', tar_path, '-C', sshx_dir], check=True)
    os.remove(tar_path)
    sshx_path = os.path.join(sshx_dir, 'sshx')
    print_main("sshx downloaded and extracted.")

    return {
        'user': user,
        'hostname': hostname,
        'password': password,
        'rootfs': rootfs,
        'arch': arch,
        'proot_bin': proot_bin,
        'distro_url': distro_url,
        'use_sshx': use_sshx,
        'sshx_path': sshx_path,
        'data_dir': data_dir
    }
