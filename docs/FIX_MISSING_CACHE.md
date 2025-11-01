# 🚨 EMERGENCY FIX - api/cache.py Missing in Docker Container

## Problem
Your logs show:
```
Created admin user from env  ✓ (This worked!)
ModuleNotFoundError: No module named 'api.cache'  ✗ (This is the issue)
```

## Root Cause
The `api/cache.py` file **exists locally** but is **NOT in the Docker container** on your AWS server.

This happens when:
1. The file wasn't uploaded to AWS server
2. The Docker image was built before the file existed
3. The file is somehow being excluded during build

## 🔍 Verify the Problem

SSH into your AWS server and run:

```bash
# Check if file exists on the server filesystem
ls -la api/cache.py

# Check if file exists in the running container
docker compose exec api ls -la /app/api/cache.py

# If the second command fails, the file is missing from the Docker image
```

## ✅ Solution 1: Ensure File is Uploaded to AWS

### Step 1: Verify Locally (on your Windows machine)
```cmd
dir api\cache.py
```

You should see the file. If not, something is seriously wrong.

### Step 2: Upload to AWS Server

**Using SCP (from Windows):**
```cmd
scp api\cache.py user@your-aws-server:/path/to/kidsmart-plus/api/cache.py
```

**Using rsync:**
```bash
rsync -avz api/cache.py user@your-aws-server:/path/to/kidsmart-plus/api/
```

**Or upload the entire api folder:**
```cmd
scp -r api user@your-aws-server:/path/to/kidsmart-plus/
```

### Step 3: Verify File is on AWS Server
```bash
# SSH into AWS
ssh user@your-aws-server

# Navigate to project
cd /path/to/kidsmart-plus

# Check file exists
ls -la api/cache.py
cat api/cache.py  # Should show the cache module code
```

## ✅ Solution 2: Rebuild Docker Image

Once the file is on the server, rebuild the Docker image:

```bash
# Stop containers
docker compose down

# Remove old images (important!)
docker compose down --rmi all

# Clear build cache
docker builder prune -f

# Build fresh image (this will now include api/cache.py)
docker compose build --no-cache

# Start services
docker compose up -d

# Watch logs
docker compose logs -f api
```

## ✅ Solution 3: Manual Verification During Build

The updated Dockerfile now includes verification. If the build fails with:
```
ERROR: api/cache.py is missing!
```

Then the file is definitely not on your AWS server filesystem.

## 🎯 Quick Fix Command Sequence

Copy-paste this entire sequence on your AWS server:

```bash
# 1. Verify file exists
if [ ! -f api/cache.py ]; then
    echo "ERROR: api/cache.py is missing from server filesystem!"
    echo "You need to upload this file from your local machine."
    exit 1
fi

# 2. Show the file to confirm it's correct
echo "File found. Contents:"
head -n 20 api/cache.py

# 3. Stop and remove everything
docker compose down --rmi all --volumes

# 4. Clear Docker cache
docker builder prune -f

# 5. Build fresh
docker compose build --no-cache

# 6. Start services
docker compose up -d

# 7. Verify the file is in the container
sleep 5
docker compose exec api ls -la /app/api/cache.py

# 8. Test import
docker compose exec api python -c "from api.cache import cache; print('✓ SUCCESS: Cache module loaded!')"

# 9. Watch logs
docker compose logs -f api
```

## 📋 Checklist

- [ ] Verify `api/cache.py` exists locally: `dir api\cache.py`
- [ ] Upload file to AWS server
- [ ] SSH into AWS server
- [ ] Navigate to project directory: `cd /path/to/kidsmart-plus`
- [ ] Verify file on server: `ls -la api/cache.py`
- [ ] View file contents: `cat api/cache.py`
- [ ] Stop containers: `docker compose down`
- [ ] Remove old images: `docker compose down --rmi all`
- [ ] Clear cache: `docker builder prune -f`
- [ ] Build with no cache: `docker compose build --no-cache`
- [ ] Start services: `docker compose up -d`
- [ ] Verify in container: `docker compose exec api ls -la /app/api/cache.py`
- [ ] Test import: `docker compose exec api python -c "from api.cache import cache; print('OK')"`
- [ ] Check logs: `docker compose logs api`

