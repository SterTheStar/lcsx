"""
Setup functionality for LCSX.
Handles initial environment setup inside proot.
"""

import os
import shutil
import urllib.request
import urllib.error
import tarfile
import sys
import time
import tempfile
from lcsx.core.proot import run_proot_command, setup_proot_binary
from lcsx.core.resolv import set_resolv_conf
from lcsx.ui.logger import print_main as print_normal, print_error, print_warning, download_progress
from lcsx.config.constants import MAX_DOWNLOAD_RETRIES, RETRY_DELAY
from lcsx.core.validation import check_disk_space

def is_rootfs_valid(rootfs_path, shell='/bin/bash'):
    """Check if the rootfs is valid by checking for the specified shell."""
    return os.path.exists(os.path.join(rootfs_path, shell.lstrip('/')))

def install_alpine_packages(rootfs_path, proot_bin, data_dir):
    """Install base Alpine packages using static apk-tools if not already installed."""
    installed_marker = os.path.join(rootfs_path, '.installed')
    if os.path.exists(installed_marker):
        return

    print_normal("Installing Alpine base packages...")
    temp_dir = tempfile.mkdtemp()
    apk_url = "https://dl-cdn.alpinelinux.org/alpine/v3.9/main/x86_64/apk-tools-static-2.10.6-r0.apk"
    apk_path = os.path.join(temp_dir, 'apk-tools-static.apk')

    # Download apk-tools-static
    for attempt in range(MAX_DOWNLOAD_RETRIES):
        try:
            urllib.request.urlretrieve(apk_url, apk_path, reporthook=download_progress)
            break
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            if attempt < MAX_DOWNLOAD_RETRIES - 1:
                print_error(f"Download failed (attempt {attempt + 1}/{MAX_DOWNLOAD_RETRIES}): {e}")
                print_normal(f"Retrying in {RETRY_DELAY} seconds...")
                if os.path.exists(apk_path):
                    os.remove(apk_path)
                time.sleep(RETRY_DELAY)
            else:
                print_error(f"Failed to download apk-tools-static after {MAX_DOWNLOAD_RETRIES} attempts: {e}")
                shutil.rmtree(temp_dir)
                raise

    # Extract apk-tools-static
    try:
        with tarfile.open(apk_path, 'r:gz') as tar:
            tar.extractall(temp_dir)
    except Exception as e:
        print_error(f"Error extracting apk-tools-static: {e}")
        shutil.rmtree(temp_dir)
        raise

    # Copy apk.static to rootfs /tmp
    apk_static_src = os.path.join(temp_dir, 'sbin', 'apk.static')
    apk_static_dest = os.path.join(rootfs_path, 'tmp', 'apk.static')
    os.makedirs(os.path.dirname(apk_static_dest), exist_ok=True)
    shutil.copy2(apk_static_src, apk_static_dest)

    # Run apk.static inside proot to install packages
    apk_command = ['/tmp/apk.static', '-X', 'https://dl-cdn.alpinelinux.org/alpine/v3.9/main/', '-U', '--allow-untrusted', '--root', '/', 'add', 'alpine-base', 'apk-tools']
    try:
        proc = run_proot_command(data_dir, rootfs_path, apk_command, proot_bin=proot_bin, capture_output=True)
        if proc.returncode != 0:
            print_error(f"Failed to install Alpine packages: {proc.stderr}")
            shutil.rmtree(temp_dir)
            raise Exception(f"apk.static failed with return code {proc.returncode}")
        else:
            print_normal("Alpine packages installed successfully.")
    except Exception as e:
        print_error(f"Failed to install Alpine packages: {e}")
        shutil.rmtree(temp_dir)
        raise

    # Create installed marker
    with open(installed_marker, 'w') as f:
        f.write('installed\n')

    # Cleanup
    shutil.rmtree(temp_dir)

def download_and_extract(url, dest_dir):
    """Download and extract the rootfs tar.xz, return the rootfs path."""
    os.makedirs(dest_dir, exist_ok=True)
    tar_path = os.path.join(dest_dir, 'rootfs.tar.xz')
    
    # Estimate required space (typically rootfs is 100-500MB compressed, 1-3GB extracted)
    # We'll check for at least 1GB to be safe
    required_space = 1 * 1024 * 1024 * 1024  # 1 GB
    has_space, available, error_msg = check_disk_space(dest_dir, required_space)
    if not has_space:
        print_warning(error_msg)
        print_warning("Proceeding anyway, but download may fail if space is insufficient.")
    else:
        print_normal(f"Disk space check passed. Available: {available / (1024**3):.2f} GB")
    
    print_normal("Downloading rootfs...")
    # Retry logic for downloads
    for attempt in range(MAX_DOWNLOAD_RETRIES):
        try:
            urllib.request.urlretrieve(url, tar_path, reporthook=download_progress)
            break
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            if attempt < MAX_DOWNLOAD_RETRIES - 1:
                print_error(f"Download failed (attempt {attempt + 1}/{MAX_DOWNLOAD_RETRIES}): {e}")
                print_normal(f"Retrying in {RETRY_DELAY} seconds...")
                if os.path.exists(tar_path):
                    os.remove(tar_path)
                time.sleep(RETRY_DELAY)
            else:
                print_error(f"Failed to download rootfs after {MAX_DOWNLOAD_RETRIES} attempts: {e}")
                if os.path.exists(tar_path):
                    os.remove(tar_path)
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
    shell = config.get('shell', '/bin/bash')

    # Download and extract rootfs if not exists or invalid
    base_dir = os.path.join(data_dir, 'rootfs')
    rootfs = base_dir
    if os.path.exists(base_dir):
            # Check if subdir
        extracted_items = os.listdir(base_dir)
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(base_dir, extracted_items[0])):
            rootfs = os.path.join(base_dir, extracted_items[0])
        if not is_rootfs_valid(rootfs, shell):
            print_normal("Rootfs invalid, re-downloading...")
            shutil.rmtree(base_dir)
            rootfs = download_and_extract(distro_url, base_dir)
    else:
        rootfs = download_and_extract(distro_url, base_dir)

    config['rootfs'] = rootfs

    # Ensure proot binary is set up
    setup_proot_binary(data_dir, proot_bin)

    # Install Alpine packages if Alpine distro
    if 'alpine' in distro_url.lower():
        install_alpine_packages(rootfs, proot_bin, data_dir)

    # Set permanent prompt based on shell
    user = config['user']
    hostname = config['hostname']
    if shell == '/bin/bash':
        bashrc_path = os.path.join(rootfs, 'root', '.bashrc')
        try:
            with open(bashrc_path, 'a') as f:
                f.write(f'\nexport PS1="{user}@{hostname}# "\n')
        except (OSError, PermissionError) as e:
            print_normal(f"Warning: Could not update .bashrc: {e}")
    elif shell == '/bin/sh':
        profile_path = os.path.join(rootfs, 'root', '.profile')
        try:
            with open(profile_path, 'a') as f:
                f.write(f'\nexport PS1="{user}@{hostname}# "\n')
        except (OSError, PermissionError) as e:
            print_normal(f"Warning: Could not update .profile: {e}")

    # Save config after setup
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from config.config import save_config
    save_config(config, data_dir)
