# 🔥 CRITICAL: api/cache.py Missing on AWS Server

## Current Status

✅ **Good News:** Admin user was created successfully (bcrypt works!)
❌ **Problem:** `api/cache.py` file is NOT in your Docker container on AWS

## Error You're Seeing
```
Created admin user from env  ← This worked!
ModuleNotFoundError: No module named 'api.cache'  ← This is failing
```

---

## 🎯 SOLUTION (Copy-Paste Commands)

### On Your AWS Server (SSH into it first)

```bash
# Step 1: Go to project directory
cd /path/to/kidsmart-plus

# Step 2: Check if cache.py exists on the server filesystem
ls -la api/cache.py

# If file is MISSING, create it:
chmod +x create-cache-file.sh
./create-cache-file.sh

# If file EXISTS, continue:

# Step 3: Stop containers
docker compose down

# Step 4: Remove old images (IMPORTANT!)
docker compose down --rmi all

# Step 5: Clear Docker build cache
docker builder prune -f

# Step 6: Build fresh image (will now include cache.py)
docker compose build --no-cache

# Step 7: Start services
docker compose up -d

# Step 8: Verify file is in container
docker compose exec api ls -la /app/api/cache.py

# Step 9: Test module import
docker compose exec api python -c "from api.cache import cache; print('✓ SUCCESS!')"

# Step 10: Watch logs
docker compose logs -f api
```

---

## 📤 If File is Missing from AWS Server

The `api/cache.py` file exists on your **local Windows machine** but not on **AWS server**.

### Option 1: Use the Emergency Script (Recommended)

On AWS server:
```bash
cd /path/to/kidsmart-plus
chmod +x create-cache-file.sh
./create-cache-file.sh
```

This creates the file automatically.

### Option 2: Upload from Windows

From your Windows machine:
```cmd
REM Upload the single file
scp api\cache.py user@your-aws-ip:/path/to/kidsmart-plus/api/cache.py

REM Or upload entire api folder
scp -r api user@your-aws-ip:/path/to/kidsmart-plus/
```

### Option 3: Create Manually on AWS

SSH into AWS and run:
```bash
cd /path/to/kidsmart-plus
cat > api/cache.py << 'EOF'
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
EOF

# Verify it was created
cat api/cache.py
```

---

## ✅ After File is on AWS Server

Once `api/cache.py` exists on your AWS server filesystem:

```bash
# 1. Verify file exists
ls -la api/cache.py
cat api/cache.py  # Should show the cache module code

# 2. Rebuild Docker image
docker compose down --rmi all
docker builder prune -f
docker compose build --no-cache

# 3. Start services
docker compose up -d

# 4. Verify SUCCESS
docker compose exec api python -c "from api.cache import cache; print('✓ Module loaded successfully!')"

# 5. Check API logs
docker compose logs -f api
```

---

## 🎉 Success Indicators

You've fixed it when you see:

### In the verify command:
```bash
$ docker compose exec api python -c "from api.cache import cache; print('✓ Module loaded successfully!')"
✓ Module loaded successfully!
```

### In the logs:
```
Created admin user from env
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### No more errors:
- ✅ No `ModuleNotFoundError`
- ✅ No import errors
- ✅ API starts successfully

---

## 🔍 Troubleshooting

### If "create-cache-file.sh" doesn't exist on AWS:

You need to upload it first:
```cmd
REM From Windows
scp create-cache-file.sh user@your-aws-ip:/path/to/kidsmart-plus/
```

Or just create the file manually (see Option 3 above).

### If file exists but still getting error:

1. **Check file in container:**
   ```bash
   docker compose exec api ls -la /app/api/
   docker compose exec api cat /app/api/cache.py
   ```

2. **Check __init__.py exists:**
   ```bash
   docker compose exec api ls -la /app/api/__init__.py
   ```

3. **Rebuild without cache:**
   ```bash
   docker compose down --rmi all --volumes
   docker system prune -af
   docker compose build --no-cache
   docker compose up -d
   ```

### If you can't SSH into AWS:

Use AWS Systems Manager Session Manager or EC2 Instance Connect instead of SSH.

---

## 📋 Complete Checklist

- [ ] SSH into AWS server
- [ ] Navigate to project: `cd /path/to/kidsmart-plus`
- [ ] Check if cache.py exists: `ls -la api/cache.py`
- [ ] If missing, create it (use script or manual method)
- [ ] Verify file contents: `cat api/cache.py`
- [ ] Stop containers: `docker compose down`
- [ ] Remove old images: `docker compose down --rmi all`
- [ ] Clear cache: `docker builder prune -f`
- [ ] Build fresh: `docker compose build --no-cache`
- [ ] Start services: `docker compose up -d`
- [ ] Verify in container: `docker compose exec api ls -la /app/api/cache.py`
- [ ] Test import: `docker compose exec api python -c "from api.cache import cache; print('OK')"`
- [ ] Check logs: `docker compose logs api`
- [ ] Access API docs: `curl http://localhost:8000/docs`

---

## 💡 Why This Happened

1. The file exists on your local Windows machine
2. But it wasn't uploaded to AWS server (or was deleted somehow)
3. Docker built the image without the file
4. Now the container is missing the module

**Solution:** Upload the file, rebuild the image.

---

## 📞 Quick Reference

### File Location:
- **Local (Windows):** `D:\Python\kidsmart-plus\api\cache.py`
- **AWS Server:** `/path/to/kidsmart-plus/api/cache.py`
- **Docker Container:** `/app/api/cache.py`

### File Size:
- Should be approximately **1,000 bytes** (1 KB)

### Required Files in api/:
```
api/
├── __init__.py
├── main.py
├── auth.py
├── cache.py  ← THIS ONE IS MISSING
├── deps.py
└── ratelimit.py
```

---

## 🚀 Fastest Fix (All-in-One Command)

SSH into AWS and run this entire block:

```bash
cd /path/to/kidsmart-plus && \
if [ ! -f api/cache.py ]; then echo "File missing! Creating it..." && cat > api/cache.py << 'ENDOFFILE'
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
ENDOFFILE
fi && \
docker compose down --rmi all && \
docker builder prune -f && \
docker compose build --no-cache && \
docker compose up -d && \
sleep 10 && \
docker compose logs --tail=50 api
```

---

**TL;DR:** File is missing on AWS. Create it, rebuild Docker, done.

