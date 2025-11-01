@echo off
REM AWS Deployment Script for KidsSmart+ (Windows)
REM This script automates the deployment process

echo ==============================================
echo KidsSmart+ AWS Deployment Script
echo ==============================================
echo.

REM Step 1: Check for Docker
echo [Step 1/11] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)
echo OK: Docker is installed
echo.

REM Step 2: Check for docker compose
echo [Step 2/11] Checking Docker Compose...
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose is not available.
    pause
    exit /b 1
)
echo OK: Docker Compose is available
echo.

REM Step 3: Check for .env file
echo [Step 3/11] Checking for .env file...
if not exist .env (
    echo ERROR: .env file not found!
    echo.
    echo Please create a .env file with the following variables:
    echo   DB_URL=postgresql://postgres:postgres@db:5432/kidssmart
    echo   REDIS_URL=redis://redis:6379/0
    echo   ADMIN_USERNAME=admin
    echo   ADMIN_PASSWORD=your-secure-password
    echo   SECRET_KEY=your-secret-key
    echo.
    pause
    exit /b 1
)
echo OK: .env file found
echo.

REM Step 4: Verify critical files
echo [Step 4/11] Verifying critical files...
set MISSING_FILES=0

if not exist "api\cache.py" (
    echo ERROR: api\cache.py is missing!
    set MISSING_FILES=1
)
if not exist "api\main.py" (
    echo ERROR: api\main.py is missing!
    set MISSING_FILES=1
)
if not exist "scripts\start_api.py" (
    echo ERROR: scripts\start_api.py is missing!
    set MISSING_FILES=1
)
if not exist "requirements-base.txt" (
    echo ERROR: requirements-base.txt is missing!
    set MISSING_FILES=1
)
if not exist "docker-compose.yml" (
    echo ERROR: docker-compose.yml is missing!
    set MISSING_FILES=1
)
if not exist "Dockerfile" (
    echo ERROR: Dockerfile is missing!
    set MISSING_FILES=1
)

if %MISSING_FILES% neq 0 (
    echo.
    echo ERROR: Some critical files are missing. Cannot proceed.
    pause
    exit /b 1
)
echo OK: All critical files present
echo.

REM Step 5: Check bcrypt in requirements
echo [Step 5/11] Checking bcrypt version...
findstr /C:"bcrypt==4.0.1" requirements-base.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: bcrypt==4.0.1 not found in requirements-base.txt
    echo This may cause issues. Please add it to requirements.
    pause
)
echo OK: bcrypt version correct
echo.

REM Step 6: Stop existing containers
echo [Step 6/11] Stopping existing containers...
docker compose down
echo OK: Containers stopped
echo.

REM Step 7: Ask about full rebuild
echo [Step 7/11] Docker image cleanup...
set /p FULL_REBUILD="Remove old images for complete rebuild? (y/n): "
if /i "%FULL_REBUILD%"=="y" (
    echo Removing old images and volumes...
    docker compose down --rmi all --volumes
    docker builder prune -f
    echo OK: Old images removed
) else (
    echo Skipping image removal
)
echo.

REM Step 8: Build new image
echo [Step 8/11] Building Docker image (this may take a few minutes)...
docker compose build --no-cache
if %errorlevel% neq 0 (
    echo ERROR: Docker build failed!
    pause
    exit /b 1
)
echo OK: Docker image built successfully
echo.

REM Step 9: Start services
echo [Step 9/11] Starting services...
docker compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start services!
    pause
    exit /b 1
)
echo OK: Services started
echo.

REM Step 10: Wait for services
echo [Step 10/11] Waiting for services to initialize...
timeout /t 15 /nobreak >nul
echo.

REM Step 11: Check service status
echo [Step 11/11] Checking service status...
docker compose ps
echo.

REM Show API logs
echo ==============================================
echo API Container Logs (last 30 lines):
echo ==============================================
docker compose logs --tail=30 api
echo.

REM Final status
echo ==============================================
echo Deployment Complete!
echo ==============================================
echo.
echo Access your services at:
echo   - API Docs:    http://localhost:8000/docs
echo   - Dashboard:   http://localhost:8501
echo.
echo To view logs:
echo   docker compose logs -f api
echo   docker compose logs -f dashboard
echo.
echo To stop services:
echo   docker compose down
echo.
echo Press any key to exit...
pause >nul

