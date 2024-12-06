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