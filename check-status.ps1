# Docker Build Status Checker
# Run this to check the current build/deployment status

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "KidsSmart+ Status Checker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking Docker Images..." -ForegroundColor Yellow
$images = docker images | Select-String "kidsmart"
if ($images) {
    Write-Host "Found KidsSmart+ images:" -ForegroundColor Green
    docker images | Select-String "kidsmart|REPOSITORY"
} else {
    Write-Host "No KidsSmart+ images found yet (build in progress)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Checking Running Containers..." -ForegroundColor Yellow
$containers = docker compose ps
Write-Host $containers
Write-Host ""

$runningCount = (docker compose ps --status running 2>$null | Measure-Object -Line).Lines
if ($runningCount -gt 1) {
    Write-Host "✓ Services are RUNNING!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access your application:" -ForegroundColor Cyan
    Write-Host "  API: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  Dashboard: http://localhost:8501" -ForegroundColor White
    Write-Host ""
    Write-Host "View logs with: docker compose logs -f" -ForegroundColor Gray
} else {
    Write-Host "⏳ Build may still be in progress or services not started yet" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To start services after build completes:" -ForegroundColor Cyan
    Write-Host "  docker compose up -d" -ForegroundColor White
    Write-Host ""
    Write-Host "To check build progress:" -ForegroundColor Cyan
    Write-Host "  docker compose build" -ForegroundColor White
}
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

