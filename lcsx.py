#!/usr/bin/env python3
"""
LCSX - GUI CLI for Proot Automation
Main entry point for the LCSX tool.
"""

import json
import os
import sys

from lcsx.core.proot import run_proot_command, start_proot_shell
from lcsx.core.setup import setup_environment
from lcsx.ui.cli import prompt_setup
from lcsx.ui.auto import auto_setup
from lcsx.ui.ascii import display_ascii
from lcsx.config.config import load_config, save_config, is_configured
from lcsx.ui.logger import print_main

def main():
    # Check for help option
    if len(sys.argv) > 1 and (sys.argv[1] in ('-h', '--help')):
        from .help import print_help
        print_help()
        return

    # Display ASCII art
    display_ascii()

    print_main("Welcome to LCSX setup.")

    # Check for arguments
    auto = False
    custom_data_dir = None
    args = sys.argv[1:]
    for arg in args:
        if arg == '--auto':
            auto = True
        elif not custom_data_dir:
            custom_data_dir = os.path.abspath(arg)
    if custom_data_dir:
        print_main(f"Using custom data directory: {custom_data_dir}")

    # Determine data directory
    data_dir = custom_data_dir if custom_data_dir else os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'data')
    default_data_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'data')

    # Handle config migration for custom data dir
    if custom_data_dir and not is_configured(data_dir):
        default_data_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'data')
        default_config_file = os.path.join(default_data_dir, 'config.json')
        if os.path.exists(default_config_file):
            custom_config_file = os.path.join(custom_data_dir, 'config.json')
            os.makedirs(custom_data_dir, exist_ok=True)
            import shutil
            shutil.copy(default_config_file, custom_config_file)
            with open(custom_config_file, 'r') as f:
                config = json.load(f)
            config['data_dir'] = custom_data_dir
            # Update proot_bin if it was in the old data dir
            if 'proot_bin' in config and config['proot_bin'].startswith(default_data_dir):
                old_proot_bin = config['proot_bin']
                config['proot_bin'] = config['proot_bin'].replace(default_data_dir, custom_data_dir, 1)
                # Copy the proot binary to the new location
                if os.path.exists(old_proot_bin):
                    os.makedirs(os.path.dirname(config['proot_bin']), exist_ok=True)
                    import shutil
                    shutil.copy2(old_proot_bin, config['proot_bin'])
            with open(custom_config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print_main("Configuration migrated to custom data directory.")

    # If auto flag is set, use auto_setup instead of prompt_setup
    if auto:
        if is_configured(data_dir):
            config = load_config(data_dir, default_data_dir)
            print_main(f"Configuration found. Starting LCSX for user '{config['user']}' on '{config['hostname']}'...")
            start_proot_shell(config)
        else:
            print_main("No configuration found. Running automatic setup...")
            config = auto_setup(pre_data_dir=custom_data_dir)
            if custom_data_dir:
                config['data_dir'] = custom_data_dir
            setup_environment(config)
            save_config(config, data_dir)
            print_main("Automatic setup complete. Starting LCSX...")
            start_proot_shell(config)
        return


    # Check if configured
    if is_configured(data_dir):
        config = load_config(data_dir, default_data_dir)
        print_main(f"Configuration found. Starting LCSX for user '{config['user']}' on '{config['hostname']}'...")
        start_proot_shell(config)
    else:
        print_main("No configuration found. Setting up LCSX...")
        config = prompt_setup(pre_data_dir=custom_data_dir)
        if custom_data_dir:
            config['data_dir'] = custom_data_dir
        setup_environment(config)
        save_config(config, data_dir)
        print_main("Setup complete. Starting LCSX...")
        start_proot_shell(config)

if __name__ == "__main__":
    main()
