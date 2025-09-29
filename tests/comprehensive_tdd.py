#!/usr/bin/env python3
"""
Comprehensive Test-Driven Development Framework for HandyConnect
Author: Sunayana
Purpose: Complete TDD testing for entire application
"""

import unittest
import requests
import json
import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class HandyConnectTDDTestSuite(unittest.TestCase):
    """Comprehensive TDD test suite for HandyConnect application"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.base_url = "http://localhost:5001"
        cls.test_results = []
        cls.start_time = datetime.now()
        print(f"\n🧪 Starting HandyConnect TDD Test Suite at {cls.start_time}")
        print("=" * 60)
    
    @classmethod
    def tearDownClass(cls):
        """Generate final test report"""
        cls.generate_test_report()
    
    def log_test_result(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """Log individual test result"""
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def test_application_health(self):
        """Test 1: Application Health and Basic Connectivity"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result("Application Health", "PASS", 
                    f"Status: {data.get('status')}, Service: {data.get('data', {}).get('service')}", duration)
                self.assertEqual(data.get('status'), 'success')
            else:
                self.log_test_result("Application Health", "FAIL", 
                    f"Expected 200, got {response.status_code}", duration)
                self.fail(f"Health check failed with status {response.status_code}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Application Health", "FAIL", str(e), duration)
            self.fail(f"Health check failed: {e}")
    
    def test_core_api_endpoints(self):
        """Test 2: Core API Endpoints Functionality"""
        endpoints = [
            ("/", "Main Dashboard", 200),
            ("/analytics", "Analytics Dashboard", 200),
            ("/threads", "Threads Page", 200),
            ("/api/tasks", "Tasks API", 200),
            ("/api/analytics/health", "Analytics Health", 200)
        ]
        
        for endpoint, name, expected_status in endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                duration = time.time() - start_time
                
                if response.status_code == expected_status:
                    self.log_test_result(f"Core API: {name}", "PASS", 
                        f"Status: {response.status_code}", duration)
                else:
                    self.log_test_result(f"Core API: {name}", "FAIL", 
                        f"Expected {expected_status}, got {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result(f"Core API: {name}", "FAIL", str(e), duration)
    
    def test_analytics_endpoints(self):
        """Test 3: Analytics and Reporting Endpoints"""
        analytics_endpoints = [
            ("/api/analytics/report", "Analytics Report"),
            ("/api/analytics/tasks", "Task Analytics"),
            ("/api/analytics/user-behavior", "User Behavior"),
            ("/api/analytics/system-health", "System Health"),
            ("/api/analytics/current-metrics", "Current Metrics"),
            ("/api/analytics/charts", "Charts Data")
        ]
        
        for endpoint, name in analytics_endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_test_result(f"Analytics: {name}", "PASS", 
                        f"Status: {response.status_code}", duration)
                else:
                    self.log_test_result(f"Analytics: {name}", "FAIL", 
                        f"Expected 200, got {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result(f"Analytics: {name}", "FAIL", str(e), duration)
    
    def test_realtime_dashboard(self):
        """Test 4: Real-time Dashboard Features"""
        realtime_endpoints = [
            ("/api/realtime/dashboard/live", "Live Dashboard"),
            ("/api/realtime/performance/stats", "Performance Stats"),
            ("/api/realtime/dashboard/stream", "SSE Stream")
        ]
        
        for endpoint, name in realtime_endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_test_result(f"Real-time: {name}", "PASS", 
                        f"Status: {response.status_code}", duration)
                else:
                    self.log_test_result(f"Real-time: {name}", "FAIL", 
                        f"Expected 200, got {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result(f"Real-time: {name}", "FAIL", str(e), duration)
    
    def test_data_operations(self):
        """Test 5: Data Collection and Export Operations"""
        # Test data collection
        test_data = {
            "user_id": "test_user_tdd",
            "session_id": "test_session_tdd",
            "action": "test_action",
            "page": "/test",
            "timestamp": datetime.now().isoformat()
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/analytics/collect/user-behavior",
                json=test_data,
                timeout=5
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test_result("Data Collection", "PASS", 
                    "User behavior data collected", duration)
            else:
                self.log_test_result("Data Collection", "FAIL", 
                    f"Expected 200, got {response.status_code}", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Data Collection", "FAIL", str(e), duration)
        
        # Test data export
        start_time = time.time()
        try:
            export_data = {"data_type": "tasks", "format": "json"}
            response = requests.post(
                f"{self.base_url}/api/analytics/admin/export",
                json=export_data,
                timeout=10
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test_result("Data Export", "PASS", 
                    "Data export successful", duration)
            else:
                self.log_test_result("Data Export", "FAIL", 
                    f"Expected 200, got {response.status_code}", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Data Export", "FAIL", str(e), duration)
    
    def test_performance_metrics(self):
        """Test 6: Performance and Response Time Testing"""
        endpoints = [
            "/api/health",
            "/api/analytics/health",
            "/api/realtime/performance/stats"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                duration = time.time() - start_time
                
                if duration < 2.0:  # Performance threshold
                    self.log_test_result(f"Performance: {endpoint}", "PASS", 
                        f"Response time: {duration:.3f}s", duration)
                else:
                    self.log_test_result(f"Performance: {endpoint}", "FAIL", 
                        f"Response time too slow: {duration:.3f}s", duration)
                        
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result(f"Performance: {endpoint}", "FAIL", str(e), duration)
    
    def test_error_handling(self):
        """Test 7: Error Handling and Edge Cases"""
        # Test 404 endpoints
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/api/nonexistent", timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 404:
                self.log_test_result("Error Handling: 404", "PASS", 
                    "Correctly returns 404 for non-existent endpoint", duration)
            else:
                self.log_test_result("Error Handling: 404", "FAIL", 
                    f"Expected 404, got {response.status_code}", duration)
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Error Handling: 404", "FAIL", str(e), duration)
    
    def test_json_response_format(self):
        """Test 8: JSON Response Format Validation"""
        endpoints = [
            "/api/health",
            "/api/analytics/report",
            "/api/analytics/user-behavior"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and 'status' in data:
                            self.log_test_result(f"JSON Format: {endpoint}", "PASS", 
                                "Valid JSON with status field", duration)
                        else:
                            self.log_test_result(f"JSON Format: {endpoint}", "FAIL", 
                                "Invalid JSON structure", duration)
                    except json.JSONDecodeError:
                        self.log_test_result(f"JSON Format: {endpoint}", "FAIL", 
                            "Invalid JSON response", duration)
                else:
                    self.log_test_result(f"JSON Format: {endpoint}", "FAIL", 
                        f"HTTP {response.status_code}", duration)
                        
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result(f"JSON Format: {endpoint}", "FAIL", str(e), duration)
    
    @classmethod
    def generate_test_report(cls):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TDD TEST REPORT SUMMARY")
        print("=" * 60)
        
        total_tests = len(cls.test_results)
        passed_tests = len([r for r in cls.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in cls.test_results if r['status'] == 'FAIL'])
        
        end_time = datetime.now()
        total_duration = (end_time - cls.start_time).total_seconds()
        
        print(f"🎯 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"⏱️ Total Duration: {total_duration:.2f}s")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in cls.test_results:
                if result['status'] == 'FAIL':
                    print(f"   - {result['test_name']}: {result['details']}")
            print()
        
        # Save detailed report
        report_data = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests/total_tests)*100,
                'total_duration': total_duration,
                'test_start': cls.start_time.isoformat(),
                'test_end': end_time.isoformat()
            },
            'test_results': cls.test_results
        }
        
        with open('tdd_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Detailed report saved to: tdd_test_report.json")
        
        if passed_tests == total_tests:
            print("🎉 ALL TDD TESTS PASSED!")
            return True
        else:
            print("⚠️ SOME TDD TESTS FAILED!")
            return False

def run_tdd_tests():
    """Run the complete TDD test suite"""
    print("🚀 Starting HandyConnect TDD Test Suite")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(HandyConnectTDDTestSuite)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tdd_tests()
    sys.exit(0 if success else 1)
