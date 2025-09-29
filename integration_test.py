#!/usr/bin/env python3
"""
HandyConnect Integration Test Suite
Comprehensive testing of all application components
Author: Sunayana
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any

class IntegrationTester:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_test(self, test_name: str, status: str, details: str = "", response_time: float = 0):
        """Log test result"""
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_color = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_color} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if response_time > 0:
            print(f"   Response Time: {response_time:.3f}s")
        print()
    
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, expected_status: int = 200) -> bool:
        """Test a single endpoint"""
        start_time = time.time()
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = self.session.get(url, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=10)
            else:
                response = self.session.request(method, url, json=data, timeout=10)
            
            response_time = time.time() - start_time
            
            if response.status_code == expected_status:
                self.log_test(f"{method} {endpoint}", "PASS", f"Status: {response.status_code}", response_time)
                return True
            else:
                self.log_test(f"{method} {endpoint}", "FAIL", f"Expected {expected_status}, got {response.status_code}", response_time)
                return False
                
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.log_test(f"{method} {endpoint}", "FAIL", f"Request failed: {str(e)}", response_time)
            return False
    
    def test_health_endpoints(self):
        """Test application health and basic connectivity"""
        print("🏥 Testing Health Endpoints...")
        print("=" * 50)
        
        health_tests = [
            ("/api/health", "GET", 200),
            ("/", "GET", 200),
            ("/analytics", "GET", 200),
            ("/threads", "GET", 200)
        ]
        
        for endpoint, method, expected_status in health_tests:
            self.test_endpoint(endpoint, method, expected_status=expected_status)
    
    def test_core_apis(self):
        """Test core API endpoints"""
        print("🔧 Testing Core APIs...")
        print("=" * 50)
        
        core_tests = [
            ("/api/tasks", "GET", 200),
            ("/api/threads", "GET", 200),
            ("/api/analytics/health", "GET", 200),
            ("/api/analytics/tasks", "GET", 200),
            ("/api/analytics/performance", "GET", 200)
        ]
        
        for endpoint, method, expected_status in core_tests:
            self.test_endpoint(endpoint, method, expected_status=expected_status)
    
    def test_analytics_features(self):
        """Test analytics and reporting features"""
        print("📊 Testing Analytics Features...")
        print("=" * 50)
        
        analytics_tests = [
            ("/api/analytics/report", "GET", 200),
            ("/api/analytics/user-behavior", "GET", 200),
            ("/api/analytics/system-health", "GET", 200),
            ("/api/analytics/current-metrics", "GET", 200),
            ("/api/analytics/charts", "GET", 200),
            ("/api/analytics/charts/task-status", "GET", 200),
            ("/api/analytics/charts/priority-distribution", "GET", 200),
            ("/api/analytics/charts/response-time-trend", "GET", 200)
        ]
        
        for endpoint, method, expected_status in analytics_tests:
            self.test_endpoint(endpoint, method, expected_status=expected_status)
    
    def test_realtime_features(self):
        """Test real-time dashboard features"""
        print("⚡ Testing Real-time Features...")
        print("=" * 50)
        
        realtime_tests = [
            ("/api/realtime/dashboard/live", "GET", 200),
            ("/api/realtime/performance/stats", "GET", 200),
            ("/api/realtime/dashboard/stream", "GET", 200)
        ]
        
        for endpoint, method, expected_status in realtime_tests:
            self.test_endpoint(endpoint, method, expected_status=expected_status)
    
    def test_data_operations(self):
        """Test data collection and export operations"""
        print("💾 Testing Data Operations...")
        print("=" * 50)
        
        # Test data collection
        test_task_data = {
            "task_id": "test_task_001",
            "title": "Integration Test Task",
            "status": "completed",
            "priority": "medium",
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat()
        }
        
        self.test_endpoint("/api/analytics/collect/task", "POST", test_task_data, 201)
        
        # Test user behavior collection
        test_behavior_data = {
            "user_id": "test_user_001",
            "session_id": "test_session_001",
            "action": "page_view",
            "page": "/analytics",
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_endpoint("/api/analytics/collect/user-behavior", "POST", test_behavior_data, 201)
        
        # Test data export
        export_data = {
            "data_type": "tasks",
            "format": "json"
        }
        
        self.test_endpoint("/api/analytics/admin/export", "POST", export_data, 200)
    
    def test_admin_features(self):
        """Test admin and utility features"""
        print("🔧 Testing Admin Features...")
        print("=" * 50)
        
        admin_tests = [
            ("/api/analytics/admin/storage-stats", "GET", 200),
            ("/api/analytics/metrics/summary", "GET", 200)
        ]
        
        for endpoint, method, expected_status in admin_tests:
            self.test_endpoint(endpoint, method, expected_status=expected_status)
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("🚨 Testing Error Handling...")
        print("=" * 50)
        
        error_tests = [
            ("/api/nonexistent", "GET", 404),
            ("/api/analytics/invalid-endpoint", "GET", 404)
        ]
        
        for endpoint, method, expected_status in error_tests:
            self.test_endpoint(endpoint, method, expected_status=expected_status)
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("📋 Generating Test Report...")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        print(f"🎯 INTEGRATION TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total Duration: {total_duration:.2f}s")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
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
                'test_start': self.start_time.isoformat(),
                'test_end': end_time.isoformat()
            },
            'test_results': self.test_results
        }
        
        with open('integration_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Detailed report saved to: integration_test_report.json")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting HandyConnect Integration Tests")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            self.test_health_endpoints()
            self.test_core_apis()
            self.test_analytics_features()
            self.test_realtime_features()
            self.test_data_operations()
            self.test_admin_features()
            self.test_error_handling()
            
            success = self.generate_report()
            
            if success:
                print("🎉 ALL INTEGRATION TESTS PASSED!")
                return True
            else:
                print("⚠️ SOME INTEGRATION TESTS FAILED!")
                return False
                
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n💥 Test suite failed with error: {e}")
            return False

if __name__ == "__main__":
    tester = IntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
