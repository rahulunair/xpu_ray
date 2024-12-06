# Stable Diffusion API Client Guide

## Authentication

1. Deploy the service.
2. Get your API token from the `.auth_token.env` file created by `deploy.sh`
3. Set your token:
```bash
export VALID_TOKEN="your-token-here"
```

## Quick Start

Using the Python client:
```python
from client import StableDiffusionClient

client = StableDiffusionClient("http://your-server:9000/imagine")
image_path = client.generate_image(
    prompt="a magical cosmic unicorn",
    img_size=1024,
    guidance_scale=0.0,
    num_inference_steps=4
)
print(f"Image saved to: {image_path}")
```

Or using curl:
```bash
curl -X POST http://your-server:9000/imagine/generate \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "a magical cosmic unicorn",
       "img_size": 1024,
       "guidance_scale": 0.0,
       "num_inference_steps": 4
     }' \
     --output image.png
```

For more API examples and detailed documentation:
- See `examples.md` for more curl commands and usage patterns
- See `api.md` for complete API reference




