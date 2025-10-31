@echo off
REM KidsSmart+ Docker Cleanup and Rebuild Script
REM This script cleans up Docker images and rebuilds the project

echo ========================================
echo KidsSmart+ Docker Cleanup and Rebuild
echo ========================================
echo.

echo [Step 1/5] Stopping all containers...
docker compose down
if %errorlevel% neq 0 (
    echo Warning: Failed to stop containers
)
echo.

echo [Step 2/5] Removing old images and volumes...
docker compose down --rmi all --volumes
if %errorlevel% neq 0 (
    echo Warning: Failed to remove images
)
echo.

echo [Step 3/5] Cleaning Docker build cache...
docker builder prune -f
if %errorlevel% neq 0 (
    echo Warning: Failed to prune builder cache
)
echo.

echo [Step 4/5] Building fresh images...
docker compose build
if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    exit /b 1
)
echo.

echo [Step 5/5] Starting services...
docker compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start services!
    exit /b 1
)
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Services running:
docker compose ps
echo.
echo API: http://localhost:8000/docs
echo Dashboard: http://localhost:8501
echo.
echo To view logs: docker compose logs -f
echo To stop: docker compose down
echo.

