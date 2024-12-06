# ⚡ XPU Ray Stable Diffusion Service



A high-performance Stable Diffusion service powered by Intel XPU and Ray Serve, supporting multiple models with authentication and load balancing.

<div align="center">
  <p>
    <img src="images/artist.png" width="250" alt="AI Artist" />
    <img src="images/nature.png" width="250" alt="Nature Meets Technology" />
    <img src="images/flow.png" width="250" alt="Data Flow" />
  </p>
  <p><i>Images generated using SDXL-Lightning model on Intel Max Series GPU VM 1100</i></p>
</div>

## ✨ Features

- Multiple Model Support:
  - Stable Diffusion 2.0 (SD2)
  - Stable Diffusion XL (SDXL)
  - SDXL-Turbo
  - SDXL-Lightning

- Intel XPU Optimization:
  - Optimized for Intel GPUs using Intel Extension for PyTorch
  - Efficient memory management
  - Hardware-accelerated inference

- Production-Ready Features:
  - Token-based authentication
  - Load balancing with Traefik
  - Health checks and monitoring
  - Automatic model management
  - Request queuing and rate limiting

- Cloud Deployment:
  - For cloud deployments, explore Intel Tiber AI Cloud at [https://cloud.intel.com](https://cloud.intel.com)

## Prerequisites

- Docker and Docker Compose
- Intel GPU with appropriate drivers
- 32GB+ RAM recommended
- Ubuntu 22.04 or later

## Model Selection

### Available Models
- sdxl-turbo (fastest, 1 step)
- sdxl-lightning (default, fast with better quality, 4 steps)
- sdxl (highest quality, 25 steps)
- sd2 (alternative style, 30 steps)
- flux (fast artistic, 4 steps)

### Choosing a Model
```bash
# Deploy with specific model
./deploy.sh <model-name>

# Examples:
./deploy.sh sdxl-turbo    # For fastest generation (1 step)
./deploy.sh sdxl-lightning # For fast generation with better quality (4 steps)
./deploy.sh sdxl          # For highest quality (25 steps)
./deploy.sh sd2           # For SD 2.1 base model (30 steps)
```

### Switching Models
To switch models without restarting base services:
```bash
./deploy.sh <model-name> --skip-base
```

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
- Wait for model to load
- Display the API endpoint and token

## Authentication Setup

1. Source the token file:
```bash
source .auth_token.env
```

2. Verify token is set:
```bash
echo $VALID_TOKEN
```

See `./examples.md` for detailed API usage examples.

## API Overview

Main endpoints:
- `/imagine/generate` - Generate images
- `/imagine/health` - Check service health
- `/imagine/info` - Get model information

See `./api.md` for complete API documentation.

## Model Configurations

| Model          | Steps | Guidance | Min Size | Max Size |
|----------------|-------|----------|----------|----------|
| SDXL-Turbo     | 1     | 0.0      | 512      | 1024     |
| SDXL-Lightning | 4     | 0.0      | 512      | 1024     |
| SDXL           | 25    | 7.5      | 512      | 1024     |
| SD2            | 30    | 7.5      | 512      | 768      |
| Flux           | 4     | 0.0      | 256      | 1024     |

## Management Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f
```

## Security & Performance

- Token-based authentication
- Rate limiting and request queuing
- Model caching
- Optimized for Intel GPUs

## Model Cache

Models are cached in `${HOME}/.cache/huggingface` to improve load times and reduce bandwidth usage.

## Acknowledgments

Built with Intel Extension for PyTorch, Hugging Face Diffusers, and Ray Project


