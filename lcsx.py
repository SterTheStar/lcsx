#!/usr/bin/env python3
"""
LCSX - GUI CLI for Proot Automation
Main entry point for the LCSX tool.
"""

import json
import os
import sys
import argparse
import platform
import urllib.request
import subprocess

from lcsx.core.proot import run_proot_command, start_proot_shell, setup_proot_binary
from lcsx.core.setup import setup_environment
from lcsx.ui.cli import prompt_setup
from lcsx.ui.auto import auto_setup
from lcsx.ui.ascii import display_ascii
from lcsx.config.config import load_config, save_config, is_configured
from lcsx.ui.logger import print_main
from lcsx.core.gotty import setup_gotty
from lcsx.core.sshx import setup_sshx # Import the new setup_sshx function

def setup_terminal_service(config, data_dir, service, port=None):
    """Sets up the chosen terminal service and updates the config."""
    config['terminal_service'] = service
    config['terminal_port'] = port
    config['sshx_path'] = None
    config['gotty_path'] = None

    if service == 'sshx':
        print_main("Setting up sshx...")
        config['sshx_path'] = setup_sshx(data_dir)
        print_main("sshx setup complete.")
    elif service == 'gotty':
        print_main("Setting up gotty...")
        config['gotty_path'] = setup_gotty(data_dir)
        print_main("Gotty setup complete.")
    elif service == 'native':
        print_main("Using native terminal.")
    
    return config

def main():
    parser = argparse.ArgumentParser(description="LCSX - GUI CLI for Proot Automation")
    parser.add_argument('--auto', action='store_true', help="Run automatic setup")
    parser.add_argument('--gotty', action='store_true', help="Use gotty as the terminal service")
    parser.add_argument('--sshx', action='store_true', help="Use sshx as the terminal service")
    parser.add_argument('--native', action='store_true', help="Use native terminal service")
    parser.add_argument('--port', type=int, default=6040, help="Port for gotty (default: 6040). Only applicable with --gotty.")
    parser.add_argument('data_dir', nargs='?', help="Custom data directory")

    args = parser.parse_args()

    # Validate --port usage
    if args.port != 6040 and not args.gotty:
        print_main("Error: --port can only be used with --gotty.")
        sys.exit(1)

    # Display ASCII art
    display_ascii()

    print_main("Welcome to LCSX setup.")

    custom_data_dir = args.data_dir
    if custom_data_dir:
        custom_data_dir = os.path.abspath(custom_data_dir)
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

    config = None
    if is_configured(data_dir):
        config = load_config(data_dir, default_data_dir)

    # Determine if a terminal service is forced via command-line arguments
    forced_terminal_service = None
    if args.gotty:
        forced_terminal_service = 'gotty'
    elif args.sshx:
        forced_terminal_service = 'sshx'
    elif args.native:
        forced_terminal_service = 'native'

    # If a terminal service is forced and config exists, update it
    if forced_terminal_service and config:
        config = setup_terminal_service(config, data_dir, forced_terminal_service, args.port)
        save_config(config, data_dir)
        print_main(f"Terminal service updated to {forced_terminal_service}.")

    # Ensure proot binary is set up
    if config:
        setup_proot_binary(data_dir, config['proot_bin'])

    # If auto flag is set, use auto_setup instead of prompt_setup
    if args.auto:
        if config and is_configured(data_dir):
            print_main(f"Configuration found. Starting LCSX for user '{config['user']}' on '{config['hostname']}'...")
            start_proot_shell(config)
        else:
            print_main("No configuration found. Running automatic setup...")
            config = auto_setup(pre_data_dir=custom_data_dir, force_gotty=args.gotty, force_sshx=args.sshx, force_native=args.native, force_port=args.port)
            if custom_data_dir:
                config['data_dir'] = custom_data_dir
            setup_environment(config)
            save_config(config, data_dir)
            setup_proot_binary(data_dir, config['proot_bin'])
            print_main("Automatic setup complete. Starting LCSX...")
            start_proot_shell(config)
        return


    # Check if configured (for interactive mode)
    if config and is_configured(data_dir):
        print_main(f"Configuration found. Starting LCSX for user '{config['user']}' on '{config['hostname']}'...")
        start_proot_shell(config)
    else:
        print_main("No configuration found. Setting up LCSX...")
        config = prompt_setup(pre_data_dir=custom_data_dir, force_gotty=args.gotty, force_sshx=args.sshx, force_native=args.native, force_port=args.port)
        if custom_data_dir:
            config['data_dir'] = custom_data_dir
        setup_environment(config)
        save_config(config, data_dir)
        setup_proot_binary(data_dir, config['proot_bin'])
        print_main("Setup complete. Starting LCSX...")
        start_proot_shell(config)

if __name__ == "__main__":
    main()
