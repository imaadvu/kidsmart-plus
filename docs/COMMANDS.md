# 🚀 KidsSmart+ AWS Deployment - Command Reference

## 📋 Pre-Deployment (Local Machine)

```bash
# Verify all files are ready
python verify_deployment.py
```

## 📤 Upload to AWS

```bash
# Option 1: Using SCP
scp -r . user@your-aws-server:/path/to/kidsmart-plus/

# Option 2: Using rsync (faster, only uploads changed files)
rsync -avz --progress . user@your-aws-server:/path/to/kidsmart-plus/

# Option 3: Using Git (if you have a repository)
git add .
git commit -m "Fix deployment issues"
git push origin main
# Then on AWS: git pull origin main
```

## 🚀 Deploy on AWS Server

### Quick Deploy (Copy-Paste)
```bash
cd /path/to/kidsmart-plus/
docker compose down --rmi all --volumes
docker builder prune -f
docker compose build --no-cache
docker compose up -d
docker compose logs -f api
```

### Step-by-Step Deploy
```bash
# 1. Navigate to project
cd /path/to/kidsmart-plus/

# 2. Stop containers
docker compose down

# 3. Remove old images (forces complete rebuild)
docker compose down --rmi all --volumes

# 4. Clear build cache
docker builder prune -f

# 5. Build fresh image
docker compose build --no-cache

# 6. Start services
docker compose up -d

# 7. Watch API logs
docker compose logs -f api
```

## ✅ Verification Commands

```bash
# Check all services
docker compose ps

# Test module import
docker compose exec api python -c "from api.cache import cache; print('✓')"

# Test bcrypt
docker compose exec api python -c "import bcrypt; print(bcrypt.__version__)"

# Test API endpoint
curl http://localhost:8000/docs

# Run full test suite
chmod +x test-deployment.sh
./test-deployment.sh
```

## 🔍 Debugging Commands

```bash
# View logs
docker compose logs api                # All API logs
docker compose logs --tail=50 api     # Last 50 lines
docker compose logs -f api            # Follow in real-time

# Check file exists in container
docker compose exec api ls -la /app/api/cache.py

# Check installed packages
docker compose exec api pip list | grep bcrypt
docker compose exec api pip list | grep passlib

# Enter container shell
docker compose exec api /bin/bash

# Check environment variables
docker compose exec api env | grep ADMIN

# Database connection test
docker compose exec api python -c "from core.db import SessionLocal; SessionLocal()"
```

## 🔄 Common Operations

### Restart Services
```bash
docker compose restart api
docker compose restart
```

### View Resource Usage
```bash
docker stats
```

### Update Code (without rebuilding image)
```bash
# Only works if you're not changing dependencies
docker compose down
docker compose up -d
```

### Complete Cleanup
```bash
docker compose down --rmi all --volumes
docker system prune -af
docker volume prune -f
```

## 🛠️ Troubleshooting

### Container won't start
```bash
docker compose logs api
docker compose ps
```

### Port already in use
```bash
# Find what's using port 8000
sudo lsof -i :8000
sudo netstat -tulpn | grep :8000

# Kill the process
sudo kill -9 <PID>
```

### Database issues
```bash
docker compose logs db
docker compose restart db
docker compose exec db psql -U postgres -d kidssmart
```

### Clear everything and start fresh
```bash
docker compose down --rmi all --volumes
docker system prune -af
rm -rf volumes/  # If you have local volumes
docker compose build --no-cache
docker compose up -d
```

## 📊 Health Checks

### Quick Health Check
```bash
# All-in-one health check
docker compose ps && \
docker compose exec api python -c "from api.cache import cache; print('✓ Cache OK')" && \
curl -s http://localhost:8000/docs > /dev/null && echo "✓ API OK" || echo "✗ API Failed"
```

### Individual Service Checks
```bash
# Database
docker compose exec db pg_isready -U postgres

# Redis
docker compose exec redis redis-cli ping

# API
curl http://localhost:8000/health  # If you have a health endpoint
```

## 🔐 Security

### View environment variables (be careful!)
```bash
docker compose config
```

### Change admin password
```bash
# Edit .env file
nano .env
# Update ADMIN_PASSWORD
# Restart
docker compose restart api
```

## 📦 Backup & Restore

### Backup Database
```bash
docker compose exec db pg_dump -U postgres kidssmart > backup.sql
```

### Restore Database
```bash
docker compose exec -T db psql -U postgres kidssmart < backup.sql
```

## 🎯 Access Points

After successful deployment:
- **API Documentation:** http://your-server:8000/docs
- **Dashboard:** http://your-server:8501
- **Database:** localhost:5432 (from server)
- **Redis:** localhost:6379 (from server)

## 💡 Tips

1. **Always use `--no-cache` on first deployment** to ensure all files are included
2. **Monitor logs during deployment** with `docker compose logs -f api`
3. **Test module imports** before assuming deployment succeeded
4. **Keep `.env` file secure** - never commit to git
5. **Regular backups** of database volumes

## 🆘 Emergency Commands

```bash
# Nuclear option - complete reset
docker compose down --rmi all --volumes
docker system prune -af --volumes
docker volume prune -f
rm -rf __pycache__ */__pycache__ */*/__pycache__
docker compose build --no-cache
docker compose up -d

# If still failing, check files are on server
ls -la api/cache.py
cat requirements-base.txt | grep bcrypt
```

---

**Quick Win:** Just run `deploy-aws.sh` for automated deployment!

