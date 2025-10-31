#!/usr/bin/env python3
"""
Test script to check if pip can download packages successfully
Run this before Docker build to diagnose network issues
"""

import time
import subprocess
import sys

def test_pip_download(package, timeout=300):
    """Test downloading a specific package"""
    print(f"\n{'='*60}")
    print(f"Testing download of: {package}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        # Try to download the package (without installing)
        cmd = [
            sys.executable, "-m", "pip", "download",
            "--no-deps",  # Don't download dependencies
            "--timeout", str(timeout),
            package,
            "-d", "./test_downloads"
        ]

        print(f"Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✓ SUCCESS: Downloaded in {elapsed:.2f} seconds")
            return True
        else:
            print(f"✗ FAILED: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"✗ TIMEOUT: Failed after {elapsed:.2f} seconds")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    print("KidsSmart+ Docker Build Network Test")
    print("=" * 60)

    # Test packages from largest to smallest
    test_packages = [
        ("playwright==1.47.0", "Playwright (38MB - largest, most likely to timeout)"),
        ("numpy==2.1.2", "NumPy (16MB)"),
        ("pandas==2.2.3", "Pandas (13MB)"),
        ("scikit-learn==1.5.2", "Scikit-learn (13MB)"),
        ("streamlit==1.39.0", "Streamlit (8.7MB)"),
    ]

    results = {}

    for package, description in test_packages:
        print(f"\n{description}")
        results[package] = test_pip_download(package, timeout=300)
        time.sleep(2)  # Brief pause between tests

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = all(results.values())

    for package, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {package}")

    print("\n" + "=" * 60)

    if all_passed:
        print("✓ All packages downloaded successfully!")
        print("  Docker build should work fine.")
    else:
        print("✗ Some packages failed to download.")
        print("\nRecommendations:")
        print("1. Check your internet connection stability")
        print("2. Try again during off-peak hours")
        print("3. Consider using a PyPI mirror (see DOCKER_BUILD_FIXES.md)")
        print("4. Use the alternative Dockerfile with longer timeouts")
        print("5. Pre-download wheels manually (see DOCKER_BUILD_FIXES.md)")

    print("\nCleanup: You can delete ./test_downloads directory")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

