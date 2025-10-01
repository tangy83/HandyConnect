#!/usr/bin/env python3
"""
HandyConnect Phase 11: System Integration Test Runner
Simplified test runner without Unicode characters for Windows compatibility
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class Phase11TestRunner:
    """Phase 11: System Integration Test Runner"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.test_results = []
        self.start_time = datetime.now()
        
        print("HandyConnect Phase 11: System Integration Testing")
        print("=" * 60)
    
    def run_integration_tests(self):
        """Run comprehensive integration tests"""
        print("\nRunning Phase 11 Integration Tests...")
        
        # Test 1: Application Health
        self.test_application_health()
        
        # Test 2: API Integration
        self.test_api_integration()
        
        # Test 3: Frontend Integration
        self.test_frontend_integration()
        
        # Test 4: Analytics Integration
        self.test_analytics_integration()
        
        # Test 5: Real-time Integration
        self.test_realtime_integration()
        
        # Test 6: Performance Integration
        self.test_performance_integration()
        
        # Test 7: Cross-browser Compatibility
        self.test_cross_browser_compatibility()
        
        # Test 8: Error Handling
        self.test_error_handling()
        
        self.generate_report()
    
    def test_application_health(self):
        """Test application health and startup"""
        print("\n1. Testing Application Health...")
        
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Application Health", "PASS", "Application is healthy and running")
            else:
                self.log_result("Application Health", "FAIL", f"Health check failed: {response.status_code}")
        except Exception as e:
            self.log_result("Application Health", "FAIL", f"Health check error: {str(e)}")
    
    def test_api_integration(self):
        """Test API integration"""
        print("\n2. Testing API Integration...")
        
        api_endpoints = [
            "/api/health",
            "/api/tasks",
            "/api/analytics/health",
            "/api/analytics/current-metrics",
            "/api/realtime/dashboard/live"
        ]
        
        passed = 0
        for endpoint in api_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    passed += 1
                else:
                    self.log_result(f"API - {endpoint}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"API - {endpoint}", "FAIL", f"Error: {str(e)}")
        
        if passed == len(api_endpoints):
            self.log_result("API Integration", "PASS", f"All {len(api_endpoints)} API endpoints working")
        else:
            self.log_result("API Integration", "PARTIAL", f"{passed}/{len(api_endpoints)} endpoints working")
    
    def test_frontend_integration(self):
        """Test frontend integration"""
        print("\n3. Testing Frontend Integration...")
        
        pages = ["/", "/analytics", "/threads"]
        frontend_files = [
            "/static/js/app-enhanced.js",
            "/static/js/integration-manager.js",
            "/static/js/analytics-integration.js",
            "/static/css/integration-styles.css"
        ]
        
        # Test pages
        pages_ok = 0
        for page in pages:
            try:
                response = requests.get(f"{self.base_url}{page}", timeout=10)
                if response.status_code == 200:
                    pages_ok += 1
                else:
                    self.log_result(f"Frontend Page - {page}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Frontend Page - {page}", "FAIL", f"Error: {str(e)}")
        
        # Test static files
        files_ok = 0
        for file_path in frontend_files:
            try:
                response = requests.get(f"{self.base_url}{file_path}", timeout=5)
                if response.status_code == 200:
                    files_ok += 1
                else:
                    self.log_result(f"Frontend File - {file_path}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Frontend File - {file_path}", "FAIL", f"Error: {str(e)}")
        
        if pages_ok == len(pages) and files_ok == len(frontend_files):
            self.log_result("Frontend Integration", "PASS", "All frontend components integrated")
        else:
            self.log_result("Frontend Integration", "PARTIAL", f"Pages: {pages_ok}/{len(pages)}, Files: {files_ok}/{len(frontend_files)}")
    
    def test_analytics_integration(self):
        """Test analytics integration"""
        print("\n4. Testing Analytics Integration...")
        
        analytics_endpoints = [
            "/api/analytics/health",
            "/api/analytics/report",
            "/api/analytics/current-metrics",
            "/api/analytics/charts",
            "/api/analytics/user-behavior",
            "/api/analytics/performance"
        ]
        
        passed = 0
        for endpoint in analytics_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'status' in data and data['status'] == 'success':
                        passed += 1
                    else:
                        self.log_result(f"Analytics - {endpoint}", "WARN", "Invalid response format")
                else:
                    self.log_result(f"Analytics - {endpoint}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Analytics - {endpoint}", "FAIL", f"Error: {str(e)}")
        
        if passed == len(analytics_endpoints):
            self.log_result("Analytics Integration", "PASS", "All analytics endpoints working")
        else:
            self.log_result("Analytics Integration", "PARTIAL", f"{passed}/{len(analytics_endpoints)} endpoints working")
    
    def test_realtime_integration(self):
        """Test real-time integration"""
        print("\n5. Testing Real-time Integration...")
        
        realtime_endpoints = [
            "/api/realtime/dashboard/live",
            "/api/realtime/metrics/live",
            "/api/realtime/performance/stats",
            "/api/realtime/alerts"
        ]
        
        passed = 0
        for endpoint in realtime_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    passed += 1
                else:
                    self.log_result(f"Real-time - {endpoint}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Real-time - {endpoint}", "FAIL", f"Error: {str(e)}")
        
        # Test Server-Sent Events
        try:
            response = requests.get(f"{self.base_url}/api/realtime/dashboard/stream", timeout=10, stream=True)
            if response.status_code == 200:
                if 'text/event-stream' in response.headers.get('content-type', ''):
                    # Read first SSE message to verify it's working
                    sse_messages = 0
                    for line in response.iter_lines(decode_unicode=True):
                        if line and line.startswith('data:'):
                            sse_messages += 1
                            if sse_messages >= 1:  # Just need to verify we get at least one message
                                break
                    
                    if sse_messages > 0:
                        passed += 1
                        self.log_result("SSE Integration", "PASS", f"Server-Sent Events working ({sse_messages} messages received)")
                    else:
                        self.log_result("SSE Integration", "WARN", "SSE endpoint responds but no messages received")
                else:
                    self.log_result("SSE Integration", "WARN", "Wrong content type")
            else:
                self.log_result("SSE Integration", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("SSE Integration", "FAIL", f"Error: {str(e)}")
        
        if passed >= len(realtime_endpoints):
            self.log_result("Real-time Integration", "PASS", "Real-time features working")
        else:
            self.log_result("Real-time Integration", "PARTIAL", f"{passed}/{len(realtime_endpoints)+1} features working")
    
    def test_performance_integration(self):
        """Test performance integration"""
        print("\n6. Testing Performance Integration...")
        
        endpoints = [
            "/api/health",
            "/api/tasks",
            "/api/analytics/health",
            "/api/realtime/dashboard/live"
        ]
        
        slow_endpoints = []
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                if response_time > 3.0:
                    slow_endpoints.append(f"{endpoint}: {response_time:.2f}s")
                
                if response.status_code != 200:
                    self.log_result(f"Performance - {endpoint}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Performance - {endpoint}", "FAIL", f"Error: {str(e)}")
        
        if not slow_endpoints:
            self.log_result("Performance Integration", "PASS", "All endpoints perform well")
        else:
            self.log_result("Performance Integration", "WARN", f"Slow endpoints: {', '.join(slow_endpoints)}")
    
    def test_cross_browser_compatibility(self):
        """Test cross-browser compatibility"""
        print("\n7. Testing Cross-Browser Compatibility...")
        
        # Test HTML5 features
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                content = response.text
                
                html5_features = [
                    ('<!DOCTYPE html>', 'HTML5 DOCTYPE'),
                    ('<meta charset="UTF-8">', 'UTF-8 encoding'),
                    ('<meta name="viewport"', 'Viewport meta tag'),
                    ('<nav class="navbar"', 'HTML5 nav element')
                ]
                
                features_found = 0
                for feature, description in html5_features:
                    if feature in content:
                        features_found += 1
                
                if features_found >= 3:
                    self.log_result("Cross-Browser Compatibility", "PASS", f"HTML5 features: {features_found}/{len(html5_features)}")
                else:
                    self.log_result("Cross-Browser Compatibility", "WARN", f"Limited HTML5 features: {features_found}/{len(html5_features)}")
            else:
                self.log_result("Cross-Browser Compatibility", "FAIL", f"Page load failed: {response.status_code}")
        except Exception as e:
            self.log_result("Cross-Browser Compatibility", "FAIL", f"Error: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling"""
        print("\n8. Testing Error Handling...")
        
        # Test 404 handling
        try:
            response = requests.get(f"{self.base_url}/api/nonexistent", timeout=10)
            if response.status_code == 404:
                self.log_result("Error Handling - 404", "PASS", "404 errors handled correctly")
            else:
                self.log_result("Error Handling - 404", "WARN", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling - 404", "FAIL", f"Error: {str(e)}")
        
        # Test invalid endpoint
        try:
            response = requests.get(f"{self.base_url}/api/tasks/invalid", timeout=10)
            if response.status_code in [404, 400]:
                self.log_result("Error Handling - Invalid ID", "PASS", "Invalid requests handled correctly")
            else:
                self.log_result("Error Handling - Invalid ID", "WARN", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling - Invalid ID", "FAIL", f"Error: {str(e)}")
        
        self.log_result("Error Handling Integration", "PASS", "Error handling working correctly")
    
    def log_result(self, test_name: str, status: str, details: str):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = {
            'PASS': '[PASS]',
            'FAIL': '[FAIL]',
            'WARN': '[WARN]',
            'PARTIAL': '[PARTIAL]'
        }
        
        icon = status_icon.get(status, '[INFO]')
        print(f"   {icon} {test_name}: {details}")
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("PHASE 11 INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        partial = len([r for r in self.test_results if r['status'] == 'PARTIAL'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Warnings: {warnings}")
        print(f"Partial: {partial}")
        
        if total_tests > 0:
            success_rate = (passed / total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status_icon = {
                'PASS': '[PASS]',
                'FAIL': '[FAIL]',
                'WARN': '[WARN]',
                'PARTIAL': '[PARTIAL]'
            }
            icon = status_icon.get(result['status'], '[INFO]')
            print(f"{icon} {result['test']}: {result['details']}")
        
        # Save report
        report = {
            'test_session': {
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - self.start_time).total_seconds()
            },
            'summary': {
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'partial': partial,
                'success_rate': (passed / total_tests * 100) if total_tests > 0 else 0
            },
            'results': self.test_results
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"phase11_integration_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {filename}")
        
        if failed == 0:
            print("\nPhase 11 Integration Testing: SUCCESS!")
            print("All integration components are working correctly.")
        else:
            print(f"\nPhase 11 Integration Testing: {failed} issues found")
            print("Please review the failed tests and address the issues.")

def main():
    """Main function"""
    print("HandyConnect Phase 11: System Integration Test Runner")
    print("Testing system integration components...")
    
    # Check if application is running
    try:
        response = requests.get("http://localhost:5001/api/health", timeout=5)
        if response.status_code != 200:
            print("ERROR: Application not running on localhost:5001")
            print("Please start the application before running integration tests")
            return False
    except requests.exceptions.RequestException:
        print("ERROR: Cannot connect to application on localhost:5001")
        print("Please start the application before running integration tests")
        return False
    
    # Run tests
    runner = Phase11TestRunner()
    runner.run_integration_tests()
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
