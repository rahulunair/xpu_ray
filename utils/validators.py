from typing import Dict, Any, Optional, Union
from fastapi import HTTPException

from config.model_configs import MODEL_CONFIGS

class GenerationValidator:
    """Validation utilities for image generation parameters."""
    
    MAX_PROMPT_LENGTH: int = 200
    MAX_GUIDANCE_SCALE: float = 10.0
    MAX_INFERENCE_STEPS: int = 50

    @classmethod
    def validate_prompt(cls, prompt: str) -> None:
        """Validate generation prompt."""
        if not prompt or not prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        if len(prompt) > cls.MAX_PROMPT_LENGTH:
            raise HTTPException(
                status_code=400, 
                detail=f"Prompt too long (max {cls.MAX_PROMPT_LENGTH} characters)"
            )

    @classmethod
    def validate_image_size(cls, model_name: str, img_size: Union[int, str]) -> None:
        """Validate image size is within model's allowed range."""
        config = MODEL_CONFIGS[model_name]
        
        try:
            img_size_int = int(img_size)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Image size must be an integer")

        if img_size_int < config["min_img_size"] or img_size_int > config["max_img_size"]:
            raise HTTPException(
                status_code=400,
                detail=f"Image size must be between {config['min_img_size']} and {config['max_img_size']}"
            )

    @classmethod
    def validate_generation_params(
        cls,
        model_name: str,
        guidance_scale: Optional[Union[float, int, str]],
        num_inference_steps: Optional[Union[int, str]]
    ) -> Dict[str, Any]:
        """Validate and prepare generation parameters."""
        config = MODEL_CONFIGS[model_name]
        
        if guidance_scale is not None:
            try:
                guidance_scale_float = float(guidance_scale)
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="Guidance scale must be a number")
            
            if guidance_scale_float < 0 or guidance_scale_float > cls.MAX_GUIDANCE_SCALE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Guidance scale must be between 0 and {cls.MAX_GUIDANCE_SCALE}"
                )
        else:
            guidance_scale_float = config["default_guidance"]
        
        if num_inference_steps is not None:
            try:
                steps_int = int(num_inference_steps)
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="Number of steps must be an integer")
            
            if steps_int < 1 or steps_int > cls.MAX_INFERENCE_STEPS:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Number of steps must be between 1 and {cls.MAX_INFERENCE_STEPS}"
                )
        else:
            steps_int = config["default_steps"]
        
        return {
            "guidance_scale": guidance_scale_float,
            "num_inference_steps": steps_int
        } 