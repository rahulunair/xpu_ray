import warnings

warnings.filterwarnings("ignore")  # ipex warning

import logging
from typing import Any, Dict

import psutil
import torch
import intel_extension_for_pytorch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemMonitor:
    """Utility class for monitoring system resources."""

    BYTES_PER_GB: int = 1024**3

    @classmethod
    def get_system_info(cls, device=0) -> Dict[str, Any]:
        """Get comprehensive system information."""
        info = {
            "cpu_usage": psutil.cpu_percent(),
            "available_memory": psutil.virtual_memory().available / cls.BYTES_PER_GB,
            "total_memory": psutil.virtual_memory().total / cls.BYTES_PER_GB,
        }

        try:
            if hasattr(torch.xpu, "get_device_properties"):
                device_props = torch.xpu.get_device_properties(device)
                total_vram = device_props.total_memory / cls.BYTES_PER_GB
                memory_stats = torch.xpu.memory_stats(device)
                used_vram = memory_stats.get("allocated_bytes", 0) / cls.BYTES_PER_GB
                free_vram = total_vram - used_vram
                info.update(
                    {
                        "total_vram": f"{total_vram:.2f}GB",
                        "available_vram": f"{free_vram:.2f}GB",
                        "vram_usage": f"{used_vram:.2f}GB",
                    }
                )
        except Exception as e:
            logger.warning(f"Could not get VRAM info: {e}")
        return info
