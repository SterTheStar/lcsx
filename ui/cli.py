"""
CLI interface for LCSX.
Handles user prompts.
"""

import getpass
import platform
import os
import urllib.request
import subprocess
import sys

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

data_dir = os.path.join(base_dir, 'data')

def prompt_setup():
    """Prompt user for setup information."""
    print("Welcome to LCSX setup.")
    user = input("Enter username to create: ").strip()
    hostname = input("Enter hostname: ").strip()
    password = getpass.getpass("Enter password for user: ")
    rootfs = 'rootfs'  # Default rootfs directory

    # Detect architecture
    arch = platform.machine()
    if arch == 'x86_64':
        proot_bin = 'proot'
        distro_url = "https://github.com/termux/proot-distro/releases/download/v4.29.0/debian-trixie-x86_64-pd-v4.29.0.tar.xz"
        sshx_url = "https://sshx.s3.amazonaws.com/sshx-x86_64-unknown-linux-musl.tar.gz"
        proot_url = "https://raw.githubusercontent.com/SterTheStar/lcsx/8d13901c99e8a222838999e11682ea0a7d797940/libs/proot"
    elif arch == 'aarch64':
        proot_bin = 'prootarm64'
        distro_url = "https://github.com/termux/proot-distro/releases/download/v4.29.0/debian-trixie-aarch64-pd-v4.29.0.tar.xz"
        sshx_url = "https://sshx.s3.amazonaws.com/sshx-aarch64-unknown-linux-musl.tar.gz"
        proot_url = "https://raw.githubusercontent.com/SterTheStar/lcsx/8d13901c99e8a222838999e11682ea0a7d797940/libs/prootarm64"
    else:
        print(f"Unsupported architecture: {arch}")
        exit(1)

    # Download proot binary if not exists
    proot_dir = os.path.join(data_dir, 'libs')
    os.makedirs(proot_dir, exist_ok=True)
    proot_path = os.path.join(proot_dir, proot_bin)
    if not os.path.exists(proot_path):
        print(f"Downloading {proot_bin}...")
        urllib.request.urlretrieve(proot_url, proot_path)
        os.chmod(proot_path, 0o755)
        print(f"{proot_bin} downloaded and set executable.")

    use_sshx = input("Do you want to use sshx? (y/n): ").strip().lower() == 'y'
    sshx_path = None
    if use_sshx:
        print("Downloading sshx...")
        sshx_dir = os.path.join(data_dir, 'libs', 'sshx')
        os.makedirs(sshx_dir, exist_ok=True)
        tar_path = os.path.join(sshx_dir, 'sshx.tar.gz')
        urllib.request.urlretrieve(sshx_url, tar_path)
        subprocess.run(['tar', '-xf', tar_path, '-C', sshx_dir], check=True)
        os.remove(tar_path)
        sshx_path = os.path.join(sshx_dir, 'sshx')
        print("sshx downloaded and extracted.")

    return {
        'user': user,
        'hostname': hostname,
        'password': password,
        'rootfs': rootfs,
        'arch': arch,
        'proot_bin': proot_bin,
        'distro_url': distro_url,
        'use_sshx': use_sshx,
        'sshx_path': sshx_path
    }
