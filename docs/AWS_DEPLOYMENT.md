# AWS Deployment Guide for KidsSmart+

## 🔴 Current Issues Fixed

Your deployment was failing with these errors:

1. **`ModuleNotFoundError: No module named 'api.cache'`** ✅ FIXED
   - The `api/cache.py` file exists but wasn't being copied to AWS
   - Solution: Ensure all files are uploaded and rebuild the Docker image

2. **`bcrypt version error`** ✅ FIXED
   - Passlib 1.7.4 had compatibility issues with bcrypt
   - Solution: Added explicit `bcrypt==4.0.1` to requirements files

3. **`password cannot be longer than 72 bytes`** ✅ FIXED
   - Admin password exceeded bcrypt's 72-byte limit
   - Solution: Modified `scripts/start_api.py` to auto-truncate passwords

## 📋 Pre-Deployment Checklist

Before deploying to AWS, run this verification script locally:

```bash
python verify_deployment.py
```

This will check:
- ✅ All Docker files are present
- ✅ API modules exist (including `api/cache.py`)
- ✅ Requirements files have correct bcrypt version
- ✅ All scripts are in place

## 🚀 Quick Deployment (AWS Server)

### Option 1: Automated Deployment (Linux/Mac)

```bash
# Make the script executable
chmod +x deploy-aws.sh

# Run the deployment script
./deploy-aws.sh
```

### Option 2: Automated Deployment (Windows - if you're using Git Bash on AWS)

```bash
./deploy-aws.bat
```

### Option 3: Manual Deployment Steps

```bash
# 1. Stop existing containers
docker compose down

# 2. Remove old images (for complete rebuild)
docker compose down --rmi all --volumes

# 3. Clear Docker cache
docker builder prune -f

# 4. Build fresh image (this ensures all files are included)
docker compose build --no-cache

# 5. Start all services
docker compose up -d

# 6. Check logs
docker compose logs -f api
```

## 🔧 Environment Configuration

Create or update your `.env` file on the AWS server with these variables:

```env
# Database Configuration
DB_URL=postgresql://postgres:postgres@db:5432/kidssmart
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-db-password
POSTGRES_DB=kidssmart

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Admin User (password will be auto-truncated to 72 chars)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password

# JWT Configuration
SECRET_KEY=your-very-long-secret-key-here-minimum-32-characters
JWT_ALGO=HS256

# Optional Features
ENABLE_PLAYWRIGHT=false
ENABLE_EMBEDDINGS=false
GEOCODING_ENABLED=false

# API Keys (optional)
EVENTBRITE_TOKEN=your-eventbrite-token
MEETUP_TOKEN=your-meetup-token
SERPAPI_KEY=your-serpapi-key
MAPS_TOKEN=your-google-maps-token

# Performance
CACHE_TTL=60
RATE_LIMIT_PER_MIN=120
NEARDUP_THRESHOLD=0.85
```

## 📦 Files Changed in This Fix

The following files were updated to fix your deployment issues:

1. **`requirements-base.txt`** - Added `bcrypt==4.0.1`
2. **`requirements.txt`** - Added `bcrypt==4.0.1`
3. **`scripts/start_api.py`** - Added password truncation logic

Make sure these updated files are on your AWS server!

## 🔍 Verification Steps

After deployment, verify everything is working:

### 1. Check All Services Are Running

```bash
docker compose ps
```

Expected output:
```
NAME                   STATUS
kidsmart-plus-api      Up
kidsmart-plus-worker   Up
kidsmart-plus-beat     Up
kidsmart-plus-dashboard Up
kidsmart-plus-db       Up (healthy)
kidsmart-plus-redis    Up
```

### 2. Check API Logs

```bash
docker compose logs api
```

You should see:
- ✅ "Seeded demo data" (if database was empty)
- ✅ "Created admin user from env"
- ✅ No module import errors
- ✅ "Application startup complete"

### 3. Verify Module Loading

