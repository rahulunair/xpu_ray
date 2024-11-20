import hashlib
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import RequestException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StableDiffusionClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)
        self.available_models = self._get_available_models()

    def _create_filename(self, prompt: str, model_name: str) -> str:
        """Create a filename from prompt using first few words and hash."""
        words = " ".join(prompt.split()[:5])
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{model_name}_{words}_{prompt_hash}_{timestamp}.png"
        return "".join(c if c.isalnum() or c in "._- " else "_" for c in filename)

    def _get_available_models(self) -> List[str]:
        """Get list of available models from server."""
        try:
            response = requests.get(f"{self.base_url}/info")
            response.raise_for_status()
            return response.json().get("available_models", [])
        except RequestException as e:
            logger.error(f"Failed to get available models: {e}")
            return []

    def check_health(self) -> Dict[str, Any]:
        """Check if the service is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Health check failed: {e}")
            raise

    def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        try:
            response = requests.get(f"{self.base_url}/info")
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to get server info: {e}")
            raise

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        try:
            response = requests.get(f"{self.base_url}/model_info/{model_name}")
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to get model info for {model_name}: {e}")
            raise

    def reload_model(self, model_name: str) -> Dict[str, Any]:
        """Request server to reload a specific model."""
        try:
            response = requests.post(f"{self.base_url}/reload_model/{model_name}")
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to reload model {model_name}: {e}")
            raise

    def generate_image(
        self,
        prompt: str,
        model_name: str = "sdxl",  # Default to SDXL
        img_size: int = 512,
        guidance_scale: Optional[float] = None,
        num_inference_steps: Optional[int] = None,
        fallback_models: Optional[List[str]] = None,
    ) -> str:
        """
        Generate an image from a prompt using specified model with fallback options.
        Returns the path to saved image.
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty")

        if model_name not in self.available_models:
            if not fallback_models:
                raise ValueError(
                    f"Model {model_name} is not available and no fallbacks specified"
                )
            logger.warning(
                f"Primary model {model_name} not available, trying fallbacks"
            )
            available_fallbacks = [
                m for m in fallback_models if m in self.available_models
            ]
            if not available_fallbacks:
                raise ValueError("No available models to generate image")
            model_name = available_fallbacks[0]
            logger.info(f"Using fallback model: {model_name}")

        params = {
            "prompt": prompt,
            "img_size": img_size,
        }
        if guidance_scale is not None:
            params["guidance_scale"] = guidance_scale
        if num_inference_steps is not None:
            params["num_inference_steps"] = num_inference_steps

        try:
            response = requests.post(
                f"{self.base_url}/imagine/{model_name}", params=params
            )
            response.raise_for_status()

            filename = self._create_filename(prompt, model_name)
            image_path = self.output_dir / filename

            with open(image_path, "wb") as f:
                f.write(response.content)

            return str(image_path)

        except RequestException as e:
            logger.error(f"Failed to generate image with {model_name}: {e}")
            if fallback_models:
                remaining_fallbacks = [m for m in fallback_models if m != model_name]
                if remaining_fallbacks:
                    logger.info(f"Attempting generation with fallback model")
                    return self.generate_image(
                        prompt=prompt,
                        model_name=remaining_fallbacks[0],
                        img_size=img_size,
                        guidance_scale=guidance_scale,
                        num_inference_steps=num_inference_steps,
                        fallback_models=remaining_fallbacks[1:],
                    )
            raise


def main():
    client = StableDiffusionClient()

    try:
        # Check service health
        health_status = client.check_health()
        logger.info(f"Service health status: {health_status}")

        # Get server information
        server_info = client.get_server_info()
        logger.info("Server Information:")
        logger.info(json.dumps(server_info, indent=2))

        # Test prompts for different scenarios
        test_scenarios = [
            {
                "category": "Landscapes",
                "prompts": [
                    "A serene mountain landscape with a crystal-clear lake at sunset, dramatic clouds",
                    "A dense tropical rainforest with rays of sunlight penetrating the canopy",
                ],
            },
            {
                "category": "Character Art",
                "prompts": [
                    "A detailed portrait of a cyberpunk samurai with glowing neon armor",
                    "An elegant elven queen in flowing silver robes surrounded by magical lights",
                ],
            },
            {
                "category": "Abstract Concepts",
                "prompts": [
                    "A surreal visualization of time and space warping around a black hole",
                    "The concept of artificial intelligence depicted as abstract geometric patterns",
                ],
            },
        ]

        model_configs = {
            "sdxl": {
                "img_size": 1024,
                "guidance_scale": 7.5,
                "num_inference_steps": 50,
                "fallbacks": ["sdxl_turbo", "sd2"],
            },
            "sdxl_turbo": {
                "img_size": 1024,
                "guidance_scale": 7.5,
                "num_inference_steps": 1,  # Turbo mode uses single step
                "fallbacks": ["sdxl", "sd2"],
            },
            "sd2": {
                "img_size": 768,
                "guidance_scale": 7.0,
                "num_inference_steps": 45,
                "fallbacks": ["sdxl", "sdxl_turbo"],
            },
            "kandinsky": {
                "img_size": 1024,
                "guidance_scale": 7.0,
                "num_inference_steps": 50,
                "fallbacks": ["sdxl", "sd2"],
            },
            "playground": {
                "img_size": 1024,
                "guidance_scale": 7.0,
                "num_inference_steps": 50,
                "fallbacks": ["sdxl", "sd2"],
            },
            # "flux": {
            #     "img_size": 512,
            #     "guidance_scale": 8.0,
            #     "num_inference_steps": 40,
            #     "fallbacks": ["sd2", "sdxl"],
            # },
        }

        # Test each model with each category of prompts
        for model_name, config in model_configs.items():
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing Model: {model_name.upper()}")
            logger.info(f"{'='*50}")

            # Get and display model info
            try:
                model_info = client.get_model_info(model_name)
                logger.info(f"Model Information for {model_name}:")
                logger.info(json.dumps(model_info, indent=2))
            except Exception as e:
                logger.error(f"Failed to get model info for {model_name}: {e}")

            for scenario in test_scenarios:
                logger.info(f"\nCategory: {scenario['category']}")

                for prompt in scenario["prompts"]:
                    logger.info(f"\nGenerating image for prompt: {prompt}")
                    start_time = time.time()

                    try:
                        image_path = client.generate_image(
                            prompt=prompt,
                            model_name=model_name,
                            img_size=config["img_size"],
                            guidance_scale=config["guidance_scale"],
                            num_inference_steps=config["num_inference_steps"],
                            fallback_models=config["fallbacks"],
                        )

                        generation_time = time.time() - start_time
                        logger.info(
                            f"Image generated successfully in {generation_time:.2f} seconds"
                        )
                        logger.info(f"Saved as: {image_path}")

                    except Exception as e:
                        logger.error(f"Failed to generate image for prompt: {prompt}")
                        logger.error(f"Error: {e}")
                        continue
                    time.sleep(1)
            try:
                logger.info(f"\nTesting model reload for {model_name}")
                reload_result = client.reload_model(model_name)
                logger.info(f"Model reload result: {reload_result}")
            except Exception as e:
                logger.error(f"Failed to reload model {model_name}: {e}")

            # Larger delay between model switches
            time.sleep(5)

    except Exception as e:
        logger.error(f"Service error: {e}")
        return


if __name__ == "__main__":
    main()
