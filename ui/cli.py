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
from .auto import auto_setup

def prompt_setup(pre_data_dir=None):
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
            sshx_url = "https://sshx.s3.amazonaws.com/sshx-x86_64-unknown-linux-musl.tar.gz"
            proot_url = "https://raw.githubusercontent.com/SterTheStar/lcsx/8d13901c99e8a222838999e11682ea0a7d797940/libs/proot"
        elif arch == 'aarch64':
            proot_bin = 'prootarm64'
            sshx_url = "https://sshx.s3.amazonaws.com/sshx-aarch64-unknown-linux-musl.tar.gz"
            proot_url = "https://raw.githubusercontent.com/SterTheStar/lcsx/8d13901c99e8a222838999e11682ea0a7d797940/libs/prootarm64"

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

    # Download proot binary if not exists
    proot_dir = os.path.join(data_dir, 'libs')
    os.makedirs(proot_dir, exist_ok=True)
    proot_path = os.path.join(proot_dir, proot_bin)
    if not os.path.exists(proot_path):
        print_main(f"Downloading {proot_bin}...")
        urllib.request.urlretrieve(proot_url, proot_path)
        os.chmod(proot_path, 0o755)
        print_main(f"{proot_bin} downloaded and set executable.")

    print_prompt("Do you want to use sshx? (y/n):")
    use_sshx = input().strip().lower() == 'y'
    sshx_path = None
    if use_sshx:
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


