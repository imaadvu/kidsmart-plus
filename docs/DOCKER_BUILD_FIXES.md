# Docker Build Timeout Solutions

## Problem
Docker build fails when downloading large packages (especially `playwright` at 38.1 MB) due to network timeouts.

## Solutions Implemented

### Solution 1: Optimized Dockerfile (Current)
The main `Dockerfile` has been updated with:
- Increased pip timeout to 1000 seconds
- Added retry logic (5 retries)
- Split requirements into 3 files for better caching and isolation:
  - `requirements-base.txt` - Core dependencies
  - `requirements-ml.txt` - Data science packages
  - `requirements-playwright.txt` - Playwright only
- Upgraded pip before installing packages
- Added environment variables for pip optimization

**Usage:**
```bash
docker compose up --build
```

### Solution 2: Alternative Multi-Stage Build
If Solution 1 still times out, use `Dockerfile.alternative`:
- Uses multi-stage builds to reduce final image size
- Even longer timeouts (2000 seconds)
- Automatic retry with sleep delays
- Virtual environment isolation

**Usage:**
```bash
# Temporarily rename files
mv Dockerfile Dockerfile.backup
mv Dockerfile.alternative Dockerfile
docker compose up --build
# Restore if needed
mv Dockerfile.backup Dockerfile
```

### Solution 3: Build Without Playwright (Quick Start)
If you don't need Playwright immediately:

1. Comment out playwright in `requirements-playwright.txt`:
```txt
# playwright==1.47.0
```

2. Set in `.env`:
```
ENABLE_PLAYWRIGHT=false
```

3. Build and run:
```bash
docker compose up --build
```

4. Install playwright later inside the running container:
```bash
docker compose exec api pip install playwright==1.47.0
docker compose exec api python -m playwright install chromium
```

### Solution 4: Pre-download Wheels Locally
Download large packages locally first, then copy to container:

```bash
# On your host machine
pip download playwright==1.47.0 -d ./wheels
pip download numpy==2.1.2 -d ./wheels
pip download pandas==2.2.3 -d ./wheels
```

Then modify Dockerfile:
```dockerfile
COPY wheels/ /tmp/wheels/
RUN pip install --no-index --find-links=/tmp/wheels -r requirements.txt
```

### Solution 5: Use Docker BuildKit with Caching
Enable BuildKit for better caching:

```bash
# Windows PowerShell
$env:DOCKER_BUILDKIT=1
docker compose build

# Or in docker-compose.yml, add:
# export DOCKER_BUILDKIT=1
```

### Solution 6: Use Alternative PyPI Mirror
If PyPI is slow, use a faster mirror. Add to Dockerfile before pip install:

```dockerfile
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# or
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

### Solution 7: Increase Docker Daemon Timeout
Edit Docker Desktop settings:
1. Open Docker Desktop
2. Settings → Docker Engine
3. Add/modify:
```json
{
  "max-download-attempts": 5,
  "registry-mirrors": []
}
```

## Recommended Approach

1. **First try**: Use the current optimized `Dockerfile` (Solution 1)
2. **If timeout persists**: Use `Dockerfile.alternative` (Solution 2)
3. **For quick testing**: Temporarily disable playwright (Solution 3)
4. **For slow networks**: Pre-download wheels (Solution 4) or use mirror (Solution 6)

## Verification

After successful build, verify all packages:
```bash
docker compose exec api pip list | grep -E "playwright|streamlit|pandas|numpy"
```

## Network Tips

- Check your internet connection stability
- Temporarily disable VPN if using one
- Try building during off-peak hours
- Consider using ethernet instead of WiFi for stability
- Check if firewall/antivirus is interfering with Docker

