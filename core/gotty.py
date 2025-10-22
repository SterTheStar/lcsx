import os
import urllib.request
import tarfile
import subprocess
import platform
from lcsx.ui.logger import print_main

GOTTY_URL_BASE = "https://github.com/yudai/gotty/releases/download/v1.0.1/"

def get_gotty_url():
    """Determines the correct gotty download URL based on architecture."""
    arch = platform.machine()
    if arch == 'x86_64':
        return f"{GOTTY_URL_BASE}gotty_linux_amd64.tar.gz"
    elif arch == 'aarch64':
        # Assuming aarch64 for ARM, adjust if gotty uses a different naming convention
        return f"{GOTTY_URL_BASE}gotty_linux_arm64.tar.gz" # This might need to be confirmed
    else:
        raise Exception(f"Unsupported architecture for gotty: {arch}")

def download_gotty(data_dir):
    """Downloads the gotty tarball."""
    gotty_url = get_gotty_url()
    gotty_dir = os.path.join(data_dir, 'libs', 'gotty')
    os.makedirs(gotty_dir, exist_ok=True)
    tar_path = os.path.join(gotty_dir, 'gotty.tar.gz')
    
    urllib.request.urlretrieve(gotty_url, tar_path)
    return tar_path, gotty_dir

def extract_gotty(tar_path, gotty_dir):
    """Extracts the gotty tarball."""
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=gotty_dir)
    os.remove(tar_path)

def find_gotty_binary(gotty_dir):
    """Finds the gotty executable within the extracted directory."""
    for root, _, files in os.walk(gotty_dir):
        if 'gotty' in files:
            gotty_path = os.path.join(root, 'gotty')
            return gotty_path
    return None

def setup_gotty(data_dir):
    """Downloads, extracts, and sets up gotty."""
    gotty_dir = os.path.join(data_dir, 'libs', 'gotty')
    gotty_path = find_gotty_binary(gotty_dir)

    if not gotty_path or not os.path.exists(gotty_path):
        print_main(f"Gotty binary not found. Downloading again...")
        tar_path, gotty_dir = download_gotty(data_dir)
        extract_gotty(tar_path, gotty_dir)
        gotty_path = find_gotty_binary(gotty_dir)
        if not gotty_path:
            raise Exception("Could not find 'gotty' binary after extraction.")
    
    os.chmod(gotty_path, 0o755)
    return gotty_path

def run_gotty(gotty_path, port, command):
    """Runs the gotty server."""
    # gotty -a 0.0.0.0 -p 25656 -w bash
    # The command will be passed as a list of arguments to gotty
    gotty_cmd = [gotty_path, '-a', '0.0.0.0', '-p', str(port), '-w', 'bash', '-c', command]
    
    # This will be run by proot, so we just return the command to be executed by proot
    return gotty_cmd
