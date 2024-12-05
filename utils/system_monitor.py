import logging
from typing import Any, Dict

import psutil
import torch

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Utility class for monitoring system resources."""

    BYTES_PER_GB: int = 1024**3

    @classmethod
    def get_system_info(cls) -> Dict[str, Any]:
        """Get comprehensive system information."""
        info = {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "available_memory": psutil.virtual_memory().available / cls.BYTES_PER_GB,
            "total_memory": psutil.virtual_memory().total / cls.BYTES_PER_GB,
        }

        try:
            if hasattr(torch.xpu, "get_device_properties"):
                total_vram = (
                    torch.xpu.get_device_properties(0).total_memory / cls.BYTES_PER_GB
                )
                free_vram = (
                    torch.xpu.get_device_properties(0).free_memory / cls.BYTES_PER_GB
                )
                info.update(
                    {
                        "total_vram": f"{total_vram:.2f}GB",
                        "available_vram": f"{free_vram:.2f}GB",
                        "vram_usage": f"{(total_vram - free_vram):.2f}GB",
                    }
                )
        except Exception as e:
            logger.warning(f"Could not get VRAM info: {e}")
        return info
