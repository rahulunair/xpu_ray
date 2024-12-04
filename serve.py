import gc
import logging
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from typing import Any, Dict, Optional

import psutil
import ray
import torch
from fastapi import FastAPI, HTTPException, Response
from ray import serve

from sd import ModelFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

MODEL_CONFIGS = {
    "sd2": {
        "default_steps": 50,
        "default_guidance": 7.5,
        "min_img_size": 512,
        "max_img_size": 768,
    },
    "sdxl": {
        "default_steps": 50,
        "default_guidance": 7.5,
        "min_img_size": 512,
        "max_img_size": 1024,
    },
    "flux": {
        "default_steps": 4,
        "default_guidance": 0.0,
        "min_img_size": 256,
        "max_img_size": 1024,
    },
    "sdxl-turbo": {
        "default_steps": 1,
        "default_guidance": 0.0,
        "min_img_size": 512,
        "max_img_size": 1024,
    },
    "sdxl-lightning": {
        "default_steps": 4,
        "default_guidance": 0.0,
        "min_img_size": 512,
        "max_img_size": 1024,
    },
}


class ModelStatus:
    def __init__(self):
        self.is_loaded = False
        self.error = None
        self.model = None
        self.last_error_time = None

    def __str__(self):
        return f"Loaded: {self.is_loaded}, Error: {self.error}"


@serve.deployment(
    ray_actor_options={"num_cpus": 20},
    num_replicas=1,
    max_concurrent_queries=40,
    user_config={
        "max_batch_size": 1,
        "batch_wait_timeout_s": 0.1
    }
)
@serve.ingress(app)
class ImageGenerationServer:
    def __init__(self):
        logger.info("Initializing Image Generation Server")
        self.model_statuses = {
            model_name: ModelStatus() for model_name in MODEL_CONFIGS.keys()
        }
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._initialize_models()

    def _load_single_model(self, model_name: str) -> None:
        """Attempt to load a single model."""
        try:
            logger.info(f"Loading model: {model_name}")
            model = ModelFactory.create_model(model_name)
            self.model_statuses[model_name].model = model
            self.model_statuses[model_name].is_loaded = True
            self.model_statuses[model_name].error = None
            logger.info(f"Successfully loaded model: {model_name}")
        except Exception as e:
            error_msg = f"Failed to load model {model_name}: {str(e)}"
            logger.error(error_msg)
            self.model_statuses[model_name].is_loaded = False
            self.model_statuses[model_name].error = error_msg
            self.model_statuses[model_name].model = None

    def _initialize_models(self) -> None:
        """Initialize all models independently."""
        for model_name in self.model_statuses.keys():
            self._load_single_model(model_name)

    def _get_system_info(self) -> Dict[str, Any]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "available_memory": psutil.virtual_memory().available / (1024**3),
            "total_memory": psutil.virtual_memory().total / (1024**3),
        }

    @app.get("/info")
    def get_info(self) -> Dict[str, Any]:
        model_status = {
            name: {
                "is_loaded": status.is_loaded,
                "error": status.error,
                "config": MODEL_CONFIGS[name],
            }
            for name, status in self.model_statuses.items()
        }

        return {
            "available_models": [
                name for name, status in self.model_statuses.items() if status.is_loaded
            ],
            "model_status": model_status,
            "system_info": self._get_system_info(),
        }

    @app.post("/reload_model/{model_name}")
    def reload_model(self, model_name: str) -> Dict[str, Any]:
        if model_name not in self.model_statuses:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

        self._load_single_model(model_name)
        return {
            "model": model_name,
            "status": (
                "loaded" if self.model_statuses[model_name].is_loaded else "failed"
            ),
            "error": self.model_statuses[model_name].error,
        }

    @app.get("/model_info/{model_name}")
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        if model_name not in self.model_statuses:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

        status = self.model_statuses[model_name]
        if not status.is_loaded:
            return {
                "model": model_name,
                "status": "not_loaded",
                "error": status.error,
                "config": MODEL_CONFIGS[model_name],
            }

        return {
            "model": model_name,
            "status": "loaded",
            "info": status.model.get_model_info(),
            "config": MODEL_CONFIGS[model_name],
        }

    @app.post("/imagine/{model_name}")
    async def generate(
        self,
        model_name: str,
        prompt: str,
        img_size: int = 512,
        guidance_scale: Optional[float] = None,
        num_inference_steps: Optional[int] = None,
    ) -> Response:
        try:
            if model_name not in self.model_statuses:
                raise HTTPException(
                    status_code=404, detail=f"Model {model_name} not found"
                )
            config = MODEL_CONFIGS[model_name]
            if img_size < config["min_img_size"] or img_size > config["max_img_size"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image size must be between {config['min_img_size']} and {config['max_img_size']} for {model_name}",
                )

            status = self.model_statuses[model_name]
            if not status.is_loaded:
                self._load_single_model(model_name)
                if not status.is_loaded:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Model {model_name} is not available. Error: {status.error}",
                    )

            if not prompt:
                raise HTTPException(status_code=400, detail="Prompt cannot be empty")

            kwargs = {
                "guidance_scale": (
                    guidance_scale
                    if guidance_scale is not None
                    else config["default_guidance"]
                ),
                "num_inference_steps": (
                    num_inference_steps
                    if num_inference_steps is not None
                    else config["default_steps"]
                ),
            }

            try:
                image = status.model.generate(
                    prompt=prompt, height=img_size, width=img_size, **kwargs
                )
            except Exception as e:
                logger.error(f"Error generating with model {model_name}: {e}")
                status.is_loaded = False
                status.error = str(e)
                raise HTTPException(
                    status_code=500,
                    detail=f"Error generating image with model {model_name}: {str(e)}",
                )

            file_stream = BytesIO()
            image.save(file_stream, "PNG")

            gc.collect()
            torch.xpu.empty_cache()

            return Response(content=file_stream.getvalue(), media_type="image/png")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    def health_check(self) -> Dict[str, Any]:
        """Enhanced health check endpoint."""
        loaded_models = [
            name for name, status in self.model_statuses.items() if status.is_loaded
        ]
        is_healthy = len(loaded_models) > 0

        return {
            "status": "healthy" if is_healthy else "degraded",
            "loaded_models": loaded_models,
            "system_info": self._get_system_info(),
        }


entrypoint = ImageGenerationServer.bind()

def entrypoint(args):
    ray.init(
        address="auto",
        namespace="serve",
        runtime_env={
            "env_vars": {
                "RAY_SERVE_ENABLE_EXPERIMENTAL_STREAMING": "1"
            }
        }
    )
    serve.start(
        http_options={
            "host": "0.0.0.0",
            "port": 9002,
            "location": "EveryNode"
        },
        detached=True
    )
    ImageGenerationServer.deploy()
