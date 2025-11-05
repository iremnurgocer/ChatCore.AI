# -*- coding: utf-8 -*-
"""
Module: Backend-Frontend Connection Test
Description: Tests backend API accessibility and frontend-backend connection
"""
import requests
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_settings

settings = get_settings()

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"


def test_backend_status():
    """Test backend status endpoint"""
    print("\n" + "=" * 60)
    print("Testing Backend Status")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Backend is running")
            print(f"     Status: {data.get('status', 'unknown')}")
            print(f"     Database: {data.get('database', 'unknown')}")
            print(f"     Redis: {data.get('redis', 'unknown')}")
            return True
        else:
            print(f"[FAIL] Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] Cannot connect to backend at {BACKEND_URL}")
        print(f"     Make sure backend is running: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"[FAIL] Error testing backend: {e}")
        return False


def test_cors():
    """Test CORS configuration"""
    print("\n" + "=" * 60)
    print("Testing CORS Configuration")
    print("=" * 60)
    
    try:
        # Test OPTIONS request (preflight)
        headers = {
            "Origin": FRONTEND_URL,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        response = requests.options(f"{BACKEND_URL}/api/login", headers=headers, timeout=5)
        
        cors_headers = {
            "access-control-allow-origin": response.headers.get("Access-Control-Allow-Origin"),
            "access-control-allow-methods": response.headers.get("Access-Control-Allow-Methods"),
            "access-control-allow-credentials": response.headers.get("Access-Control-Allow-Credentials")
        }
        
        if cors_headers["access-control-allow-origin"]:
            print(f"[OK] CORS is configured")
            print(f"     Allowed Origins: {cors_headers['access-control-allow-origin']}")
            print(f"     Allowed Methods: {cors_headers['access-control-allow-methods']}")
            print(f"     Allow Credentials: {cors_headers['access-control-allow-credentials']}")
            return True
        else:
            print(f"[WARN] CORS headers not found. May cause frontend connection issues.")
            return False
    except Exception as e:
        print(f"[FAIL] Error testing CORS: {e}")
        return False


def test_backend_endpoints():
    """Test key backend endpoints"""
    print("\n" + "=" * 60)
    print("Testing Backend Endpoints")
    print("=" * 60)
    
    endpoints = [
        ("/", "GET", "Root endpoint"),
        ("/api/status", "GET", "Status endpoint"),
        ("/docs", "GET", "API documentation"),
    ]
    
    results = []
    for path, method, description in endpoints:
        try:
            url = f"{BACKEND_URL}{path}"
            response = requests.request(method, url, timeout=5)
            if response.status_code < 500:
                print(f"[OK] {description}: {path} ({response.status_code})")
                results.append(True)
            else:
                print(f"[FAIL] {description}: {path} ({response.status_code})")
                results.append(False)
        except Exception as e:
            print(f"[FAIL] {description}: {path} - {e}")
            results.append(False)
    
    return all(results)


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ChatCore.AI - Backend-Frontend Connection Test")
    print("=" * 60)
    
    results = []
    
    # Test backend status
    results.append(("Backend Status", test_backend_status()))
    
    # Test CORS
    results.append(("CORS Configuration", test_cors()))
    
    # Test endpoints
    results.append(("Backend Endpoints", test_backend_endpoints()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All connection tests passed!")
        print(f"\nBackend URL: {BACKEND_URL}")
        print(f"Frontend URL: {FRONTEND_URL}")
        print(f"\nYou can now:")
        print(f"  1. Access backend API docs: {BACKEND_URL}/docs")
        print(f"  2. Access frontend: {FRONTEND_URL}")
        print(f"  3. Login with: admin / 1234")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please check:")
        print(f"  1. Is backend running? Start with: uvicorn main:app --reload")
        print(f"  2. Is frontend running? Start with: streamlit run app.py")
        print(f"  3. Check CORS settings in backend/.env")
        return 1


if __name__ == "__main__":
    exit(main())

