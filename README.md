# 🎨 XPU Ray Stable Diffusion Service

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


- **☁️ Cloud Deployment**:
  - For cloud deployments, explore Intel Tiber AI Cloud at [https://cloud.intel.com](https://cloud.intel.com) to try it out.
  
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

## Authentication Setup

Before making API calls, you need to set up authentication:

1. **Source the Token File**:
    ```bash
    source .auth_token.env
    ```

2. **Verify Token is Set**:
    ```bash
    echo $VALID_TOKEN
    ```

If you don't see a token:
- Run `./deploy.sh` to generate a new token
- The token will be saved in `.auth_token.env`
- Source the file again

**Note**: You need to source `.auth_token.env` in each new terminal session where you plan to make API calls.

## API Endpoints

### Generate Image
```bash
# Save to a file (e.g., output.png)
curl -X POST "http://localhost:9000/imagine/generate?prompt=a%20beautiful%20sunset%20over%20mountains" \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -o output.png

# Advanced usage with all parameters
curl -X POST "http://localhost:9000/imagine/generate?prompt=a%20beautiful%20sunset%20over%20mountains&img_size=1024&guidance_scale=7.5&num_inference_steps=20" \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -o generated_image.png
```

Parameters:
- `prompt` (required): Text description of the image to generate
- `img_size` (optional): Size of the output image (default varies by model)
- `guidance_scale` (optional): How closely to follow the prompt
- `num_inference_steps` (optional): Number of denoising steps

Returns: PNG image saved to the specified file

### Check Service Health
```bash
curl "http://localhost:9000/imagine/health" \
     -H "Authorization: Bearer $VALID_TOKEN"
```

Returns:
```json
{
    "status": "healthy"  // or "degraded"
}
```

### Get Model Information
```bash
curl "http://localhost:9000/imagine/info" \
     -H "Authorization: Bearer $VALID_TOKEN"
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
        "cpu_usage": "float",
        "memory_usage": "float",
        "available_memory": "float",
        "total_memory": "float"
    }
}
```

**Note**: 
- All endpoints require authentication using the `Authorization` header with a valid token
- The token is generated during deployment and can be found in `.auth_token.env`
- Source the token file before making requests: `source .auth_token.env`


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
## 🔒 Security Considerations

This service includes several features:
- Token-based authentication for all endpoints
- Rate limiting (both global and per-IP)
- Network isolation via Docker
- Resource limits and container security options

**Note on HTTPS**: 
- The default setup uses HTTP for simplicity in development/example environments
- For production deployments, it's strongly recommended to:
  1. Use a domain name with valid SSL/TLS certificates
  2. Configure Traefik with HTTPS
  3. Deploy behind a secure reverse proxy
  4. Implement additional security measures based on your requirements

**Current Security Features**:
- ✅ Authentication required for all endpoints
- ✅ Rate limiting: 10 requests/second per IP
- ✅ Global rate limiting: 10 requests/second
- ✅ Security headers for basic protection
- ✅ Container isolation and resource limits


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