## 🔍 Detailed Verification

### On Your Local Machine (Windows):

```cmd
REM Check the file exists
dir api\cache.py

REM Show file size (should be around 1 KB)
dir api\cache.py | find "cache.py"

REM Show first few lines
type api\cache.py | more
```

### On AWS Server:

```bash
# Check file on filesystem
ls -lh api/cache.py

# Show file size (should match local)
du -h api/cache.py

# Show contents
cat api/cache.py

# Check file permissions (should be readable)
stat api/cache.py
```

### After Docker Build:

```bash
# Verify file is in the image
docker compose exec api test -f /app/api/cache.py && echo "File exists in container" || echo "File MISSING in container"

# Show file in container
docker compose exec api cat /app/api/cache.py

# Test Python can import it
docker compose exec api python -c "import sys; print(sys.path)"
docker compose exec api python -c "from api.cache import cache; print(cache)"
```

## 🚨 If File is Still Missing After Upload

If you've uploaded the file and rebuilt but it's still missing:

### Check .dockerignore

```bash
cat .dockerignore | grep -i cache
```

If you see `cache.py` or `*.cache.py` or `**/cache.py`, remove that line.

### Check for Hidden Characters

```bash
# The filename might have hidden characters
ls -la api/ | cat -A
```

### Try Explicit COPY in Dockerfile

Edit Dockerfile and add before the general `COPY . /app`:

```dockerfile
# Explicitly copy api directory first
COPY ../api /app/api/

# Then copy everything else
COPY .. /app
```

### Nuclear Option - Copy File Directly into Running Container

```bash
# This is a temporary fix to test
docker compose up -d
docker cp api/cache.py $(docker compose ps -q api):/app/api/cache.py
docker compose restart api
docker compose logs -f api
```

## 📞 What to Check If This Doesn't Work

1. **File permissions on AWS server:**
   ```bash
   ls -la api/cache.py
   chmod 644 api/cache.py
   ```

2. **Python path in container:**
   ```bash
   docker compose exec api python -c "import sys; print('\\n'.join(sys.path))"
   ```

3. **API directory structure in container:**
   ```bash
   docker compose exec api ls -la /app/api/
   ```

4. **Check if __init__.py exists:**
   ```bash
   docker compose exec api ls -la /app/api/__init__.py
   ```

## ✅ Success Indicators

You've fixed it when you see:

```bash
$ docker compose exec api python -c "from api.cache import cache; print('OK')"
OK

$ docker compose logs api
...
Created admin user from env
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**No more `ModuleNotFoundError: No module named 'api.cache'`**

---

## 💡 Prevention for Future

1. **Always verify files are uploaded** before building Docker image
2. **Use the verification script** before deploying: `python verify_deployment.py`
3. **Use rsync** instead of manual file copying for consistency
4. **Set up Git on AWS** and use `git pull` to sync files

## 📦 The api/cache.py File

For reference, this is what should be in `api/cache.py`:

```python
"""Simple in-memory cache for API responses."""
import json
from typing import Any, Optional
from datetime import datetime, timedelta


class Cache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        self._cache = {}
    
    def get_json(self, key: str) -> Optional[Any]:
        """Get a value from cache as JSON."""
        if key in self._cache:
            value, expiry = self._cache[key]
            if datetime.utcnow() < expiry:
                return value
            else:
                # Expired, remove it
                del self._cache[key]
        return None
    
    def set_json(self, key: str, value: Any, ttl: int = 60):
        """Set a value in cache with TTL in seconds."""
        expiry = datetime.utcnow() + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry)
    
    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()


# Global cache instance
cache = Cache()
```

If this file is missing, you can create it manually on the AWS server.

---

**TL;DR: Upload api/cache.py to AWS server, then rebuild Docker image with --no-cache flag.**

