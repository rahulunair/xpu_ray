import hashlib
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import requests
from requests.exceptions import RequestException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StableDiffusionClient:
    def __init__(self, base_url: str = "http://localhost:9000/imagine"):
        self.base_url = base_url.rstrip("/")
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)

    def _create_filename(self, prompt: str) -> str:
        """Create a filename from prompt using first few words and hash."""
        words = " ".join(prompt.split()[:5])
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{words}_{prompt_hash}_{timestamp}.png"
        return "".join(c if c.isalnum() or c in "._- " else "_" for c in filename)

    def check_health(self) -> Dict[str, Any]:
        """Check if the service is healthy."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                headers={"Authorization": f"Bearer {os.getenv('VALID_TOKEN')}"}
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Health check failed: {e}")
            raise

    def get_info(self) -> Dict[str, Any]:
        """Get server information."""
        try:
            response = requests.get(
                f"{self.base_url}/info",
                headers={"Authorization": f"Bearer {os.getenv('VALID_TOKEN')}"}
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to get server info: {e}")
            raise

    def generate_image(
        self,
        prompt: str,
        img_size: int = 512,
        guidance_scale: Optional[float] = None,
        num_inference_steps: Optional[int] = None,
    ) -> str:
        """Generate an image from a prompt."""
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                headers={"Authorization": f"Bearer {os.getenv('VALID_TOKEN')}"},
                json={
                    "prompt": prompt,
                    "img_size": img_size,
                    "guidance_scale": guidance_scale,
                    "num_inference_steps": num_inference_steps
                }
            )
            response.raise_for_status()
            filename = self._create_filename(prompt)
            image_path = self.output_dir / filename
            with open(image_path, "wb") as f:
                f.write(response.content)
            return str(image_path)
        except RequestException as e:
            logger.error(f"Failed to generate image: {e}")
            raise

def main():
    client = StableDiffusionClient()
    try:
        health = client.check_health()
        logger.info(f"Service health: {health}")
        info = client.get_info()
        logger.info(f"Service info: {info}")
        prompt = "A serene mountain landscape with a crystal-clear lake at sunset"
        logger.info(f"Generating image for prompt: {prompt}")
        image_path = client.generate_image(
            prompt=prompt,
            img_size=512,
            guidance_scale=0.0,
            num_inference_steps=4
        )
        logger.info(f"Image saved to: {image_path}")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
