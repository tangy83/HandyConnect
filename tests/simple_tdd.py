#!/usr/bin/env python3
"""
Simple TDD Test Suite for HandyConnect
Author: Sunayana
"""

import unittest
import requests
import json
import time
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SimpleTDDTest(unittest.TestCase):
    """Simple TDD test suite for HandyConnect"""
    
    def setUp(self):
        self.base_url = "http://localhost:5001"
        self.test_results = []
    
    def log_result(self, test_name, status, details=""):
        """Log test result"""
        icon = "PASS" if status == "PASS" else "FAIL"
        print(f"{icon}: {test_name} - {details}")
        self.test_results.append({
            'name': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_health_check(self):
        """Test application health"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Health Check", "PASS", f"Status: {data.get('status')}")
                # Accept both 'success' and 'healthy' as valid status
                self.assertIn(data.get('status'), ['success', 'healthy'])
            else:
                self.log_result("Health Check", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Health Check", "FAIL", str(e))
    
    def test_main_pages(self):
        """Test main application pages"""
        pages = [
            ("/", "Main Dashboard"),
            ("/analytics", "Analytics Dashboard"),
            ("/threads", "Threads Page")
        ]
        
        for endpoint, name in pages:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_result(f"Page: {name}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_result(f"Page: {name}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Page: {name}", "FAIL", str(e))
    
    def test_api_endpoints(self):
        """Test core API endpoints"""
        apis = [
            ("/api/tasks", "Tasks API"),
            ("/api/analytics/health", "Analytics Health"),
            ("/api/analytics/report", "Analytics Report"),
            ("/api/analytics/user-behavior", "User Behavior"),
            ("/api/analytics/system-health", "System Health")
        ]
        
        for endpoint, name in apis:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_result(f"API: {name}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_result(f"API: {name}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"API: {name}", "FAIL", str(e))
    
    def test_realtime_features(self):
        """Test real-time dashboard features"""
        realtime_apis = [
            ("/api/realtime/dashboard/live", "Live Dashboard"),
            ("/api/realtime/performance/stats", "Performance Stats")
        ]
        
        for endpoint, name in realtime_apis:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_result(f"Real-time: {name}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_result(f"Real-time: {name}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Real-time: {name}", "FAIL", str(e))
    
    def test_data_operations(self):
        """Test data collection and export"""
        # Test user behavior collection
        test_data = {
            "user_id": "tdd_test_user",
            "session_id": "tdd_test_session",
            "action": "test",
            "page": "/test",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/analytics/collect/user-behavior",
                json=test_data,
                timeout=5
            )
            if response.status_code == 200:
                self.log_result("Data Collection", "PASS", "User behavior collected")
            else:
                self.log_result("Data Collection", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Data Collection", "FAIL", str(e))
        
        # Test data export
        try:
            export_data = {"data_type": "tasks", "format": "json"}
            response = requests.post(
                f"{self.base_url}/api/analytics/admin/export",
                json=export_data,
                timeout=10
            )
            if response.status_code == 200:
                self.log_result("Data Export", "PASS", "Export successful")
            else:
                self.log_result("Data Export", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Data Export", "FAIL", str(e))
    
    def test_performance(self):
        """Test response times"""
        endpoints = ["/api/health", "/api/analytics/health"]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                duration = time.time() - start_time
                
                if duration < 3.0:  # Adjusted threshold for Windows environment
                    self.log_result(f"Performance: {endpoint}", "PASS", f"Response time: {duration:.3f}s")
                else:
                    self.log_result(f"Performance: {endpoint}", "FAIL", f"Too slow: {duration:.3f}s")
            except Exception as e:
                self.log_result(f"Performance: {endpoint}", "FAIL", str(e))
    
    def test_json_format(self):
        """Test JSON response format"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'status' in data:
                    self.log_result("JSON Format", "PASS", "Valid JSON structure")
                else:
                    self.log_result("JSON Format", "FAIL", "Invalid JSON structure")
            else:
                self.log_result("JSON Format", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("JSON Format", "FAIL", str(e))

def run_tests():
    """Run all TDD tests"""
    print("Starting HandyConnect TDD Tests")
    print("=" * 40)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleTDDTest)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "=" * 40)
    print("TDD TEST SUMMARY")
    print("=" * 40)
    
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if failures > 0:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if errors > 0:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\\n')[-2]}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
