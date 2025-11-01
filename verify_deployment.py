"""
Pre-deployment verification script for KidsSmart+
Run this before deploying to AWS to ensure all required files are present
"""
import os
import sys
from pathlib import Path

def check_file(filepath, description):
    """Check if a file exists and is not empty"""
    if not os.path.exists(filepath):
        print(f"❌ MISSING: {filepath} - {description}")
        return False
    
    if os.path.getsize(filepath) == 0:
        print(f"⚠️  EMPTY: {filepath} - {description}")
        return False
    
    print(f"✅ OK: {filepath}")
    return True

def check_docker_files():
    """Verify Docker-related files"""
    print("\n=== Docker Files ===")
    files = {
        "Dockerfile": "Main Docker build file",
        "docker-compose.yml": "Docker compose configuration",
        ".dockerignore": "Docker ignore patterns"
    }
    return all(check_file(f, desc) for f, desc in files.items())

def check_api_files():
    """Verify API files"""
    print("\n=== API Files ===")
    files = {
        "api/__init__.py": "API package initializer",
        "api/main.py": "Main FastAPI application",
        "api/auth.py": "Authentication module",
        "api/cache.py": "Cache module (CRITICAL)",
        "api/deps.py": "Dependencies module",
        "api/ratelimit.py": "Rate limiting module"
    }
    return all(check_file(f, desc) for f, desc in files.items())

def check_requirements():
    """Verify requirements files and check for bcrypt"""
    print("\n=== Requirements Files ===")
    files = {
        "requirements-base.txt": "Base requirements",
        "requirements-ml.txt": "ML requirements",
        "requirements-playwright.txt": "Playwright requirements",
        "requirements.txt": "Combined requirements"
    }
    
    all_ok = all(check_file(f, desc) for f, desc in files.items())
    
    # Check for bcrypt in requirements
    print("\n=== Checking bcrypt in requirements ===")
    for req_file in ["requirements-base.txt", "requirements.txt"]:
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                content = f.read()
                if 'bcrypt==4.0.1' in content:
                    print(f"✅ {req_file} contains bcrypt==4.0.1")
                else:
                    print(f"❌ {req_file} missing bcrypt==4.0.1")
                    all_ok = False
    
    return all_ok

def check_scripts():
    """Verify script files"""
    print("\n=== Script Files ===")
    files = {
        "scripts/start_api.py": "API startup script",
        "scripts/ingest_all.py": "Data ingestion script",
        "scripts/migrate_seed.py": "Migration and seed script"
    }
    return all(check_file(f, desc) for f, desc in files.items())

def check_core_modules():
    """Verify core modules"""
    print("\n=== Core Modules ===")
    files = {
        "core/__init__.py": "Core package initializer",
        "core/db.py": "Database module",
        "core/settings.py": "Settings module",
        "core/etl.py": "ETL module"
    }
    return all(check_file(f, desc) for f, desc in files.items())

def check_env_example():
    """Check if .env.example exists for reference"""
    print("\n=== Environment Configuration ===")
    if os.path.exists(".env"):
        print("✅ .env file exists (won't be copied to Docker, that's correct)")
    else:
        print("⚠️  .env file not found - make sure it exists on the server")
    
    if os.path.exists(".env.example"):
        print("✅ .env.example exists (good for documentation)")
    else:
        print("⚠️  .env.example not found")
    
    return True

def main():
    """Run all checks"""
    print("=" * 60)
    print("KidsSmart+ Pre-Deployment Verification")
    print("=" * 60)
    
    checks = [
        check_docker_files(),
        check_api_files(),
        check_requirements(),
        check_scripts(),
        check_core_modules(),
        check_env_example()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ ALL CHECKS PASSED - Ready for deployment!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Upload all files to AWS server")
        print("2. Run: docker compose build --no-cache")
        print("3. Run: docker compose up -d")
        print("4. Check logs: docker compose logs -f api")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Fix issues before deploying")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

