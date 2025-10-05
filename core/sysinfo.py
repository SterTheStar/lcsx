"""
System information collection for LCSX.
Collects CPU, RAM, and disk information.
"""

import psutil
import os

def get_cpu_info():
    """Get CPU information."""
    return {
        'count': psutil.cpu_count(),
        'count_logical': psutil.cpu_count(logical=True),
        'freq': psutil.cpu_freq().current if psutil.cpu_freq() else None,
        'usage': psutil.cpu_percent(interval=1)
    }

def get_ram_info():
    """Get RAM information."""
    mem = psutil.virtual_memory()
    return {
        'total': mem.total,
        'available': mem.available,
        'used': mem.used,
        'percent': mem.percent
    }

def get_disk_info():
    """Get disk information."""
    disk = psutil.disk_usage('/')
    return {
        'total': disk.total,
        'used': disk.used,
        'free': disk.free,
        'percent': disk.percent
    }

def get_system_info():
    """Get all system information."""
    return {
        'cpu': get_cpu_info(),
        'ram': get_ram_info(),
        'disk': get_disk_info()
    }
