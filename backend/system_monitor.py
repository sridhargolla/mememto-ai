import os
from typing import Any

import psutil


class SystemMonitor:
    """Monitor system resources for performance tracking."""

    @staticmethod
    def get_memory_usage() -> dict[str, Any]:
        """
        Get current memory usage statistics.

        Returns:
            Dictionary with memory usage info
        """
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        return {
            "rss_mb": memory_info.rss / (1024 * 1024),  # Resident Set Size in MB
            "vms_mb": memory_info.vms / (1024 * 1024),  # Virtual Memory Size in MB
            "percent": process.memory_percent(),  # Memory percentage
            "available_mb": psutil.virtual_memory().available / (1024 * 1024),
            "total_mb": psutil.virtual_memory().total / (1024 * 1024),
        }

    @staticmethod
    def get_cpu_usage() -> dict[str, Any]:
        """
        Get current CPU usage statistics.

        Returns:
            Dictionary with CPU usage info
        """
        process = psutil.Process(os.getpid())

        return {
            "percent": process.cpu_percent(interval=0.1),
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
        }

    @staticmethod
    def get_disk_usage() -> dict[str, Any]:
        """
        Get disk usage statistics.

        Returns:
            Dictionary with disk usage info
        """
        disk = psutil.disk_usage(".")

        return {
            "total_gb": disk.total / (1024 * 1024 * 1024),
            "used_gb": disk.used / (1024 * 1024 * 1024),
            "free_gb": disk.free / (1024 * 1024 * 1024),
            "percent": disk.percent,
        }

    @staticmethod
    def get_system_info() -> dict[str, Any]:
        """
        Get comprehensive system information.

        Returns:
            Dictionary with all system metrics
        """
        return {
            "memory": SystemMonitor.get_memory_usage(),
            "cpu": SystemMonitor.get_cpu_usage(),
            "disk": SystemMonitor.get_disk_usage(),
        }
