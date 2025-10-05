"""
Resolv.conf configuration for LCSX.
Handles setting DNS servers in the rootfs.
"""

import os
from lcsx.ui.logger import print_main

def set_resolv_conf(rootfs_path):
    """Set resolv.conf with custom DNS servers."""
    resolv_path = os.path.join(rootfs_path, 'etc', 'resolv.conf')
    content = """nameserver 8.8.8.8
nameserver 1.1.1.1
nameserver 9.9.9.9
options edns0
"""
    with open(resolv_path, 'w') as f:
        f.write(content)
    print_main("resolv.conf updated with custom DNS servers.")
