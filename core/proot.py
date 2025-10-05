"""
Proot core functionality for LCSX.
Handles running proot commands and starting the shell.
"""

import subprocess
import os
import sys
from lcsx.ui.logger import print_main

def get_proot_path(data_dir, proot_bin):
    """Get the path to the proot binary."""
    return os.path.join(data_dir, 'libs', proot_bin)

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
    """Start the proot shell with the configured prompt or sshx."""
    rootfs = config['rootfs']
    proot_bin = config['proot_bin']
    data_dir = config['data_dir']
    user = config['user']
    hostname = config['hostname']
    use_sshx = config.get('use_sshx', False)
    sshx_path = config.get('sshx_path')
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

    if use_sshx and sshx_path:
        abs_sshx_dir = os.path.abspath(os.path.dirname(sshx_path))
        cmd.extend(['-b', f'{abs_sshx_dir}:/sshx'])
        # Mount pseudo-terminals for better sshx compatibility
        cmd.extend(['-b', '/dev/ptmx:/dev/ptmx', '-b', '/dev/pts:/dev/pts', '-b', '/dev/tty:/dev/tty'])
        # Set permanent prompt for sshx shell
        command = [shell, '-c', f'export PS1="{user}@{hostname}# "; exec /sshx/sshx --shell {shell}']
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
