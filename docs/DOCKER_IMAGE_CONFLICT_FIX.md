# Docker Image Conflict Fix

## Problem
The error `failed to solve: image "docker.io/library/kidsmart-plus-api:latest": already exists` occurs when Docker tries to create multiple images with the same name.

## Root Cause
The original `docker-compose.yml` had multiple services (api, worker, dashboard, beat) all using `build: .`, which caused Docker Compose to create separate images for each service (kidsmart-plus-api, kidsmart-plus-worker, etc.), even though they all use the same Dockerfile.

## Solution Applied

### 1. Updated docker-compose.yml
Changed from multiple images to a single shared image:

**Before:**
```yaml
api:
  build: .
  ...
worker:
  build: .
  ...
dashboard:
  build: .
  ...
beat:
  build: .
  ...
```

**After:**
```yaml
api:
  build: .
  image: kidsmart-plus:latest
  ...
worker:
  image: kidsmart-plus:latest
  ...
dashboard:
  image: kidsmart-plus:latest
  ...
beat:
  image: kidsmart-plus:latest
  ...
```

Now only the `api` service builds the image, and all other services reuse it.

### 2. Removed obsolete version attribute
Removed `version: "3.9"` from docker-compose.yml as it's deprecated.

## How to Use

### Clean Start (Recommended)
```bash
# Remove everything and start fresh
docker compose down --rmi all --volumes
docker compose up --build -d
```

### Quick Rebuild
```bash
# Stop services
docker compose down

# Rebuild
docker compose build

# Start services
docker compose up -d
```

### Check Status
```bash
# View running containers
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
```

## Benefits

✓ **Single image** - Only one image built instead of 4 identical ones  
✓ **Faster builds** - Less disk space and build time  
✓ **No conflicts** - Prevents image name collision errors  
✓ **Efficient** - All services share the same base image  

## Troubleshooting

### If you still get image conflicts:

1. **Force remove all images:**
   ```bash
   docker compose down --rmi all
   docker system prune -a -f
   docker compose up --build
   ```

2. **Check for orphaned images:**
   ```bash
   docker images | grep kidsmart
   # Manually remove any orphaned images
   docker rmi <image-id> -f
   ```

3. **Clear build cache:**
   ```bash
   docker builder prune -f
   docker compose build --no-cache
   ```

## Verification

After successful build and start:

```bash
# Should show 5 running containers
docker compose ps

# Check API is healthy
curl http://localhost:8000/docs

# Check dashboard
# Open browser: http://localhost:8501
```

## Architecture

```
Single Docker Image: kidsmart-plus:latest
    ├── api (port 8000)
    ├── worker (celery worker)
    ├── dashboard (port 8501)
    └── beat (celery scheduler)
    
External Images:
    ├── postgres:15 (port 5432)
    └── redis:7 (port 6379)
```

All application services use the same image but run different commands.

