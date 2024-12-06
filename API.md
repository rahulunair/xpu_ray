# API Documentation

## Base URL
`http://localhost:9000/imagine`

## Authentication
All endpoints require the `Authorization` header:
```bash
Authorization: Bearer <your-token>
```

## Endpoints

### 1. Generate Image
**Endpoint**: `POST /generate`

**Headers**:
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

**Request Body**:
```json
{
    "prompt": string,           // Required: Text description of the image
    "img_size": integer,        // Optional: Size of output image (512-1024)
    "guidance_scale": float,    // Optional: Guidance scale for generation
    "num_inference_steps": int  // Optional: Number of denoising steps
}
```

**Model-Specific Defaults**:
| Model          | Steps | Guidance | Min Size | Max Size |
|----------------|-------|----------|----------|----------|
| sdxl-lightning | 4     | 0.0      | 512      | 1024     |
| sdxl-turbo     | 1     | 0.0      | 512      | 1024     |
| sdxl           | 20    | 7.5      | 512      | 1024     |

**Response**:
- Content-Type: `image/png`
- Binary image data

**Example**:
```bash
curl -X POST "http://localhost:9000/imagine/generate" \
     -H "Authorization: Bearer $VALID_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "a beautiful sunset over mountains",
       "img_size": 1024,
       "guidance_scale": 0,
       "num_inference_steps": 4
     }' \
     --output image.png
```

### 2. Health Check
**Endpoint**: `GET /health`

**Headers**:
- `Authorization: Bearer <token>`

**Response**:
```json
{
    "status": string  // "healthy" or "degraded"
}
```

**Example**:
```bash
curl "http://localhost:9000/imagine/health" \
     -H "Authorization: Bearer $VALID_TOKEN"
```

### 3. Model Information
**Endpoint**: `GET /info`

**Headers**:
- `Authorization: Bearer <token>`

**Response**:
```json
{
    "model": string,          // Current model name
    "is_loaded": boolean,     // Model load status
    "error": string|null,     // Error message if any
    "config": {
        "default_steps": integer,
        "default_guidance": float,
        "min_img_size": integer,
        "max_img_size": integer,
        "default": boolean
    },
    "system_info": {
        "cpu_usage": float,           // CPU usage percentage
        "available_memory": float,     // Available RAM in GB
        "total_memory": float,         // Total RAM in GB
        "total_vram": string,          // Total GPU memory
        "available_vram": string,      // Available GPU memory
        "vram_usage": string          // Used GPU memory
    }
}
```

**Example**:
```bash
curl "http://localhost:9000/imagine/info" \
     -H "Authorization: Bearer $VALID_TOKEN"
```

## Error Responses

All endpoints may return the following errors:

### Authentication Errors
```json
{
    "detail": "Invalid token"
}
```
Status Code: 401

### Rate Limiting
```json
{
    "detail": "Rate limit exceeded"
}
```
Status Code: 429

### Service Errors
```json
{
    "detail": "Error message"
}
```
Status Code: 500

## Rate Limits
- Global: 10 requests/second
- Per IP: 10 requests/second
- Burst: 25 requests

## Notes
- Image generation can take several seconds depending on the model and parameters
- The service automatically manages memory and GPU resources
- All responses include CORS headers for browser compatibility 