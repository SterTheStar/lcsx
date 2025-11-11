"""
Resolv.conf configuration for LCSX.
Handles setting DNS servers in the rootfs.
"""

import os
from lcsx.ui.logger import print_main
from lcsx.config.constants import DNS_SERVERS

def set_resolv_conf(rootfs_path):
    """Set resolv.conf with custom DNS servers."""
    resolv_path = os.path.join(rootfs_path, 'etc', 'resolv.conf')
    nameservers = '\n'.join(f'nameserver {dns}' for dns in DNS_SERVERS)
    content = f"""{nameservers}
options edns0
"""
    try:
        os.makedirs(os.path.dirname(resolv_path), exist_ok=True)
        with open(resolv_path, 'w') as f:
            f.write(content)
        print_main("resolv.conf updated with custom DNS servers.")
    except (OSError, PermissionError) as e:
        print_main(f"Warning: Could not update resolv.conf: {e}")
