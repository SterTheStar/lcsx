"""
Setup functionality for LCSX.
Handles initial environment setup inside proot.
"""

import os
import urllib.request
import urllib.error
import tarfile
import sys
from lcsx.core.proot import run_proot_command
from lcsx.core.resolv import set_resolv_conf
from lcsx.ui.logger import print_main as print_normal, print_error, download_progress

def is_rootfs_valid(rootfs_path):
    """Check if the rootfs is valid by checking for /bin/bash."""
    return os.path.exists(os.path.join(rootfs_path, 'bin', 'bash'))

def download_and_extract(url, dest_dir):
    """Download and extract the rootfs tar.xz, return the rootfs path."""
    os.makedirs(dest_dir, exist_ok=True)
    tar_path = os.path.join(dest_dir, 'rootfs.tar.xz')
    print_normal("Downloading rootfs...")
    try:
        urllib.request.urlretrieve(url, tar_path, reporthook=download_progress)
    except urllib.error.HTTPError as e:
        print_error(f"Error downloading rootfs: {e}")
        raise
    print_normal("Extracting rootfs...")
    try:
        with tarfile.open(tar_path, 'r:xz') as tar:
            # Extract all except dev/* and device files
            for member in tar.getmembers():
                if not member.name.startswith('dev/') and not member.isdev():
                    try:
                        tar.extract(member, dest_dir)
                    except PermissionError as e:
                        print_error(f"Permission denied, skipping file: {member.name}")
    except Exception as e:
        print_error(f"Error extracting rootfs: {e}")
        raise Exception("Extraction failed")
    os.remove(tar_path)
    print_normal("Extraction complete.")
    # Check for subdirectory
    extracted_items = os.listdir(dest_dir)
    if len(extracted_items) == 1 and os.path.isdir(os.path.join(dest_dir, extracted_items[0])):
        rootfs_path = os.path.join(dest_dir, extracted_items[0])
    else:
        rootfs_path = dest_dir
    # Set custom resolv.conf
    set_resolv_conf(rootfs_path)
    return rootfs_path

def setup_environment(config):
    """Set up the proot environment: download rootfs."""
    distro_url = config['distro_url']
    proot_bin = config['proot_bin']
    data_dir = config['data_dir']

    # Download and extract rootfs if not exists or invalid
    base_dir = os.path.join(data_dir, 'rootfs')
    rootfs = base_dir
    if os.path.exists(base_dir):
            # Check if subdir
        extracted_items = os.listdir(base_dir)
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(base_dir, extracted_items[0])):
            rootfs = os.path.join(base_dir, extracted_items[0])
        if not is_rootfs_valid(rootfs):
            print_normal("Rootfs invalid, re-downloading...")
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

    # Save config after setup
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from config.config import save_config
    save_config(config, data_dir)
