#!/usr/bin/env python3
"""
Comprehensive Test Runner for HandyConnect Application
Simplified test runner that works without external dependencies
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from io import StringIO

def test_application_health():
    """Test basic application health"""
    print("Testing Application Health...")
    
    try:
        # Test if application is running
        response = requests.get("http://localhost:5001/api/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Application Health: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"[FAIL] Application Health: Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[FAIL] Application Health: Connection failed - Application not running")
        return False
    except Exception as e:
        print(f"[FAIL] Application Health: Error - {e}")
        return False

def test_core_api_endpoints():
    """Test core API endpoints"""
    print("\nTesting Core API Endpoints...")
    
    endpoints = [
        ("/api/health", "Health Check"),
        ("/api/tasks", "Tasks List"),
        ("/", "Main Dashboard")
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:5001{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"[PASS] {description}: Status {response.status_code}")
                results.append(True)
            else:
                print(f"[WARN] {description}: Status {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"[FAIL] {description}: Error - {e}")
            results.append(False)
    
    return results

def test_analytics_endpoints():
    """Test analytics endpoints"""
    print("\nTesting Analytics Endpoints...")
    
    endpoints = [
        ("/api/analytics/dashboard", "Analytics Dashboard"),
        ("/api/analytics/reports/summary", "Summary Report"),
        ("/api/analytics/reports/performance", "Performance Report"),
        ("/api/analytics/reports/trends", "Trends Report"),
        ("/api/analytics/reports/categories", "Categories Report")
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:5001{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {description}: Status {response.status_code}")
                results.append(True)
            elif response.status_code == 404:
                print(f"⚠️ {description}: Not implemented (404)")
                results.append(False)
            else:
                print(f"⚠️ {description}: Status {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
            results.append(False)
    
    return results

def test_realtime_endpoints():
    """Test real-time endpoints"""
    print("\nTesting Real-time Endpoints...")
    
    endpoints = [
        ("/api/realtime/dashboard/live", "Live Dashboard"),
        ("/api/realtime/dashboard/metrics", "Real-time Metrics"),
        ("/api/realtime/dashboard/alerts", "Real-time Alerts"),
        ("/api/realtime/dashboard/stream", "SSE Stream")
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:5001{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {description}: Status {response.status_code}")
                results.append(True)
            elif response.status_code == 404:
                print(f"⚠️ {description}: Not implemented (404)")
                results.append(False)
            else:
                print(f"⚠️ {description}: Status {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
            results.append(False)
    
    return results

def test_sse_endpoint_detailed():
    """Test SSE endpoint in detail"""
    print("\nTesting SSE Endpoint in Detail...")
    
    try:
        response = requests.get("http://localhost:5001/api/realtime/dashboard/stream", 
                              timeout=10, stream=True)
        
        if response.status_code == 200:
            print(f"✅ SSE Endpoint: Status {response.status_code}")
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'text/event-stream' in content_type:
                print(f"✅ SSE Content-Type: {content_type}")
            else:
                print(f"⚠️ SSE Content-Type: {content_type} (expected text/event-stream)")
            
            # Try to read some SSE data
            try:
                sse_data = []
                for line in response.iter_lines(decode_unicode=True):
                    if line and line.startswith('data:'):
                        sse_data.append(line)
                        if len(sse_data) >= 2:  # Read first 2 messages
                            break
                
                if sse_data:
                    print(f"✅ SSE Data: Received {len(sse_data)} messages")
                    return True
                else:
                    print("⚠️ SSE Data: No messages received")
                    return False
                    
            except Exception as e:
                print(f"⚠️ SSE Data: Error reading stream - {e}")
                return False
        else:
            print(f"❌ SSE Endpoint: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SSE Endpoint: Error - {e}")
        return False

def test_performance():
    """Test basic performance metrics"""
    print("\nTesting Performance...")
    
    endpoints_to_test = [
        "/api/health",
        "/api/tasks"
    ]
    
    results = []
    
    for endpoint in endpoints_to_test:
        try:
            start_time = time.time()
            response = requests.get(f"http://localhost:5001{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                if response_time < 1000:  # Less than 1 second
                    print(f"✅ {endpoint}: {response_time:.2f}ms (Excellent)")
                    results.append(True)
                elif response_time < 3000:  # Less than 3 seconds
                    print(f"✅ {endpoint}: {response_time:.2f}ms (Good)")
                    results.append(True)
                else:
                    print(f"⚠️ {endpoint}: {response_time:.2f}ms (Slow)")
                    results.append(False)
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
            results.append(False)
    
    return results

def test_error_handling():
    """Test error handling"""
    print("\nTesting Error Handling...")
    
    # Test 404 handling
    try:
        response = requests.get("http://localhost:5001/api/nonexistent", timeout=10)
        if response.status_code == 404:
            print("✅ 404 Error Handling: Correctly returns 404")
            return True
        else:
            print(f"⚠️ 404 Error Handling: Returns {response.status_code} instead of 404")
            return False
    except Exception as e:
        print(f"❌ 404 Error Handling: Error - {e}")
        return False

def test_phase12_features():
    """Test Phase 12 features if available"""
    print("\nTesting Phase 12 Features...")
    
    # Test mobile optimization by checking if mobile CSS is included
    try:
        response = requests.get("http://localhost:5001/", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Check for mobile optimization
            mobile_features = [
                "mobile-optimization.css",
                "mobile-optimization.js",
                "viewport"
            ]
            
            found_features = []
            for feature in mobile_features:
                if feature in content:
                    found_features.append(feature)
            
            if found_features:
                print(f"✅ Mobile Optimization: Found {len(found_features)} features")
                return True
            else:
                print("⚠️ Mobile Optimization: No mobile features detected")
                return False
        else:
            print(f"❌ Mobile Optimization: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Mobile Optimization: Error - {e}")
        return False

def generate_test_report(results):
    """Generate comprehensive test report"""
    print(f"\n{'='*60}")
    print("COMPREHENSIVE TEST REPORT")
    print(f"{'='*60}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Application: HandyConnect")
    print(f"Test Type: Integration Testing")
    print(f"{'='*60}")
    
    total_tests = sum(len(result) for result in results.values() if isinstance(result, list))
    passed_tests = sum(sum(result) for result in results.values() if isinstance(result, list))
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
    
    print(f"\n{'='*60}")
    print("DETAILED RESULTS")
    print(f"{'='*60}")
    
    for category, result in results.items():
        if isinstance(result, bool):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{category}: {status}")
        elif isinstance(result, list):
            passed = sum(result)
            total = len(result)
            status = "✅ PASS" if passed == total else "⚠️ PARTIAL" if passed > 0 else "❌ FAIL"
            print(f"{category}: {status} ({passed}/{total})")
    
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS")
    print(f"{'='*60}")
    
    if results.get('application_health', False):
        print("✅ Application is running and healthy")
    else:
        print("❌ Application health issues detected - check if app is running")
    
    if results.get('sse_endpoint', False):
        print("✅ Real-time features are working")
    else:
        print("⚠️ Real-time features need attention")
    
    if results.get('performance', [False]):
        print("⚠️ Performance optimization recommended")
    else:
        print("✅ Performance is acceptable")
    
    print(f"\n{'='*60}")

def main():
    """Main test execution function"""
    print("HandyConnect Comprehensive Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run all tests
    results = {}
    
    # Test application health
    results['application_health'] = test_application_health()
    
    # Test core API endpoints
    results['core_endpoints'] = test_core_api_endpoints()
    
    # Test analytics endpoints
    results['analytics_endpoints'] = test_analytics_endpoints()
    
    # Test real-time endpoints
    results['realtime_endpoints'] = test_realtime_endpoints()
    
    # Test SSE endpoint in detail
    results['sse_endpoint'] = test_sse_endpoint_detailed()
    
    # Test performance
    results['performance'] = test_performance()
    
    # Test error handling
    results['error_handling'] = test_error_handling()
    
    # Test Phase 12 features
    results['phase12_features'] = test_phase12_features()
    
    # Generate comprehensive report
    generate_test_report(results)
    
    # Determine overall success
    all_core_passed = results.get('application_health', False) and results.get('core_endpoints', [False])
    if isinstance(all_core_passed, list):
        all_core_passed = all(all_core_passed)
    
    if all_core_passed:
        print("\n🎉 OVERALL RESULT: TESTS PASSED - Application is functioning correctly!")
        return 0
    else:
        print("\n⚠️ OVERALL RESULT: SOME TESTS FAILED - Review issues above")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
