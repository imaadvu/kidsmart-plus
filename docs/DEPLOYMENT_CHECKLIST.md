# AWS Deployment Checklist

## Issues Fixed

### 1. ✅ ModuleNotFoundError: No module named 'api.cache'
**Root Cause**: The `api/cache.py` file exists locally but may not have been copied to the server or the Docker image wasn't rebuilt.

**Solution**: 
- Ensure all files are uploaded to the server
- Rebuild the Docker image after uploading files

### 2. ✅ bcrypt version compatibility error
**Root Cause**: Passlib 1.7.4 has compatibility issues with newer bcrypt versions.

**Solution**: 
- Added explicit `bcrypt==4.0.1` to requirements files
- This version is compatible with both passlib and Python 3.11

### 3. ✅ Admin password too long (>72 bytes)
**Root Cause**: bcrypt has a 72-byte limit for passwords.

**Solution**: 
- Modified `scripts/start_api.py` to truncate password to 72 bytes
- Password is now automatically truncated: `admin_pwd = settings.admin_password[:72]`

## Deployment Steps for AWS

### Step 1: Upload Updated Files
```bash
# On your local machine, ensure these files are updated on the server:
# - requirements-base.txt (with bcrypt==4.0.1)
# - requirements.txt (with bcrypt==4.0.1)
# - scripts/start_api.py (with password truncation)
# - api/cache.py (must be present)

# Use SCP or your preferred method:
scp -r . your-aws-server:/path/to/kidsmart-plus/
```

### Step 2: Rebuild Docker Image
```bash
# SSH into your AWS server
ssh your-aws-server

# Navigate to the project directory
cd /path/to/kidsmart-plus/

# Stop all running containers
docker compose down

# Remove old images to force rebuild
docker compose down --rmi all

# Rebuild with no cache to ensure all changes are included
docker compose build --no-cache

# Start services
docker compose up -d
```

### Step 3: Verify Deployment
```bash
# Check logs for the API container
docker compose logs api

# You should see:
# - "Seeded demo data" (if database was empty)
# - "Created admin user from env"
# - API server starting on port 8000

# Check if all services are running
docker compose ps

# Test the API
curl http://localhost:8000/docs
```

### Step 4: Monitor for Issues
```bash
# Watch logs in real-time
docker compose logs -f api

# Check if modules are properly loaded
docker compose exec api python -c "from api.cache import cache; print('Cache module OK')"

# Check bcrypt version
docker compose exec api python -c "import bcrypt; print(f'bcrypt version: {bcrypt.__version__}')"
```

## Environment Variables to Check

Ensure your `.env` file on the AWS server contains:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=kidssmart
DB_URL=postgresql://postgres:postgres@db:5432/kidssmart

# Redis
REDIS_URL=redis://redis:6379/0

# Admin credentials (will be truncated to 72 bytes automatically)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password-here

# JWT
SECRET_KEY=your-secret-key-here
JWT_ALGO=HS256

# Optional features
ENABLE_PLAYWRIGHT=false
ENABLE_EMBEDDINGS=false
GEOCODING_ENABLED=false
```

## Quick Rebuild Commands (Copy-Paste)

### Complete Rebuild (Recommended for first deployment after fixes)
```bash
docker compose down --rmi all --volumes
docker compose build --no-cache
docker compose up -d
docker compose logs -f api
```

### Fast Rebuild (If only code changed, no dependency changes)
```bash
docker compose down
docker compose build
docker compose up -d
docker compose logs -f api
```

### Emergency Stop and Cleanup
```bash
docker compose down
docker system prune -af
docker volume prune -f
```

## Troubleshooting

### If you still see "No module named 'api.cache'"
1. Verify the file exists in the container:
   ```bash
   docker compose exec api ls -la /app/api/cache.py
   ```
2. If missing, check .dockerignore isn't excluding it
3. Rebuild with --no-cache flag

### If you see bcrypt errors
1. Check installed version:
   ```bash
   docker compose exec api pip show bcrypt passlib
   ```
2. Should see bcrypt==4.0.1 and passlib==1.7.4

### If admin user creation fails
1. Check password length in .env
2. Ensure SECRET_KEY is set
3. Check database connectivity:
   ```bash
   docker compose exec api python -c "from core.db import SessionLocal; db = SessionLocal(); print('DB OK')"
   ```

## Files Changed
- ✅ `requirements-base.txt` - Added bcrypt==4.0.1
- ✅ `requirements.txt` - Added bcrypt==4.0.1
- ✅ `scripts/start_api.py` - Added password truncation
- ✅ `api/cache.py` - Already exists (verify it's on server)

## Next Steps After Deployment

1. Access API docs: `http://your-server:8000/docs`
2. Access Dashboard: `http://your-server:8501`
3. Login with admin credentials from .env
4. Test the authentication flow
5. Run data ingestion if needed

