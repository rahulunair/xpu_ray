import warnings
warnings.filterwarnings("ignore")  # supress ipex warnings

import logging
from typing import Any, Dict

import torch
import intel_extension_for_pytorch as ipex
from diffusers import (
    EulerDiscreteScheduler,
    FluxPipeline,
    StableDiffusionPipeline,
    StableDiffusionXLPipeline,
    DiffusionPipeline,
    UNet2DConditionModel,
)
from PIL import Image
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

def optimize_unet(unet):
    """Optimize UNet with IPEX"""
    try:
        logger.info("Optimizing UNet with IPEX")
        unet = ipex.optimize(unet.eval(), dtype=unet.dtype)
        logger.info("Successfully optimized UNet with IPEX")
        return unet
    except Exception as e:
        logger.warning(f"IPEX optimization failed: {e}, continuing without optimization")
        return unet

def perform_inference(pipe, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
    """Perform inference with optimized settings."""
    try:
        with torch.inference_mode(), torch.xpu.amp.autocast():
            return pipe(
                prompt,
                height=height,
                width=width,
                **kwargs
            ).images[0]
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        raise
    finally:
        if hasattr(torch.xpu, 'empty_cache'):
            torch.xpu.empty_cache()

def optimize_model_recursive(model):
    """Recursively optimize all torch.nn.Module components with IPEX"""
    try:
        if isinstance(model, torch.nn.Module):
            logger.info(f"Optimizing module: {type(model).__name__}")
            return ipex.optimize(model.eval(), dtype=model.dtype)
        if hasattr(model, '__dict__'):
            for name, component in model.__dict__.items():
                if isinstance(component, (torch.nn.Module, object)): 
                    try:
                        optimized = optimize_model_recursive(component)
                        setattr(model, name, optimized)
                    except Exception as e:
                        logger.warning(f"Failed to optimize {name}: {e}")

        return model
    except Exception as e:
        logger.warning(f"Optimization failed: {e}, continuing without optimization")
        return model

class BaseModel:
    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        raise NotImplementedError

    def get_model_info(self) -> Dict[str, Any]:
        raise NotImplementedError

class StableDiffusion2Model(BaseModel):
    def __init__(self, device: str = "xpu", dtype: torch.dtype = torch.bfloat16):
        self.model_id = "stabilityai/stable-diffusion-2"
        self.device = device
        self.dtype = dtype
        self._initialize_model()

    def _initialize_model(self):
        scheduler = EulerDiscreteScheduler.from_pretrained(
            self.model_id, subfolder="scheduler"
        )
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id, scheduler=scheduler, torch_dtype=self.dtype
        )
        self.pipe = self.pipe.to(self.device)
        self.pipe.unet = optimize_unet(self.pipe.unet)
        self.pipe.enable_attention_slicing()
        logger.info(f"Initialized {self.model_id} with device={self.device}, dtype={self.dtype}")

    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        return perform_inference(
            self.pipe,
            prompt,
            height,
            width,
            num_inference_steps=kwargs.get("num_inference_steps", 30),
            guidance_scale=kwargs.get("guidance_scale", 7.5)
        )

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_type": "Stable Diffusion 2",
            "device": self.device,
            "dtype": str(self.dtype),
        }

class StableDiffusionXLModel(BaseModel):
    def __init__(self, device: str = "xpu", dtype: torch.dtype = torch.bfloat16):
        self.model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        self.device = device
        self.dtype = dtype
        self._initialize_model()

    def _initialize_model(self):
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            self.model_id, torch_dtype=self.dtype
        )
        self.pipe = self.pipe.to(self.device)
        self.pipe.unet = optimize_unet(self.pipe.unet)
        self.pipe.enable_attention_slicing()
        logger.info(f"Initialized {self.model_id} with device={self.device}, dtype={self.dtype}")

    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        return perform_inference(
            self.pipe,
            prompt,
            height,
            width,
            num_inference_steps=kwargs.get("num_inference_steps", 30),
            guidance_scale=kwargs.get("guidance_scale", 7.5)
        )

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_type": "Stable Diffusion XL",
            "device": self.device,
            "dtype": str(self.dtype),
        }

