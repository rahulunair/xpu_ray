# Stable Diffusion API Examples

## Authentication
All requests require the authentication token in the header:
```bash
-H "Authorization: Bearer $VALID_TOKEN"
```

## SDXL Turbo (Fast Generation)
Optimized for single-step inference, best for quick generations.

```bash
# Quick Generation (1 step)
curl -X POST http://localhost:9000/imagine/generate \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
         "prompt": "a magical cosmic unicorn", 
         "img_size": 512,
         "guidance_scale": 0,
         "num_inference_steps": 1
     }' \
     --output turbo_quick.png

# Larger Resolution
curl -X POST http://localhost:9000/imagine/generate \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
         "prompt": "futuristic city skyline", 
         "img_size": 1024,
         "guidance_scale": 0,
         "num_inference_steps": 1
     }' \
     --output turbo_large.png
```

## SDXL Lightning (Fast with Better Quality)
Balanced between speed and quality, uses 4-step inference.

```bash
# Standard Generation
curl -X POST http://localhost:9000/imagine/generate \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
         "prompt": "a magical cosmic unicorn", 
         "img_size": 1024,
         "guidance_scale": 0,
         "num_inference_steps": 4
     }' \
     --output lightning_standard.png

# Artistic Style
curl -X POST http://localhost:9000/imagine/generate \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
         "prompt": "oil painting of a sunset over mountains", 
         "img_size": 1024,
         "guidance_scale": 0,
         "num_inference_steps": 4
     }' \
     --output lightning_art.png
```

## SDXL Base (Highest Quality)
Full SDXL model for highest quality outputs.

```bash
# High Quality Generation
curl -X POST http://localhost:9000/imagine/generate \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
         "prompt": "a magical cosmic unicorn", 
         "img_size": 1024,
         "guidance_scale": 7.5,
         "num_inference_steps": 25
     }' \
     --output sdxl_high_quality.png

# Detailed Art
curl -X POST http://localhost:9000/imagine/generate \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
         "prompt": "detailed oil painting of a medieval castle at sunset", 
         "img_size": 1024,
         "guidance_scale": 7.5,
         "num_inference_steps": 25
     }' \
     --output sdxl_detailed.png
```

## SD 2.1 Base
Alternative base model with different style characteristics.

```bash
# Standard Generation
curl -X POST http://localhost:9000/imagine/generate \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
         "prompt": "a magical cosmic unicorn", 
         "img_size": 768,
         "guidance_scale": 7.5,
         "num_inference_steps": 30
     }' \
     --output sd2_standard.png

# Artistic Style
curl -X POST http://localhost:9000/imagine/generate \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
         "prompt": "cyberpunk street scene at night", 
         "img_size": 768,
         "guidance_scale": 7.5,
         "num_inference_steps": 30
     }' \
     --output sd2_art.png
```

## Flux (Fast with Unique Style)
Optimized for speed while maintaining artistic quality.

```bash
# Standard Generation
curl -X POST http://localhost:9000/imagine/generate \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
         "prompt": "a magical cosmic unicorn", 
         "img_size": 512,
         "guidance_scale": 0,
         "num_inference_steps": 4
     }' \
     --output flux_standard.png

# Artistic Style
curl -X POST http://localhost:9000/imagine/generate \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
         "prompt": "vibrant digital art of a fantasy landscape", 
         "img_size": 1024,
         "guidance_scale": 0,
         "num_inference_steps": 4
     }' \
     --output flux_art.png
```

## Model Comparison
Each model has its strengths:
- **SDXL Turbo**: Fastest (1 step), good for rapid prototyping
- **SDXL Lightning**: Fast (4 steps) with better quality
- **SDXL Base**: Highest quality, slower (25+ steps)
- **SD 2.1**: Alternative style, good for specific use cases
- **Flux**: Fast (4 steps) with unique artistic style

## Tips
1. Use lower guidance scale (0-1) for fast models
2. Higher guidance (7.5) for base models
3. Adjust steps based on quality needs
4. Image size affects memory usage and generation time 