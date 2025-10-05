#!/usr/bin/env python3
"""
LCSX - GUI CLI for Proot Automation
Main entry point for the LCSX tool.
"""

import os
import sys
from core.proot import run_proot_command, start_proot_shell
from core.setup import setup_environment
from ui.cli import prompt_setup
from ui.ascii import display_ascii
from config.config import load_config, save_config, is_configured

def main():
    # Display ASCII art
    display_ascii()

    # Check if configured
    if is_configured():
        config = load_config()
        print(f"Configuration found. Starting LCSX for user '{config['user']}' on '{config['hostname']}'...")
        start_proot_shell(config)
    else:
        print("No configuration found. Setting up LCSX...")
        config = prompt_setup()
        setup_environment(config)
        save_config(config)
        print("Setup complete. Starting LCSX...")
        start_proot_shell(config)

if __name__ == "__main__":
    main()
