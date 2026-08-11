"""
Core System & Hardware Monitoring Module.
Tracks RAM, CPU, and stream usage for 32-bit hardware.
Python 3.11.2 Compatible.
"""

import os
import psutil
from typing import Dict, Any

# Track active streaming connections
active_streams_count = 0


def increment_active_streams() -> None:
    global active_streams_count
    active_streams_count += 1


def decrement_active_streams() -> None:
    global active_streams_count
    active_streams_count = max(0, active_streams_count - 1)


def get_system_metrics(total_media_count: int) -> Dict[str, Any]:
    """Retrieve live CPU, RAM, and stream metrics."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    ram_mb = round(mem_info.rss / (1024 * 1024), 1)
    
    cpu_pct = round(process.cpu_percent(interval=0.0), 1)
    system_cpu = round(psutil.cpu_percent(interval=0.0), 1)
    virtual_mem = psutil.virtual_memory()

    return {
        "status": "online",
        "process_ram_mb": ram_mb,
        "process_cpu_pct": cpu_pct,
        "system_cpu_pct": system_cpu,
        "total_system_ram_mb": round(virtual_mem.total / (1024 * 1024), 0),
        "available_system_ram_mb": round(virtual_mem.available / (1024 * 1024), 0),
        "active_streams": active_streams_count,
        "total_media_count": total_media_count
    }
