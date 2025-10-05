"""
Setup functionality for LCSX.
Handles initial environment setup inside proot.
"""

import os
import urllib.request
import urllib.error
import subprocess
import sys
from .proot import run_proot_command

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

data_dir = os.path.join(base_dir, 'data')

def download_progress(block_num, block_size, total_size):
    """Progress callback for download."""
    if total_size > 0:
        percent = (block_num * block_size / total_size) * 100
        print(f"\rDownloading rootfs... {percent:.2f}%", end='', flush=True)

def is_rootfs_valid(rootfs_path):
    """Check if the rootfs is valid by checking for /bin/bash."""
    return os.path.exists(os.path.join(rootfs_path, 'bin', 'bash'))

def download_and_extract(url, dest_dir):
    """Download and extract the rootfs tar.xz, return the rootfs path."""
    os.makedirs(dest_dir, exist_ok=True)
    tar_path = os.path.join(dest_dir, 'rootfs.tar.xz')
    print("Downloading rootfs...")
    try:
        urllib.request.urlretrieve(url, tar_path, reporthook=download_progress)
    except urllib.error.HTTPError as e:
        print(f"\nError downloading rootfs: {e}")
        raise
    print("\nExtracting rootfs...")
    result = subprocess.run(['tar', '--exclude=dev/*', '-xf', tar_path, '-C', dest_dir], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error extracting rootfs: {result.stderr}")
        raise Exception("Extraction failed")
    os.remove(tar_path)
    print("Extraction complete.")
    # Check for subdirectory
    extracted_items = os.listdir(dest_dir)
    if len(extracted_items) == 1 and os.path.isdir(os.path.join(dest_dir, extracted_items[0])):
        subdir = os.path.join(dest_dir, extracted_items[0])
        return subdir
    return dest_dir

def setup_environment(config):
    """Set up the proot environment: download rootfs."""
    distro_url = config['distro_url']
    proot_bin = config['proot_bin']

    # Download and extract rootfs if not exists or invalid
    base_dir = os.path.join(data_dir, 'rootfs')
    rootfs = base_dir
    if os.path.exists(base_dir):
        # Check if subdir
        extracted_items = os.listdir(base_dir)
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(base_dir, extracted_items[0])):
            rootfs = os.path.join(base_dir, extracted_items[0])
        if not is_rootfs_valid(rootfs):
            print("Rootfs invalid, re-downloading...")
            import shutil
            shutil.rmtree(base_dir)
            rootfs = download_and_extract(distro_url, base_dir)
    else:
        rootfs = download_and_extract(distro_url, base_dir)

    config['rootfs'] = rootfs

    # Set permanent prompt
    user = config['user']
    hostname = config['hostname']
    bashrc_path = os.path.join(rootfs, 'root', '.bashrc')
    with open(bashrc_path, 'a') as f:
        f.write(f'\nexport PS1="{user}@{hostname}# "\n')
