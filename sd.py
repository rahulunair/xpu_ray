import abc
import logging
from typing import Any, Dict, List, Optional

import intel_extension_for_pytorch as ipex
import torch
from diffusers import (
    EulerDiscreteScheduler,
    FluxPipeline,
    StableDiffusionPipeline,
    StableDiffusionXLPipeline,
    StableDiffusionXLImg2ImgPipeline,
    ControlNetModel,
    StableDiffusionControlNetPipeline,
    DiffusionPipeline,
    StableDiffusionLatentUpscalePipeline,
    UNet2DConditionModel,
)
from PIL import Image
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

logger = logging.getLogger(__name__)


class BaseModel(abc.ABC):
    @abc.abstractmethod
    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        pass

    @abc.abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        pass


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
        self.pipe.unet = ipex.optimize(self.pipe.unet.eval(), dtype=self.dtype)
        self.pipe.enable_attention_slicing()

    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        with torch.autocast(self.device):
            return self.pipe(
                prompt,
                height=height,
                width=width,
                num_inference_steps=kwargs.get("num_inference_steps", 30),
                guidance_scale=kwargs.get("guidance_scale", 7.5),
            ).images[0]

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
        self.pipe.unet = ipex.optimize(self.pipe.unet.eval(), dtype=self.dtype)
        self.pipe.enable_attention_slicing()

    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        with torch.autocast(self.device):
            return self.pipe(
                prompt,
                height=height,
                width=width,
                num_inference_steps=kwargs.get("num_inference_steps", 30),
                guidance_scale=kwargs.get("guidance_scale", 7.5),
            ).images[0]

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
        self.pipe.enable_model_cpu_offload()

    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        return self.pipe(
            prompt,
            guidance_scale=kwargs.get("guidance_scale", 0.0),
            num_inference_steps=kwargs.get("num_inference_steps", 4),
            max_sequence_length=kwargs.get("max_sequence_length", 256),
            generator=torch.Generator("cpu").manual_seed(kwargs.get("seed", 0)),
        ).images[0]

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
        self.pipe.unet = ipex.optimize(self.pipe.unet.eval(), dtype=self.dtype)
        self.pipe.enable_attention_slicing()

    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        with torch.autocast(self.device):
            return self.pipe(
                prompt,
                height=height,
                width=width,
                num_inference_steps=kwargs.get("num_inference_steps", 1),
                guidance_scale=kwargs.get("guidance_scale", 0.0),
            ).images[0]

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
        # Load the base SDXL UNet configuration
        unet = UNet2DConditionModel.from_config(
            self.base_model_id, 
            subfolder="unet"
        ).to(self.device, self.dtype)
        
        # Load the Lightning checkpoint
        unet.load_state_dict(
            load_file(
                hf_hub_download(self.repo, self.ckpt),
                device=self.device
            )
        )
        
        # Initialize the full pipeline with the custom UNet
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            self.base_model_id,
            unet=unet,
            torch_dtype=self.dtype
        ).to(self.device)
        
        # Use trailing timesteps as required by the model
        self.pipe.scheduler = EulerDiscreteScheduler.from_config(
            self.pipe.scheduler.config,
            timestep_spacing="trailing"
        )
        
        # Optimize for Intel XPU
        self.pipe.unet = ipex.optimize(self.pipe.unet.eval(), dtype=self.dtype)
        self.pipe.enable_attention_slicing()

    def generate(self, prompt: str, height: int, width: int, **kwargs) -> Image.Image:
        with torch.autocast(self.device):
            return self.pipe(
                prompt,
                height=height,
                width=width,
                num_inference_steps=kwargs.get("num_inference_steps", 4),
                guidance_scale=kwargs.get("guidance_scale", 0.0),
            ).images[0]

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
