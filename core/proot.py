import subprocess
import os
import sys
import urllib.request
import platform
from lcsx.ui.logger import print_main
from lcsx.core.gotty import run_gotty # Import run_gotty - ensure this is correctly loaded

def get_proot_path(data_dir, proot_bin):
    """Get the path to the proot binary."""
    return os.path.join(data_dir, 'libs', proot_bin)

def setup_proot_binary(data_dir, proot_bin):
    """Downloads and sets up the proot binary if it doesn't exist."""
    proot_dir = os.path.join(data_dir, 'libs')
    os.makedirs(proot_dir, exist_ok=True)
    proot_path = os.path.join(proot_dir, proot_bin)

    if not os.path.exists(proot_path):
        print_main(f"Proot binary '{proot_bin}' not found. Downloading again...")
        arch = platform.machine()
        proot_url = ""
        if arch == 'x86_64':
            proot_url = "https://raw.githubusercontent.com/SterTheStar/lcsx/8d13901c99e8a222838999e11682ea0a7d797940/libs/proot"
        elif arch == 'aarch64':
            proot_url = "https://raw.githubusercontent.com/SterTheStar/lcsx/8d13901c99e8a222838999e11682ea0a7d797940/libs/prootarm64"
        else:
            raise Exception(f"Unsupported architecture for proot: {arch}")

        print_main(f"Downloading {proot_bin}...")
        urllib.request.urlretrieve(proot_url, proot_path)
        os.chmod(proot_path, 0o755)
        print_main(f"{proot_bin} downloaded and set executable.")
    return proot_path

def run_proot_command(data_dir, rootfs, command, input=None, capture_output=False, proot_bin='proot'):
    """Run a command inside proot."""
    proot_path = get_proot_path(data_dir, proot_bin)
    cmd = [proot_path, '-r', rootfs, '-0', '-w', '/']
    if isinstance(command, str):
        cmd.append(command)
    else:
        cmd.extend(command)
    return subprocess.run(cmd, input=input, capture_output=capture_output, text=True)

import psutil
import os

def start_proot_shell(config):
    """Start the proot shell with the configured prompt or sshx/gotty."""
    rootfs = config['rootfs']
    proot_bin = config['proot_bin']
    data_dir = config['data_dir']
    user = config['user']
    hostname = config['hostname']
    terminal_service = config.get('terminal_service')
    terminal_port = config.get('terminal_port')
    sshx_path = config.get('sshx_path')
    gotty_path = config.get('gotty_path')
    shell = config.get('shell', '/bin/bash')
    print_main(f"Starting proot shell as '{user}@{hostname}' using shell '{shell}'...")

    # Collect system info
    cpu_count = psutil.cpu_count()
    ram_total = psutil.virtual_memory().total
    disk_total = psutil.disk_usage('/').total

    proot_path = get_proot_path(data_dir, proot_bin)
    cmd = [proot_path, '-r', rootfs, '-0', '-w', '/']

    # Mount /proc from host to fix /proc/stat parsing error
    cmd.extend(['-b', '/proc:/proc'])

    if terminal_service == 'sshx' and sshx_path:
        abs_sshx_dir = os.path.abspath(os.path.dirname(sshx_path))
        cmd.extend(['-b', f'{abs_sshx_dir}:/sshx'])
        # Mount pseudo-terminals for better sshx compatibility
        cmd.extend(['-b', '/dev/ptmx:/dev/ptmx', '-b', '/dev/pts:/dev/pts', '-b', '/dev/tty:/dev/tty'])
        # Set permanent prompt for sshx shell
        command = [shell, '-c', f'export PS1="{user}@{hostname}# "; exec /sshx/sshx --shell {shell}']
    elif terminal_service == 'gotty' and gotty_path and terminal_port:
        abs_gotty_dir = os.path.abspath(os.path.dirname(gotty_path))
        cmd.extend(['-b', f'{abs_gotty_dir}:/gotty'])
        # Mount pseudo-terminals for gotty compatibility
        cmd.extend(['-b', '/dev/ptmx:/dev/ptmx', '-b', '/dev/pts:/dev/pts', '-b', '/dev/tty:/dev/tty'])
        # Construct the gotty command to run inside proot
        command = run_gotty(f'/gotty/{os.path.basename(gotty_path)}', terminal_port, f'export PS1="{user}@{hostname}# "; exec {shell}')
    elif terminal_service == 'native':
        command = [shell, '-c', f'export PS1="{user}@{hostname}# "; exec {shell}']
    else:
        command = [shell, '-c', f'export PS1="{user}@{hostname}# "; exec {shell}']

    # Pass system info as environment variables
    env_vars = [
        f'CPU_COUNT={cpu_count}',
        f'RAM_TOTAL={ram_total}',
        f'DISK_TOTAL={disk_total}'
    ]
    # Prepend env vars to command
    env_command = ['env'] + env_vars + command
    cmd.extend(env_command)

    subprocess.run(cmd)
