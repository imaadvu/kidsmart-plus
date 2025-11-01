#!/bin/bash
# AWS Deployment Script for KidsSmart+
# This script automates the deployment process on AWS

set -e  # Exit on any error

echo "=============================================="
echo "KidsSmart+ AWS Deployment Script"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Step 1: Check prerequisites
print_info "Step 1: Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is installed"

# Step 2: Check for .env file
print_info "Step 2: Checking for .env file..."
if [ ! -f .env ]; then
    print_error ".env file not found!"
    echo ""
    echo "Please create a .env file with the following variables:"
    echo "  DB_URL=postgresql://postgres:postgres@db:5432/kidssmart"
    echo "  REDIS_URL=redis://redis:6379/0"
    echo "  ADMIN_USERNAME=admin"
    echo "  ADMIN_PASSWORD=your-secure-password"
    echo "  SECRET_KEY=your-secret-key"
    echo ""
    exit 1
fi
print_success ".env file found"

# Step 3: Verify critical files
print_info "Step 3: Verifying critical files..."
CRITICAL_FILES=(
    "api/cache.py"
    "api/main.py"
    "scripts/start_api.py"
    "requirements-base.txt"
    "docker-compose.yml"
    "Dockerfile"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Critical file missing: $file"
        exit 1
    fi
done
print_success "All critical files present"

# Step 4: Check bcrypt in requirements
print_info "Step 4: Checking bcrypt version in requirements..."
if ! grep -q "bcrypt==4.0.1" requirements-base.txt; then
    print_error "bcrypt==4.0.1 not found in requirements-base.txt"
    exit 1
fi
print_success "bcrypt version correct in requirements"

# Step 5: Stop existing containers
print_info "Step 5: Stopping existing containers..."
docker compose down || true
print_success "Containers stopped"

# Step 6: Remove old images (optional, uncomment for full rebuild)
read -p "Remove old images for complete rebuild? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Removing old images and volumes..."
    docker compose down --rmi all --volumes || true
    docker builder prune -f || true
    print_success "Old images removed"
fi

# Step 7: Build new image
print_info "Step 7: Building Docker image..."
docker compose build --no-cache
print_success "Docker image built"

# Step 8: Start services
print_info "Step 8: Starting services..."
docker compose up -d
print_success "Services started"

# Step 9: Wait for services to be healthy
print_info "Step 9: Waiting for services to become healthy..."
sleep 10

# Step 10: Check service status
print_info "Step 10: Checking service status..."
docker compose ps

# Step 11: Show API logs
echo ""
print_info "API Container Logs (last 50 lines):"
echo "=============================================="
docker compose logs --tail=50 api

# Step 12: Verify API is responding
echo ""
print_info "Step 11: Verifying API is responding..."
sleep 5

if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
    print_success "API is responding!"
    echo ""
    echo "=============================================="
    echo -e "${GREEN}Deployment Successful!${NC}"
    echo "=============================================="
    echo ""
    echo "Access your services at:"
    echo "  - API Docs:    http://localhost:8000/docs"
    echo "  - Dashboard:   http://localhost:8501"
    echo ""
    echo "To view logs:"
    echo "  docker compose logs -f api"
    echo "  docker compose logs -f dashboard"
    echo ""
    echo "To stop services:"
    echo "  docker compose down"
    echo ""
else
    print_error "API is not responding. Check the logs above."
    echo ""
    echo "To troubleshoot:"
    echo "  docker compose logs api"
    echo "  docker compose exec api python -c 'from api.cache import cache; print(\"OK\")'"
    echo ""
    exit 1
fi

