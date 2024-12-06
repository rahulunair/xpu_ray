# Stable Diffusion Service Benchmarks

### Running Benchmarks

1. Install wrk:
```bash
sudo apt-get install wrk
```

## Prerequisites

1. Ensure the service is running:
```bash
# Start with default model (SDXL Lightning) with auth and traefik services
./deploy.sh

# Or start specific model (skip-base assumes that auth and traefik services are up)
./deploy.sh sdxl-lightning --skip-base
```

2. Verify service is healthy:
```bash
curl -H "Authorization: Bearer $VALID_TOKEN" http://localhost:9000/imagine/health
```

## Running Tests

1. Install wrk:
```bash
sudo apt-get install wrk
```

2. Run stress test:
```bash
cd benchmarks
./scripts/stress_test.sh
```

3. Results will be saved in `results/` directory

## Available Tests

### Stress Test
Tests service performance under increasing load:
```bash
./scripts/stress_test.sh
```

Parameters:
- Connections: 4, 8, 16, 32, 64
- Duration: 30s per test
- Threads: Scales with connections

### Test Configuration
Edit `scripts/test.lua` to modify:
- Image size
- Steps
- Guidance scale
- Prompt


## Sample Results

Load testing results using SDXL-Lightning model (Bfloat16) on Intel Max GPU 1100 VM :

| Connections | Threads | Req/sec | Latency (avg) | Transfer/sec |
|------------|---------|---------|---------------|--------------|
| 4          | 1       | 1.20    | -             | 447.31 KB   |
| 8          | 2       | 1.43    | 1.28s         | 538.21 KB   |
| 16         | 4       | 1.50    | 1.28s         | 572.94 KB   |
| 32         | 8       | 1.40    | 1.39s         | 540.70 KB   |
| 64         | 16      | 1.46    | 1.46s         | 549.71 KB   |

###  Analysis

These results show typical performance for Stable Diffusion models:
- ~1-2 images per second with SDXL-Lightning (4 steps)
- Zero failed requests across all loads
- Optimal performance at 16 concurrent connections
- Consistent throughput under increasing load