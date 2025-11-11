import os
import urllib.request
import urllib.error
import subprocess
import platform
import time
from lcsx.ui.logger import print_main, print_error
from lcsx.config.constants import (
    SSHX_X86_64_URL, SSHX_ARM64_URL,
    MAX_DOWNLOAD_RETRIES, RETRY_DELAY
)

def get_sshx_url():
    """Determines the correct sshx download URL based on architecture."""
    arch = platform.machine()
    if arch == 'x86_64':
        return SSHX_X86_64_URL
    elif arch == 'aarch64':
        return SSHX_ARM64_URL
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
        # Retry logic for downloads
        for attempt in range(MAX_DOWNLOAD_RETRIES):
            try:
                urllib.request.urlretrieve(sshx_url, tar_path)
                subprocess.run(['tar', '-xf', tar_path, '-C', sshx_dir], check=True)
                os.remove(tar_path)
                break
            except (urllib.error.URLError, urllib.error.HTTPError, OSError, subprocess.CalledProcessError) as e:
                if attempt < MAX_DOWNLOAD_RETRIES - 1:
                    print_error(f"Download/extraction failed (attempt {attempt + 1}/{MAX_DOWNLOAD_RETRIES}): {e}")
                    print_main(f"Retrying in {RETRY_DELAY} seconds...")
                    if os.path.exists(tar_path):
                        os.remove(tar_path)
                    time.sleep(RETRY_DELAY)
                else:
                    print_error(f"Failed to setup sshx after {MAX_DOWNLOAD_RETRIES} attempts: {e}")
                    if os.path.exists(tar_path):
                        os.remove(tar_path)
                    raise
    return sshx_path
