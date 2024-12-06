# Stable Diffusion API Client Guide

Quick guide to interact with the Stable Diffusion service.

## Authentication

1. Deploy the service.
2. Get your API token from the `.auth_token.env` file created by `deploy.sh`

3. Use the token in all requests:
```bash
export SD_TOKEN="your-token-here"
```

## Quick Start

Generate an image:
```bash
curl -X POST http://your-server:9000/imagine/generate \
     -H "Authorization: Bearer $SD_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "a magical cosmic unicorn",
       "img_size": 1024,
       "guidance_scale": 0,
       "num_inference_steps": 4
     }' \
     --output image.png
```

## API Endpoints

- `POST /imagine/generate` - Generate images
- `GET /imagine/health` - Check service health
- `GET /imagine/info` - Get model information

## Usage Limits

- Rate limit: 15 requests per second per IP
- Burst limit: 30 requests
- Image size: 512-1024 pixels
- Response time: ~1-2 seconds per image

## Best Practices

1. Handle rate limits gracefully
2. Add timeouts to your requests
3. Validate image size requirements
4. Check service health before bulk requests

## Example Code

Python client:
```python
import requests

def generate_image(prompt, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": prompt,
        "img_size": 1024,
        "guidance_scale": 0,
        "num_inference_steps": 4
    }
    
    response = requests.post(
        "http://your-server:9000/imagine/generate",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        with open("image.png", "wb") as f:
            f.write(response.content)
        return True
    return False
```

## Support

Contact your service administrator for:
- API tokens
- Rate limit adjustments
- Service status updates
