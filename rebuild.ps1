# KidsSmart+ Docker Cleanup and Rebuild Script (PowerShell)
# This script cleans up Docker images and rebuilds the project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "KidsSmart+ Docker Cleanup and Rebuild" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[Step 1/5] Stopping all containers..." -ForegroundColor Yellow
docker compose down
Write-Host ""

Write-Host "[Step 2/5] Removing old images and volumes..." -ForegroundColor Yellow
docker compose down --rmi all --volumes
Write-Host ""

Write-Host "[Step 3/5] Cleaning Docker build cache..." -ForegroundColor Yellow
docker builder prune -f
Write-Host ""

Write-Host "[Step 4/5] Building fresh images (this may take 10-15 minutes)..." -ForegroundColor Yellow
docker compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "[Step 5/5] Starting services..." -ForegroundColor Yellow
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start services!" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services running:" -ForegroundColor Cyan
docker compose ps
Write-Host ""
Write-Host "API: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Dashboard: http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  View logs: docker compose logs -f" -ForegroundColor White
Write-Host "  Stop services: docker compose down" -ForegroundColor White
Write-Host "  Restart: docker compose restart" -ForegroundColor White
Write-Host ""