```bash
# Test that api.cache module loads correctly
docker compose exec api python -c "from api.cache import cache; print('✓ Cache module OK')"

# Test bcrypt version
docker compose exec api python -c "import bcrypt; print(f'✓ bcrypt version: {bcrypt.__version__}')"

# Test password hashing
docker compose exec api python -c "from passlib.hash import bcrypt; print('✓ Password hashing OK')"
```

### 4. Test API Endpoint

```bash
# From AWS server
curl http://localhost:8000/docs

# From external (replace with your server IP)
curl http://your-aws-ip:8000/docs
```

### 5. Test Authentication

```bash
# Get a token (use your actual credentials from .env)
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your-admin-password"
```

## 🐛 Troubleshooting

### Issue: Still seeing "No module named 'api.cache'"

**Solution:**
```bash
# Verify the file exists in the container
docker compose exec api ls -la /app/api/cache.py

# If missing, rebuild without cache
docker compose build --no-cache api
docker compose up -d
```

### Issue: bcrypt errors persist

**Solution:**
```bash
# Check installed versions
docker compose exec api pip show bcrypt passlib

# Should show:
# bcrypt: 4.0.1
# passlib: 1.7.4

# If not, rebuild the image
docker compose down --rmi all
docker compose build --no-cache
docker compose up -d
```

### Issue: Admin user creation fails

**Solution:**
```bash
# Check your .env file
cat .env | grep ADMIN

# Verify password length
echo -n "your-password-here" | wc -c

# Check database connection
docker compose exec api python -c "from core.db import SessionLocal; db = SessionLocal(); print('DB OK')"
```

### Issue: Database connection errors

**Solution:**
```bash
# Check database is running
docker compose ps db

# Check database logs
docker compose logs db

# Restart database
docker compose restart db

# Wait for health check
docker compose ps
```

### Issue: Port conflicts (8000, 8501 already in use)

**Solution:**
```bash
# Find process using the port
sudo lsof -i :8000
sudo lsof -i :8501

# Kill the process or change ports in docker-compose.yml
```

## 📊 Monitoring

### View Real-time Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f dashboard
```

### Check Resource Usage

```bash
docker stats
```

### Check Container Health

```bash
docker compose ps
docker inspect kidsmart-plus-api | grep -A 10 Health
```

## 🔄 Updating the Deployment

When you make code changes:

```bash
# Pull latest changes (if using git)
git pull origin main

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d

# Check logs
docker compose logs -f api
```

## 🛑 Stopping the Application

```bash
# Stop all services
docker compose down

# Stop and remove volumes (CAUTION: deletes data)
docker compose down --volumes

# Complete cleanup
docker compose down --rmi all --volumes
docker system prune -af
```

## 🔐 Security Checklist

Before going to production:

- [ ] Change `ADMIN_PASSWORD` from default
- [ ] Change `SECRET_KEY` to a long random string
- [ ] Change `POSTGRES_PASSWORD` to a strong password
- [ ] Set up firewall rules (only expose necessary ports)
- [ ] Enable HTTPS with SSL certificates
- [ ] Review `allowed_origins` in settings
- [ ] Enable rate limiting
- [ ] Set up backup for database volumes
- [ ] Review Docker security best practices

## 📞 Support

If you continue to have issues:

1. Run the verification script: `python verify_deployment.py`
2. Check all files are uploaded to AWS server
3. Review deployment logs: `docker compose logs api`
4. Check this guide's troubleshooting section
5. Ensure `.env` file has all required variables

## 🎯 Success Indicators

Your deployment is successful when:

- ✅ All containers show "Up" status
- ✅ API docs accessible at `http://your-server:8000/docs`
- ✅ Dashboard accessible at `http://your-server:8501`
- ✅ No errors in `docker compose logs api`
- ✅ Admin user can login successfully
- ✅ Database has demo data (if seeded)

---

**Last Updated:** Based on fixes for module import, bcrypt compatibility, and password length issues.

