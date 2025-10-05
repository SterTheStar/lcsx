"""
Configuration management for LCSX.
Handles loading, saving, and checking configuration.
"""

import json
import os
import sys

base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
data_dir = os.path.join(base_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

CONFIG_FILE = 'config.json'

def get_config_path():
    """Get the path to the config file."""
    return os.path.join(data_dir, CONFIG_FILE)

def is_configured():
    """Check if the configuration is set up."""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return False
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        required = ['user', 'hostname', 'password', 'rootfs', 'arch', 'proot_bin', 'distro_url']
        return all(key in config and config[key] for key in required)
    except (json.JSONDecodeError, KeyError):
        return False

def load_config():
    """Load the configuration from file."""
    config_path = get_config_path()
    with open(config_path, 'r') as f:
        return json.load(f)

def save_config(config):
    """Save the configuration to file."""
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
