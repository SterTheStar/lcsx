"""
Configuration management for LCSX.
Handles loading, saving, and checking configuration.
"""

import json
import os
import sys

def is_configured(data_dir):
    """Check if the configuration is set up."""
    config_file = os.path.join(data_dir, 'config.json')
    if not os.path.exists(config_file):
        return False
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Core required fields
        core_required = ['user', 'hostname', 'password', 'rootfs', 'arch', 'proot_bin', 'distro_url', 'terminal_service']
        if not all(key in config and config[key] for key in core_required):
            return False

        terminal_service = config.get('terminal_service')
        if terminal_service == 'sshx':
            return 'sshx_path' in config and config['sshx_path']
        elif terminal_service == 'gotty':
            return 'gotty_path' in config and config['gotty_path'] and 'terminal_port' in config and config['terminal_port']
        elif terminal_service == 'native':
            return True # No specific path/port needed for native
        else:
            return False # Unknown terminal service

    except (json.JSONDecodeError, KeyError):
        return False

def load_config(data_dir, default_data_dir):
    """Load the configuration from file."""
    config_file = os.path.join(data_dir, 'config.json')
    with open(config_file, 'r') as f:
        config = json.load(f)
    # Ensure data_dir is set
    config['data_dir'] = data_dir
    # Update proot_bin if it was in the default data dir
    if 'proot_bin' in config and config['proot_bin'].startswith(default_data_dir):
        old_proot_bin = config['proot_bin']
        config['proot_bin'] = config['proot_bin'].replace(default_data_dir, data_dir, 1)
        # Copy the proot binary if it exists at old location but not at new
        if os.path.exists(old_proot_bin) and not os.path.exists(config['proot_bin']):
            os.makedirs(os.path.dirname(config['proot_bin']), exist_ok=True)
            import shutil
            shutil.copy2(old_proot_bin, config['proot_bin'])
    return config

def save_config(config, data_dir):
    """Save the configuration to file."""
    os.makedirs(data_dir, exist_ok=True)
    config_file = os.path.join(data_dir, 'config.json')
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
