# XPU Ray Stable Diffusion Service

A high-performance Stable Diffusion service powered by Intel XPU and Ray Serve, supporting multiple models with authentication and load balancing.

## Features

- **Multiple Model Support**:
  - Stable Diffusion 2.0 (SD2)
  - Stable Diffusion XL (SDXL)
  - SDXL-Turbo
  - SDXL-Lightning

- **Intel XPU Optimization**:
  - Optimized for Intel GPUs using Intel Extension for PyTorch
  - Efficient memory management
  - Hardware-accelerated inference

- **Production-Ready Features**:
  - Token-based authentication
  - Load balancing with Traefik
  - Health checks and monitoring
  - Automatic model management
  - Request queuing and rate limiting

## Prerequisites

- Docker and Docker Compose
- Intel GPU with appropriate drivers
- 32GB+ RAM recommended
- Ubuntu 22.04 or later

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/rahulunair/xpu_ray.git
cd xpu_ray
```

2. Deploy the service:
```bash
./deploy.sh
```
The script will:
- Generate an authentication token
- Start all services
- Wait for models to load
- Display the API endpoint and token

## API Endpoints

### Generate Image
```bash
curl -X POST "http://localhost:8000/imagine/sdxl-turbo" \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "a beautiful sunset over mountains",
       "img_size": 1024
     }'
```

### Check Service Health
```bash
curl http://localhost:8000/health
```

### Get Model Information
```bash
curl http://localhost:8000/info
```

### Reload Specific Model
```bash
curl -X POST "http://localhost:8000/reload_model/sdxl-turbo" \
     -H "Authorization: Bearer $VALID_TOKEN"
```

## Model Configurations

| Model | Steps | Guidance | Min Size | Max Size |
|-------|--------|-----------|-----------|-----------|
| SD2 | 50 | 7.5 | 512 | 768 |
| SDXL | 50 | 7.5 | 512 | 1024 |
| SDXL-Turbo | 1 | 0.0 | 512 | 1024 |
| SDXL-Lightning | 4 | 0.0 | 512 | 1024 |

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│   Client    │────▶│ Traefik  │────▶│    Auth     │
└─────────────┘     └──────────┘     └─────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Ray Serve   │
                  │ SD Service  │
                  └─────────────┘
```

## Management Commands

### Start Services
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### Clean Up
```bash
docker compose down --remove-orphans
docker rmi xpu_ray-sd-service xpu_ray-auth xpu_ray-traefik
```

### View Logs
```bash
docker compose logs -f
```

## Environment Variables

- `VALID_TOKEN`: Authentication token
- `DIFFUSERS_CACHE`: Cache directory for diffusers
- `HF_HOME`: Hugging Face home directory

## Performance Considerations

- Models are loaded on demand
- Memory is cleared after each generation
- Health checks monitor system resources
- Request queuing prevents overload

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Your License Here]

## Acknowledgments

- Intel Extension for PyTorch
- Hugging Face Diffusers
- Ray Project
- Stability AI