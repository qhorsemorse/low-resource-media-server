"""
Core System & Hardware Monitoring Module.
Tracks RAM, CPU, and stream usage for 32-bit hardware.
Python 3.11.2 Compatible.
Gracefully handles missing psutil library using pure Python /proc fallback.
"""

import os
from typing import Dict, Any

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Track active streaming connections
active_streams_count = 0


def increment_active_streams() -> None:
    global active_streams_count
    active_streams_count += 1


def decrement_active_streams() -> None:
    global active_streams_count
    active_streams_count = max(0, active_streams_count - 1)


def _get_ram_from_resource() -> float:
    """Fallback RAM usage calculation using Python built-in resource module."""
    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF)
        # ru_maxrss is in kilobytes on Linux
        return round(usage.ru_maxrss / 1024.0, 1)
    except Exception:
        return 0.0


def _get_proc_meminfo() -> tuple[float, float]:
    """Fallback system RAM calculation by reading Linux /proc/meminfo."""
    try:
        total_kb = 0.0
        avail_kb = 0.0
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    total_kb = float(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    avail_kb = float(line.split()[1])
        return round(total_kb / 1024.0, 0), round(avail_kb / 1024.0, 0)
    except Exception:
        return 0.0, 0.0


def get_system_metrics(total_media_count: int) -> Dict[str, Any]:
    """Retrieve live CPU, RAM, and stream metrics with optional psutil."""
    if HAS_PSUTIL:
        try:
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            ram_mb = round(mem_info.rss / (1024 * 1024), 1)
            cpu_pct = round(process.cpu_percent(interval=0.0), 1)
            system_cpu = round(psutil.cpu_percent(interval=0.0), 1)
            virtual_mem = psutil.virtual_memory()
            total_ram = round(virtual_mem.total / (1024 * 1024), 0)
            avail_ram = round(virtual_mem.available / (1024 * 1024), 0)
        except Exception:
            ram_mb = _get_ram_from_resource()
            total_ram, avail_ram = _get_proc_meminfo()
            cpu_pct, system_cpu = 0.0, 0.0
    else:
        ram_mb = _get_ram_from_resource()
        total_ram, avail_ram = _get_proc_meminfo()
        cpu_pct, system_cpu = 0.0, 0.0

    return {
        "status": "online",
        "process_ram_mb": ram_mb,
        "process_cpu_pct": cpu_pct,
        "system_cpu_pct": system_cpu,
        "total_system_ram_mb": total_ram,
        "available_system_ram_mb": avail_ram,
        "active_streams": active_streams_count,
        "total_media_count": total_media_count
    }
