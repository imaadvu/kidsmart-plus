#!/bin/bash
# Emergency script to create api/cache.py if missing on AWS server
# Run this on AWS server if the file is missing

set -e

CACHE_FILE="api/cache.py"

echo "=========================================="
echo "Emergency Cache File Creator"
echo "=========================================="
echo ""

# Check if api directory exists
if [ ! -d "api" ]; then
    echo "ERROR: api directory not found!"
    echo "Make sure you're in the project root directory."
    exit 1
fi

# Check if file already exists
if [ -f "$CACHE_FILE" ]; then
    echo "WARNING: $CACHE_FILE already exists!"
    echo "File size: $(wc -c < $CACHE_FILE) bytes"
    echo ""
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Create the cache.py file
echo "Creating $CACHE_FILE..."

cat > "$CACHE_FILE" << 'EOF'
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

# Verify file was created
if [ -f "$CACHE_FILE" ]; then
    echo "✓ SUCCESS: $CACHE_FILE created!"
    echo "  File size: $(wc -c < $CACHE_FILE) bytes"
    echo "  Location: $(pwd)/$CACHE_FILE"
    echo ""
    echo "File contents (first 10 lines):"
    head -n 10 "$CACHE_FILE"
    echo ""
    echo "=========================================="
    echo "Next steps:"
    echo "1. Rebuild Docker image: docker compose build --no-cache"
    echo "2. Start services: docker compose up -d"
    echo "3. Check logs: docker compose logs -f api"
    echo "=========================================="
else
    echo "✗ ERROR: Failed to create $CACHE_FILE"
    exit 1
fi

