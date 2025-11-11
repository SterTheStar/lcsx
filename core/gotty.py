import os
import urllib.request
import urllib.error
import tarfile
import subprocess
import platform
import time
from lcsx.ui.logger import print_main, print_error
from lcsx.config.constants import (
    GOTTY_BASE_URL, PROOT_PERMISSIONS,
    MAX_DOWNLOAD_RETRIES, RETRY_DELAY
)

def get_gotty_url():
    """Determines the correct gotty download URL based on architecture."""
    arch = platform.machine()
    if arch == 'x86_64':
        return f"{GOTTY_BASE_URL}/gotty_linux_amd64.tar.gz"
    elif arch == 'aarch64':
        # Assuming aarch64 for ARM, adjust if gotty uses a different naming convention
        return f"{GOTTY_BASE_URL}/gotty_linux_arm64.tar.gz"
    else:
        raise Exception(f"Unsupported architecture for gotty: {arch}")

def download_gotty(data_dir):
    """Downloads the gotty tarball with retry logic."""
    gotty_url = get_gotty_url()
    gotty_dir = os.path.join(data_dir, 'libs', 'gotty')
    os.makedirs(gotty_dir, exist_ok=True)
    tar_path = os.path.join(gotty_dir, 'gotty.tar.gz')
    
    # Retry logic for downloads
    for attempt in range(MAX_DOWNLOAD_RETRIES):
        try:
            urllib.request.urlretrieve(gotty_url, tar_path)
            return tar_path, gotty_dir
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            if attempt < MAX_DOWNLOAD_RETRIES - 1:
                print_error(f"Download failed (attempt {attempt + 1}/{MAX_DOWNLOAD_RETRIES}): {e}")
                print_main(f"Retrying in {RETRY_DELAY} seconds...")
                if os.path.exists(tar_path):
                    os.remove(tar_path)
                time.sleep(RETRY_DELAY)
            else:
                print_error(f"Failed to download gotty after {MAX_DOWNLOAD_RETRIES} attempts: {e}")
                if os.path.exists(tar_path):
                    os.remove(tar_path)
                raise

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
    
    os.chmod(gotty_path, PROOT_PERMISSIONS)
    return gotty_path

def run_gotty(gotty_path, port, command, credential=None):
    """
    Runs the gotty server.
    
    Args:
        gotty_path: Path to gotty binary
        port: Port number
        command: Command to run
        credential: Basic auth credential in format 'user:pass' (optional)
    
    Returns:
        List of command arguments for gotty
    """
    # gotty -a 0.0.0.0 -p 25656 --credential "user:pass" -w bash -c "command"
    # Note: --credential must come before -w and -c
    gotty_cmd = [gotty_path, '-a', '0.0.0.0', '-p', str(port)]
    
    # Add credential if provided (must be before -w and -c)
    if credential:
        gotty_cmd.extend(['--credential', credential])
    
    # Add -w and -c after credential
    gotty_cmd.extend(['-w', 'bash', '-c', command])
    
    # This will be run by proot, so we just return the command to be executed by proot
    return gotty_cmd
