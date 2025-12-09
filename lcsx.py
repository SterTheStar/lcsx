#!/usr/bin/env python3
"""
LCSX - GUI CLI for Proot Automation
Main entry point for the LCSX tool.
"""

import json
import os
import shutil
import sys
import argparse
import platform
import urllib.request
import subprocess

# Add parent directory to path when running directly (before imports)
# This allows the script to be run as: python lcsx.py
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
# Add parent directory so 'lcsx' package can be found
if parent_dir and parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from lcsx.core.proot import run_proot_command, start_proot_shell, setup_proot_binary
from lcsx.core.setup import setup_environment
from lcsx.ui.cli import prompt_setup
from lcsx.ui.auto import auto_setup
from lcsx.ui.ascii import display_ascii
from lcsx.config.config import load_config, save_config, is_configured
from lcsx.ui.logger import print_main, print_prompt, print_error
from lcsx.core.gotty import setup_gotty
from lcsx.core.sshx import setup_sshx
from lcsx.config.constants import DEFAULT_PORT
from lcsx.core.logger import setup_logger
import logging

def setup_terminal_service(config, data_dir, service, port=None, credential=None, enable_auth=None):
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
        # Set credential if provided via CLI
        if credential:
            config['gotty_credential'] = credential
            print_main("Gotty credential configured from command line.")
        # If enable_auth is provided via --credential yes/no, use it
        elif enable_auth is not None:
            if enable_auth:
                # Use system username and password
                system_user = config.get('user')
                system_password = config.get('password')
                if system_user and system_password:
                    config['gotty_credential'] = f"{system_user}:{system_password}"
                    print_main(f"GoTTY will use system credentials ({system_user}:****) for Basic Authentication.")
                else:
                    config['gotty_credential'] = None
                    print_warning("System credentials not found. GoTTY will run without authentication.")
            else:
                config['gotty_credential'] = None
                print_main("GoTTY will run without authentication.")
        # If credential not in config (first time using gotty), ask user
        elif 'gotty_credential' not in config or config.get('gotty_credential') is None:
            # Ask if user wants to enable Basic Authentication
            print_prompt("Do you want to enable Basic Authentication for gotty? (y/n, default: n):")
            user_enable_auth = input().strip().lower()
            if user_enable_auth == 'y':
                # Use system username and password if available
                system_user = config.get('user')
                system_password = config.get('password')
                if system_user and system_password:
                    config['gotty_credential'] = f"{system_user}:{system_password}"
                    print_main(f"GoTTY will use system credentials ({system_user}:****) for Basic Authentication.")
                else:
                    config['gotty_credential'] = None
                    print_warning("System credentials not found. GoTTY will run without authentication.")
            else:
                config['gotty_credential'] = None
                print_main("GoTTY will run without authentication.")
        # If credential already exists in config, keep it (don't override)
        else:
            print_main(f"GoTTY will use existing credentials ({config.get('user', 'user')}:****) for Basic Authentication.")
        print_main("Gotty setup complete.")
    elif service == 'native':
        print_main("Using native terminal.")
    
    return config

def main():
    parser = argparse.ArgumentParser(description="LCSX - GUI CLI for Proot Automation")
    parser.add_argument('--auto', action='store_true', help="Run automatic setup")
    parser.add_argument('--debian', action='store_true', help="Use Debian as the distribution in auto setup")
    parser.add_argument('--alpine', action='store_true', help="Use Alpine as the distribution in auto setup")
    parser.add_argument('--arch', action='store_true', help="Use Arch Linux as the distribution in auto setup")
    parser.add_argument('--void', action='store_true', help="Use Void as the distribution in auto setup")
    parser.add_argument('--gotty', action='store_true', help="Use gotty as the terminal service")
    parser.add_argument('--sshx', action='store_true', help="Use sshx as the terminal service")
    parser.add_argument('--native', action='store_true', help="Use native terminal service")
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f"Port for gotty (default: {DEFAULT_PORT}). Only applicable with --gotty.")
    parser.add_argument('--gotty-credential', help="Basic auth credential for gotty in format 'user:pass'. Only applicable with --gotty.")
    parser.add_argument('--credential', choices=['yes', 'no'], help="Enable/disable Basic Authentication for gotty using system credentials (yes/no). Only applicable with --gotty.")
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help="Set logging level (default: INFO)")
    parser.add_argument('--log-file', help="Path to log file (default: ~/.lcsx/logs/lcsx.log)")
    parser.add_argument('data_dir', nargs='?', help="Custom data directory")

    args = parser.parse_args()
    
    # Setup logging (console disabled to avoid duplicate output with formatted prints)
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    setup_logger(log_level=log_level, log_file=args.log_file, enable_console=False)

    # Validate --port usage
    if args.port != DEFAULT_PORT and not args.gotty:
        print_main("Error: --port can only be used with --gotty.")
        sys.exit(1)
    
    # Validate --gotty-credential usage
    if args.gotty_credential and not args.gotty:
        print_main("Error: --gotty-credential can only be used with --gotty.")
        sys.exit(1)
    
    # Validate --credential usage
    if args.credential and not args.gotty:
        print_main("Error: --credential can only be used with --gotty.")
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
        # Validate gotty credential format if provided
        gotty_credential = None
        enable_auth = None
        
        if args.gotty_credential:
            if ':' in args.gotty_credential and args.gotty_credential.count(':') == 1:
                parts = args.gotty_credential.split(':')
                if parts[0] and parts[1]:
                    gotty_credential = args.gotty_credential
                else:
                    print_main("Error: Both username and password are required for --gotty-credential.")
                    sys.exit(1)
            else:
                print_main("Error: Invalid format for --gotty-credential. Use 'username:password'.")
                sys.exit(1)
        elif args.credential:
            # --credential yes/no to use system credentials
            enable_auth = args.credential.lower() == 'yes'
        
        config = setup_terminal_service(config, data_dir, forced_terminal_service, args.port, credential=gotty_credential, enable_auth=enable_auth)
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
            # Determine distro_name
            distro_name = None
            distro_flags = [args.debian, args.alpine, args.arch, args.void]
            if sum(1 for flag in distro_flags if flag):
                if sum(distro_flags) > 1:
                    print_error("Error: Only one distribution flag (--debian, --alpine, --arch, --void) can be used at a time.")
                    sys.exit(1)
                if args.debian:
                    distro_name = 'Debian'
                elif args.alpine:
                    distro_name = 'Alpine'
                elif args.arch:
                    distro_name = 'Arch Linux'
                elif args.void:
                    distro_name = 'Void'
            # Determine enable_auth from --credential argument
            enable_auth = None
            if args.credential:
                enable_auth = args.credential.lower() == 'yes'
            config = auto_setup(pre_data_dir=custom_data_dir, force_gotty=args.gotty, force_sshx=args.sshx, force_native=args.native, force_port=args.port, enable_auth=enable_auth, distro_name=distro_name)
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
        # Determine enable_auth from --credential argument
        enable_auth = None
        if args.credential:
            enable_auth = args.credential.lower() == 'yes'
        config = prompt_setup(pre_data_dir=custom_data_dir, force_gotty=args.gotty, force_sshx=args.sshx, force_native=args.native, force_port=args.port, enable_auth=enable_auth)
        if custom_data_dir:
            config['data_dir'] = custom_data_dir
        setup_environment(config)
        save_config(config, data_dir)
        setup_proot_binary(data_dir, config['proot_bin'])
        print_main("Setup complete. Starting LCSX...")
        start_proot_shell(config)

if __name__ == "__main__":
    main()
