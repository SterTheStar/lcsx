import os
import urllib.request
import subprocess
import platform
from lcsx.ui.logger import print_main

def get_sshx_url():
    """Determines the correct sshx download URL based on architecture."""
    arch = platform.machine()
    if arch == 'x86_64':
        return "https://sshx.s3.amazonaws.com/sshx-x86_64-unknown-linux-musl.tar.gz"
    elif arch == 'aarch64':
        return "https://sshx.s3.amazonaws.com/sshx-aarch64-unknown-linux-musl.tar.gz"
    else:
        raise Exception(f"Unsupported architecture for sshx: {arch}")

def setup_sshx(data_dir):
    """Downloads, extracts, and sets up sshx."""
    sshx_url = get_sshx_url()
    sshx_dir = os.path.join(data_dir, 'libs', 'sshx')
    os.makedirs(sshx_dir, exist_ok=True)
    tar_path = os.path.join(sshx_dir, 'sshx.tar.gz')
    
    sshx_path = os.path.join(sshx_dir, 'sshx')
    if not os.path.exists(sshx_path):
        print_main(f"sshx binary not found. Downloading again...")
        urllib.request.urlretrieve(sshx_url, tar_path)
        subprocess.run(['tar', '-xf', tar_path, '-C', sshx_dir], check=True)
        os.remove(tar_path)
    return sshx_path
