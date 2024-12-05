import gc
import logging
import os
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Dict, Optional, Union

import ray.serve as serve
import torch
from fastapi import FastAPI, HTTPException, Response

from config.model_configs import MODEL_CONFIGS
from sd import ModelFactory
from utils.system_monitor import SystemMonitor
from utils.validators import GenerationValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@dataclass
class ModelStatus:
    """Status and metadata for the loaded model."""

    is_loaded: bool = False
    error: Optional[str] = None
    model: Optional[Any] = None

    def __str__(self) -> str:
        return f"Loaded: {self.is_loaded}, Error: {self.error}"


@serve.deployment(
    ray_actor_options={"num_cpus": 20},
    num_replicas=1,
    max_ongoing_requests=10,
    max_queued_requests=20,
)
@serve.ingress(app)
class ImageGenerationServer:
    """Server for handling image generation requests."""

    def __init__(self):
        """Initialize the image generation server with a single model."""
        logger.info("Initializing Image Generation Server")

        self.model_name = os.environ.get("DEFAULT_MODEL", "sdxl-lightning")
        logger.info(f"Using model: {self.model_name}")

        self.model_status = ModelStatus()
        self._load_model()

    def _load_model(self) -> None:
        """Load the configured model."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            model = ModelFactory.create_model(self.model_name)
            self.model_status.model = model
            self.model_status.is_loaded = True
            self.model_status.error = None
            logger.info(f"Successfully loaded model: {self.model_name}")
        except Exception as e:
            error_msg = f"Failed to load model {self.model_name}: {str(e)}"
            logger.error(error_msg)
            self.model_status.is_loaded = False
            self.model_status.error = error_msg
            self.model_status.model = None

    @app.get("/info")
    def get_info(self) -> Dict[str, Any]:
        """Get information about the model and system status."""
        return {
            "model": self.model_name,
            "is_loaded": self.model_status.is_loaded,
            "error": self.model_status.error,
            "config": MODEL_CONFIGS[self.model_name],
            "system_info": SystemMonitor.get_system_info(),
        }

    @app.get("/health")
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy" if self.model_status.is_loaded else "degraded",
        }

    @app.post("/generate")
    async def generate(
        self,
        prompt: str,
        img_size: Union[int, str] = 512,
        guidance_scale: Optional[Union[float, int, str]] = None,
        num_inference_steps: Optional[Union[int, str]] = None,
    ) -> Response:
        """Generate an image using the loaded model."""
        try:
            GenerationValidator.validate_prompt(prompt)
            GenerationValidator.validate_image_size(self.model_name, img_size)
            kwargs = GenerationValidator.validate_generation_params(
                self.model_name, guidance_scale, num_inference_steps
            )

            if not self.model_status.is_loaded:
                raise HTTPException(
                    status_code=503,
                    detail=f"Model is not available. Error: {self.model_status.error}",
                )

            try:
                image = self.model_status.model.generate(
                    prompt=prompt, height=img_size, width=img_size, **kwargs
                )
            except Exception as e:
                logger.error(f"Error generating image: {e}")
                self.model_status.is_loaded = False
                self.model_status.error = str(e)
                gc.collect()
                torch.xpu.empty_cache()
                raise HTTPException(
                    status_code=500, detail=f"Error generating image: {str(e)}"
                )

            file_stream = BytesIO()
            image.save(file_stream, "PNG")
            return Response(content=file_stream.getvalue(), media_type="image/png")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate: {e}")
            raise HTTPException(status_code=500, detail=str(e))


entrypoint = ImageGenerationServer.bind()
