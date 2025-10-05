"""
Proot core functionality for LCSX.
Handles running proot commands and starting the shell.
"""

import subprocess
import os
import sys

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

def start_proot_shell(config):
    """Start the proot shell with the configured prompt or sshx."""
    rootfs = config['rootfs']
    proot_bin = config['proot_bin']
    data_dir = config['data_dir']
    user = config['user']
    hostname = config['hostname']
    use_sshx = config.get('use_sshx', False)
    sshx_path = config.get('sshx_path')
    print(f"Starting proot shell as '{user}@{hostname}'...")
    proot_path = get_proot_path(data_dir, proot_bin)
    cmd = [proot_path, '-r', rootfs, '-0', '-w', '/']
    if use_sshx and sshx_path:
        abs_sshx_dir = os.path.abspath(os.path.dirname(sshx_path))
        cmd.extend(['-b', f'{abs_sshx_dir}:/sshx'])
        # Mount pseudo-terminals for better sshx compatibility
        cmd.extend(['-b', '/dev/ptmx:/dev/ptmx', '-b', '/dev/pts:/dev/pts', '-b', '/dev/tty:/dev/tty'])
        command = ['/sshx/sshx']
    else:
        command = ['/bin/bash', '-c', f'export PS1="{user}@{hostname}# "; /bin/bash']
    cmd.extend(command)
    subprocess.run(cmd)
