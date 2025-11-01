@echo off
REM Emergency script to create api\cache.py if missing
REM Run this on Windows if the file is somehow missing

echo ==========================================
echo Emergency Cache File Creator (Windows)
echo ==========================================
echo.

REM Check if api directory exists
if not exist "api" (
    echo ERROR: api directory not found!
    echo Make sure you're in the project root directory.
    pause
    exit /b 1
)

REM Check if file already exists
if exist "api\cache.py" (
    echo WARNING: api\cache.py already exists!
    echo.
    set /p OVERWRITE="Do you want to overwrite it? (y/n): "
    if /i not "%OVERWRITE%"=="y" (
        echo Cancelled.
        pause
        exit /b 0
    )
)

REM Create the cache.py file
echo Creating api\cache.py...
(
echo """Simple in-memory cache for API responses."""
echo import json
echo from typing import Any, Optional
echo from datetime import datetime, timedelta
echo.
echo.
echo class Cache:
echo     """Simple in-memory cache with TTL support."""
echo
echo     def __init__^(self^):
echo         self._cache = {}
echo
echo     def get_json^(self, key: str^) -^> Optional[Any]:
echo         """Get a value from cache as JSON."""
echo         if key in self._cache:
echo             value, expiry = self._cache[key]
echo             if datetime.utcnow^(^) ^< expiry:
echo                 return value
echo             else:
echo                 # Expired, remove it
echo                 del self._cache[key]
echo         return None
echo
echo     def set_json^(self, key: str, value: Any, ttl: int = 60^):
echo         """Set a value in cache with TTL in seconds."""
echo         expiry = datetime.utcnow^(^) + timedelta^(seconds=ttl^)
echo         self._cache[key] = ^(value, expiry^)
echo
echo     def clear^(self^):
echo         """Clear all cache entries."""
echo         self._cache.clear^(^)
echo.
echo.
echo # Global cache instance
echo cache = Cache^(^)
) > api\cache.py

REM Verify file was created
if exist "api\cache.py" (
    echo.
    echo SUCCESS: api\cache.py created!
    echo File size:
    dir api\cache.py | find "cache.py"
    echo.
    echo File created successfully.
    echo.
    echo ==========================================
    echo Next steps:
    echo 1. Upload this file to your AWS server
    echo 2. Rebuild Docker image: docker compose build --no-cache
    echo 3. Start services: docker compose up -d
    echo ==========================================
) else (
    echo.
    echo ERROR: Failed to create api\cache.py
    pause
    exit /b 1
)

echo.
pause