class FluxModel(BaseModel):
    def __init__(self, device: str = "xpu", dtype: torch.dtype = torch.bfloat16):
        self.model_id = "black-forest-labs/FLUX.1-schnell"
        self.device = device
        self.dtype = dtype
        self._initialize_model()

    def _initialize_model(self):
        self.pipe = FluxPipeline.from_pretrained(self.model_id, torch_dtype=self.dtype)
        self.pipe = self.pipe.to(self.device)
        self.pipe = optimize_model_recursive(self.pipe)
        self.pipe.enable_attention_slicing()
        logger.info(f"Initialized {self.model_id} with device={self.device}, dtype={self.dtype}")

    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        return perform_inference(
            self.pipe,
            prompt,
            height,
            width,
            guidance_scale=kwargs.get("guidance_scale", 0.0),
            num_inference_steps=kwargs.get("num_inference_steps", 4),
            max_sequence_length=kwargs.get("max_sequence_length", 256),
        )

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_type": "FLUX",
            "device": self.device,
            "dtype": str(self.dtype),
        }

class SDXLTurboModel(BaseModel):
    def __init__(self, device: str = "xpu", dtype: torch.dtype = torch.bfloat16):
        self.model_id = "stabilityai/sdxl-turbo"
        self.device = device
        self.dtype = dtype
        self._initialize_model()

    def _initialize_model(self):
        self.pipe = DiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=self.dtype
        )
        self.pipe = self.pipe.to(self.device)
        self.pipe.unet = optimize_unet(self.pipe.unet)
        self.pipe.enable_attention_slicing()
        logger.info(f"Initialized {self.model_id} with device={self.device}, dtype={self.dtype}")

    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        return perform_inference(
            self.pipe,
            prompt,
            height,
            width,
            num_inference_steps=kwargs.get("num_inference_steps", 1),
            guidance_scale=kwargs.get("guidance_scale", 0.0),
        )

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_type": "SDXL Turbo",
            "device": self.device,
            "dtype": str(self.dtype),
        }

class SDXLLightningModel(BaseModel):
    def __init__(self, device: str = "xpu", dtype: torch.dtype = torch.bfloat16):
        self.base_model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        self.repo = "ByteDance/SDXL-Lightning"
        self.ckpt = "sdxl_lightning_4step_unet.safetensors"
        self.device = device
        self.dtype = dtype
        self._initialize_model()

    def _initialize_model(self):
        unet = UNet2DConditionModel.from_config(
            self.base_model_id,
            subfolder="unet"
        ).to(self.device, self.dtype)

        unet.load_state_dict(
            load_file(
                hf_hub_download(self.repo, self.ckpt),
                device=self.device
            )
        )
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            self.base_model_id,
            unet=unet,
            torch_dtype=self.dtype
        ).to(self.device)

        self.pipe.scheduler = EulerDiscreteScheduler.from_config(
            self.pipe.scheduler.config,
            timestep_spacing="trailing"
        )
        self.pipe.unet = optimize_unet(self.pipe.unet)
        self.pipe.enable_attention_slicing()
        logger.info(f"Initialized {self.repo} with device={self.device}, dtype={self.dtype}")

    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        return perform_inference(
            self.pipe,
            prompt,
            height,
            width,
            num_inference_steps=kwargs.get("num_inference_steps", 4),
            guidance_scale=kwargs.get("guidance_scale", 0.0),
        )

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_id": self.repo,
            "base_model": self.base_model_id,
            "checkpoint": self.ckpt,
            "model_type": "SDXL Lightning",
            "device": self.device,
            "dtype": str(self.dtype),
        }

class ModelFactory:
    @staticmethod
    def create_model(model_type: str, **kwargs) -> BaseModel:
        models = {
            "sd2": StableDiffusion2Model,
            "sdxl": StableDiffusionXLModel,
            "flux": FluxModel,
            "sdxl-turbo": SDXLTurboModel,
            "sdxl-lightning": SDXLLightningModel,
        }
        if model_type not in models:
            raise ValueError(f"Unknown model type: {model_type}")
        return models[model_type](**kwargs)