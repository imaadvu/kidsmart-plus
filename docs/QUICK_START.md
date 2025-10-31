# Quick Start Guide - Fixed Docker Build

## ✅ What Was Fixed

The Docker build timeout issue has been resolved by:
1. Splitting requirements into 3 files for staged installation
2. Increasing pip timeout from 15s to 1000s
3. Adding 5 retry attempts for failed downloads
4. Optimizing Docker layer caching

## 🚀 Build the Project

### Option 1: Standard Build (Recommended)
```bash
docker compose up --build
```

This will:
- Build all services (api, dashboard, worker, beat)
- Start PostgreSQL and Redis
- Run database migrations
- Start the application

### Option 2: Build Only API Service First
```bash
# Build just the API to test
docker compose build api

# Then start all services
docker compose up
```

### Option 3: Build Without Cache (Clean Build)
```bash
docker compose build --no-cache
docker compose up
```

## 📊 Build Progress

The build process now happens in stages:

1. **Base System** (~2 minutes)
   - Python 3.11 slim image
   - System dependencies (build-essential, curl)

2. **Base Python Packages** (~3-5 minutes)
   - FastAPI, SQLAlchemy, Celery, Redis, etc.
   - 21 core packages

3. **ML/Data Science Packages** (~5-8 minutes)
   - NumPy, Pandas, Scikit-learn, Streamlit
   - 4 large packages (~50MB total)

4. **Playwright** (~2-3 minutes)
   - Playwright package (~38MB)
   - Most likely to timeout, now installed separately

**Total Time**: 12-18 minutes (first build)  
**Subsequent Builds**: 1-2 minutes (with caching)

## ✓ Verification

After build completes, verify services are running:

```bash
# Check running containers
docker compose ps

# Check API logs
docker compose logs api

# Test API endpoint
curl http://localhost:8000/docs

# Test Dashboard
# Open browser: http://localhost:8501
```

## 🆘 If Build Still Fails

### Quick Fixes:

**1. Network timeout?** - Increase timeout further:
   Edit `Dockerfile`, change `--timeout=1000` to `--timeout=2000`

**2. Slow internet?** - Use alternative Dockerfile:
   ```bash
   # Backup current
   mv Dockerfile Dockerfile.backup
   
   # Use alternative (has longer timeouts)
   mv Dockerfile.alternative Dockerfile
   
   # Build
   docker compose build
   ```

**3. Test network first:**
   ```bash
   python test_network.py
   ```

**4. Temporary disable Playwright:**
   Edit `requirements-playwright.txt`:
   ```
   # playwright==1.47.0
   ```
   Then rebuild. Install playwright later if needed.

### Full Solutions:
See `DOCKER_BUILD_FIXES.md` for 7 detailed solutions.

## 📁 Files Created/Modified

### Modified:
- `Dockerfile` - Optimized with staged installation
- `README.md` - Added troubleshooting note

### Created:
- `requirements-base.txt` - Core packages
- `requirements-ml.txt` - Data science packages  
- `requirements-playwright.txt` - Playwright only
- `.dockerignore` - Speed up builds
- `Dockerfile.alternative` - Backup solution
- `DOCKER_BUILD_FIXES.md` - Comprehensive guide
- `test_network.py` - Network test script
- `QUICK_START.md` - This file

## 🎯 Next Steps After Successful Build

1. **Create .env file** (if not exists):
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Access the application**:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Dashboard: http://localhost:8501

3. **Create admin user** (if needed):
   ```bash
   docker compose exec api python -c "from scripts.create_admin import create_admin; create_admin()"
   ```

4. **Run tests**:
   ```bash
   docker compose exec api pytest
   ```

## 💡 Tips

- **First build is slow** - Be patient, subsequent builds are much faster
- **Use ethernet** - More stable than WiFi for large downloads
- **Off-peak hours** - Build during less busy internet times
- **BuildKit** - Enable for better caching: `$env:DOCKER_BUILDKIT=1`
- **Clean up** - Remove old images: `docker system prune -a`

## ❓ Common Issues

**"no space left on device"**
```bash
docker system prune -a
```

**"port already in use"**
```bash
# Stop conflicting services
docker compose down
# Or change ports in docker-compose.yml
```

**"requirements-*.txt not found"**
```bash
# Make sure you're in the project directory
cd D:\Python\kidsmart-plus
# Verify files exist
ls requirements*.txt
```

---
**Need help?** Check `DOCKER_BUILD_FIXES.md` for detailed troubleshooting.

