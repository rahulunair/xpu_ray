# 🎨 XPU Ray Stable Diffusion Service

A high-performance Stable Diffusion service powered by Intel XPU and Ray Serve, supporting multiple models with authentication and load balancing.

## ✨ Features

- **🖼️ Multiple Model Support**:
  - Stable Diffusion 2.0 (SD2)
  - Stable Diffusion XL (SDXL)
  - SDXL-Turbo
  - SDXL-Lightning

- **⚡ Intel XPU Optimization**:
  - Optimized for Intel GPUs using Intel Extension for PyTorch
  - Efficient memory management
  - Hardware-accelerated inference

- **🚀 Production-Ready Features**:
  - 🔐 Token-based authentication
  - ⚖️ Load balancing with Traefik
  - 🏥 Health checks and monitoring
  - 🤖 Automatic model management
  - 📊 Request queuing and rate limiting

## 📋 Prerequisites

- 🐳 Docker and Docker Compose
- 🎮 Intel GPU with appropriate drivers
- 💾 32GB+ RAM recommended
- 🐧 Ubuntu 22.04 or later

## 🚀 Quick Start

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
- 🔑 Generate an authentication token
- 🚀 Start all services
- ⏳ Wait for model to load
- 📝 Display the API endpoint and token

## 🔌 API Endpoints

### 🎨 Generate Image
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "a beautiful sunset over mountains",
       "img_size": 1024,
       "guidance_scale": 7.5,
       "num_inference_steps": 20
     }'
```
Returns: PNG image

### 💓 Check Service Health
```bash
curl http://localhost:8000/health
```
Returns:
```json
{
    "status": "healthy"  // or "degraded"
}
```

### ℹ️ Get Model Information
```bash
curl http://localhost:8000/info
```
Returns:
```json
{
    "model": "string",
    "is_loaded": true,
    "error": null,
    "config": {
        "default_steps": "int",
        "default_guidance": "float",
        "min_img_size": "int",
        "max_img_size": "int",
        "default": "bool"
    },
    "system_info": {
        "memory_used": "float",
        "memory_total": "float",
        "memory_percent": "float",
        "cpu_percent": "float"
    }
}
```

## ⚙️ Model Configurations

| Model          | Steps | Guidance | Min Size | Max Size |
|----------------|-------|----------|----------|----------|
| SD2            | 50    | 7.5      | 512      | 768      |
| SDXL           | 20    | 7.5      | 512      | 1024     |
| Flux           | 4     | 0.0      | 256      | 1024     |
| SDXL-Turbo     | 1     | 0.0      | 512      | 1024     |
| SDXL-Lightning | 4     | 0.0      | 512      | 1024     |

## 🏗️ Architecture

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

## 🛠️ Management Commands

### 🚀 Start Services
```bash
docker compose up -d
```

### 🛑 Stop Services
```bash
docker compose down
```

### 🧹 Clean Up
```bash
docker compose down --remove-orphans
docker rmi xpu_ray-sd-service xpu_ray-auth xpu_ray-traefik
```

### 📋 View Logs
```bash
docker compose logs -f
```

## 🔧 Environment Variables

- `VALID_TOKEN`: Authentication token
- `DIFFUSERS_CACHE`: Cache directory for diffusers
- `HF_HOME`: Hugging Face home directory
- `DEFAULT_MODEL`: Model to load at startup (default: 'sdxl-lightning')

## 📈 Performance Considerations

- 🔄 Models are loaded on demand
- 🧹 Memory is cleared after each generation
- 💓 Health checks monitor system resources
- 📊 Request queuing prevents overload

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## 📦 Caching

The service caches Hugging Face model weights in `${HOME}/.cache/huggingface` to:
- Improve load times
- Reduce bandwidth usage
- Persist between restarts

**Note**: To use custom models, please upload them to the Hugging Face Hub and update the model configuration accordingly.

**License Disclaimer**: The models used in this service are provided by third parties and are subject to their respective licenses. Users are responsible for ensuring compliance with these licenses when using the models. Please refer to the model documentation on the Hugging Face Hub for specific licensing information.

## 🙏 Acknowledgments

- Intel Extension for PyTorch
- Hugging Face Diffusers
- Ray Project

