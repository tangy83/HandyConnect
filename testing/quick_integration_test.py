#!/usr/bin/env python3
"""
Quick Integration Test for HandyConnect
Focused testing of critical endpoints
"""

import requests
import time
import sys

def test_endpoint(url, method="GET", timeout=5):
    """Quick endpoint test"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def main():
    base_url = "http://localhost:5001"
    print("🚀 Quick Integration Test for HandyConnect")
    print("=" * 50)
    
    # Wait for app to start
    print("⏳ Waiting for application to start...")
    time.sleep(3)
    
    tests = [
        ("Health Check", f"{base_url}/api/health"),
        ("Main Page", f"{base_url}/"),
        ("Analytics Dashboard", f"{base_url}/analytics"),
        ("Tasks API", f"{base_url}/api/tasks"),
        ("Analytics API", f"{base_url}/api/analytics/health"),
        ("Real-time Dashboard", f"{base_url}/api/realtime/dashboard/live"),
        ("Performance Stats", f"{base_url}/api/realtime/performance/stats"),
        ("User Behavior", f"{base_url}/api/analytics/user-behavior"),
        ("System Health", f"{base_url}/api/analytics/system-health"),
        ("Export Function", f"{base_url}/api/analytics/admin/export")
    ]
    
    passed = 0
    failed = 0
    
    for test_name, url in tests:
        print(f"Testing {test_name}...", end=" ")
        if test_endpoint(url):
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    print(f"Success Rate: {(passed/(passed+failed))*100:.1f}%")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print("⚠️ SOME TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
