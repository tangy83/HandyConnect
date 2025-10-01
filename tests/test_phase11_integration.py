"""
HandyConnect Phase 11: System Integration Tests
Comprehensive end-to-end workflow testing and integration validation
"""

import unittest
import requests
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import threading
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Phase11IntegrationTests(unittest.TestCase):
    """Phase 11: System Integration Test Suite"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.base_url = "http://localhost:5001"
        cls.test_results = []
        cls.start_time = datetime.now()
        
        # Initialize WebDriver for browser testing
        cls.driver = None
        cls.setup_selenium()
        
        print(f"\n🚀 Starting Phase 11 System Integration Tests at {cls.start_time}")
        print("=" * 80)
    
    @classmethod
    def setup_selenium(cls):
        """Set up Selenium WebDriver for browser testing"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.wait = WebDriverWait(cls.driver, 10)
            print("✅ Selenium WebDriver initialized")
            
        except WebDriverException as e:
            print(f"⚠️ Selenium WebDriver not available: {e}")
            print("   Browser testing will be skipped")
            cls.driver = None
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if cls.driver:
            cls.driver.quit()
        
        end_time = datetime.now()
        duration = end_time - cls.start_time
        
        print("\n" + "=" * 80)
        print(f"🏁 Phase 11 Integration Tests Completed in {duration}")
        print(f"📊 Total Tests: {len(cls.test_results)}")
        
        passed = sum(1 for result in cls.test_results if result['status'] == 'PASS')
        failed = len(cls.test_results) - passed
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/len(cls.test_results)*100):.1f}%")
        
        # Generate detailed report
        cls.generate_integration_report()
    
    def log_test_result(self, test_name, status, details="", duration=0):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status} ({duration:.2f}s)")
        if details:
            print(f"   Details: {details}")
    
    def test_application_startup_integration(self):
        """Test 1: Application startup and service integration"""
        start_time = time.time()
        
        try:
            # Test main application health
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            health_data = response.json()
            self.assertIn('status', health_data)
            self.assertEqual(health_data['status'], 'healthy')
            
            # Test analytics service integration
            analytics_response = requests.get(f"{self.base_url}/api/analytics/health", timeout=10)
            self.assertEqual(analytics_response.status_code, 200)
            
            # Test real-time dashboard integration
            realtime_response = requests.get(f"{self.base_url}/api/realtime/dashboard/live", timeout=10)
            self.assertEqual(realtime_response.status_code, 200)
            
            duration = time.time() - start_time
            self.log_test_result("Application Startup Integration", "PASS", 
                               "All services started and integrated successfully", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Application Startup Integration", "FAIL", 
                               f"Service integration failed: {str(e)}", duration)
            self.fail(f"Application startup integration failed: {e}")
    
    def test_frontend_backend_api_integration(self):
        """Test 2: Frontend-Backend API integration"""
        start_time = time.time()
        
        try:
            # Test task API integration
            tasks_response = requests.get(f"{self.base_url}/api/tasks", timeout=10)
            self.assertEqual(tasks_response.status_code, 200)
            
            tasks_data = tasks_response.json()
            self.assertIn('status', tasks_data)
            self.assertEqual(tasks_data['status'], 'success')
            
            # Test task creation via API
            new_task = {
                "subject": "Integration Test Task",
                "sender": "Test User",
                "sender_email": "test@example.com",
                "content": "This is a test task for integration testing",
                "category": "General Inquiry",
                "priority": "Medium",
                "status": "New"
            }
            
            # Note: We're testing the API structure, not actual creation
            # since we don't have a POST endpoint for tasks in the current setup
            
            # Test analytics API integration
            analytics_endpoints = [
                "/api/analytics/report",
                "/api/analytics/current-metrics",
                "/api/analytics/system-health"
            ]
            
            for endpoint in analytics_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('status', data)
            
            duration = time.time() - start_time
            self.log_test_result("Frontend-Backend API Integration", "PASS", 
                               "All API endpoints responding correctly", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Frontend-Backend API Integration", "FAIL", 
                               f"API integration failed: {str(e)}", duration)
            self.fail(f"Frontend-backend API integration failed: {e}")
    
    def test_analytics_dashboard_integration(self):
        """Test 3: Analytics dashboard integration"""
        start_time = time.time()
        
        try:
            # Test analytics dashboard endpoints
            dashboard_endpoints = [
                "/api/analytics/dashboard",
                "/api/analytics/charts",
                "/api/analytics/user-behavior",
                "/api/analytics/performance"
            ]
            
            for endpoint in dashboard_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                self.assertEqual(response.status_code, 200)
                
                data = response.json()
                self.assertIn('status', data)
                self.assertEqual(data['status'], 'success')
            
            # Test real-time analytics integration
            realtime_endpoints = [
                "/api/realtime/metrics/live",
                "/api/realtime/performance/stats",
                "/api/realtime/alerts"
            ]
            
            for endpoint in realtime_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                self.assertEqual(response.status_code, 200)
            
            duration = time.time() - start_time
            self.log_test_result("Analytics Dashboard Integration", "PASS", 
                               "Analytics dashboard fully integrated", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Analytics Dashboard Integration", "FAIL", 
                               f"Analytics integration failed: {str(e)}", duration)
            self.fail(f"Analytics dashboard integration failed: {e}")
    
    def test_real_time_updates_integration(self):
        """Test 4: Real-time updates integration"""
        start_time = time.time()
        
        try:
            # Test Server-Sent Events endpoint
            sse_response = requests.get(f"{self.base_url}/api/realtime/dashboard/stream", timeout=5)
            self.assertEqual(sse_response.status_code, 200)
            self.assertEqual(sse_response.headers.get('content-type'), 'text/event-stream')
            
            # Test WebSocket endpoint availability (if implemented)
            # Note: WebSocket testing requires more complex setup
            websocket_available = self.check_websocket_availability()
            
            # Test real-time notification system
            notification_response = requests.post(
                f"{self.base_url}/api/realtime/notifications",
                json={"type": "info", "message": "Integration test notification"},
                timeout=10
            )
            self.assertEqual(notification_response.status_code, 200)
            
            duration = time.time() - start_time
            details = f"SSE working, WebSocket: {'Available' if websocket_available else 'Not available'}"
            self.log_test_result("Real-time Updates Integration", "PASS", details, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Real-time Updates Integration", "FAIL", 
                               f"Real-time integration failed: {str(e)}", duration)
            self.fail(f"Real-time updates integration failed: {e}")
    
    def check_websocket_availability(self):
        """Check if WebSocket endpoint is available"""
        try:
            # Try to connect to WebSocket endpoint
            response = requests.get(f"{self.base_url}/socket.io/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_browser_compatibility_integration(self):
        """Test 5: Browser compatibility integration"""
        if not self.driver:
            self.skipTest("Selenium WebDriver not available")
        
        start_time = time.time()
        
        try:
            # Test main page loading
            self.driver.get(f"{self.base_url}/")
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Test navigation elements
            nav_elements = [
                (By.LINK_TEXT, "Tasks"),
                (By.LINK_TEXT, "Threads"),
                (By.LINK_TEXT, "Analytics")
            ]
            
            for by, text in nav_elements:
                element = self.wait.until(EC.element_to_be_clickable((by, text)))
                self.assertIsNotNone(element)
            
            # Test JavaScript integration
            js_result = self.driver.execute_script("return typeof window.integrationManager !== 'undefined';")
            self.assertTrue(js_result, "Integration Manager not loaded")
            
            # Test analytics page
            self.driver.get(f"{self.base_url}/analytics")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Test threads page
            self.driver.get(f"{self.base_url}/threads")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            duration = time.time() - start_time
            self.log_test_result("Browser Compatibility Integration", "PASS", 
                               "All pages load correctly in browser", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Browser Compatibility Integration", "FAIL", 
                               f"Browser compatibility failed: {str(e)}", duration)
            self.fail(f"Browser compatibility integration failed: {e}")
    
    def test_end_to_end_workflow_integration(self):
        """Test 6: End-to-end workflow integration"""
        start_time = time.time()
        
        try:
            # Simulate complete user workflow
            
            # 1. User visits main dashboard
            response = requests.get(f"{self.base_url}/", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            # 2. User views tasks
            tasks_response = requests.get(f"{self.base_url}/api/tasks", timeout=10)
            self.assertEqual(tasks_response.status_code, 200)
            
            # 3. User checks analytics
            analytics_response = requests.get(f"{self.base_url}/analytics", timeout=10)
            self.assertEqual(analytics_response.status_code, 200)
            
            # 4. User views real-time dashboard
            realtime_response = requests.get(f"{self.base_url}/api/realtime/dashboard/live", timeout=10)
            self.assertEqual(realtime_response.status_code, 200)
            
            # 5. User checks system status
            health_response = requests.get(f"{self.base_url}/api/health", timeout=10)
            self.assertEqual(health_response.status_code, 200)
            
            # 6. User interacts with analytics
            charts_response = requests.get(f"{self.base_url}/api/analytics/charts", timeout=10)
            self.assertEqual(charts_response.status_code, 200)
            
            duration = time.time() - start_time
            self.log_test_result("End-to-End Workflow Integration", "PASS", 
                               "Complete user workflow functional", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("End-to-End Workflow Integration", "FAIL", 
                               f"Workflow integration failed: {str(e)}", duration)
            self.fail(f"End-to-end workflow integration failed: {e}")
    
    def test_performance_integration(self):
        """Test 7: Performance integration across components"""
        start_time = time.time()
        
        try:
            # Test response times for critical endpoints
            endpoints = [
                ("/api/health", 1.0),  # Health check should be very fast
                ("/api/tasks", 2.0),   # Tasks API
                ("/api/analytics/health", 2.0),  # Analytics health
                ("/api/realtime/dashboard/live", 3.0),  # Real-time data
                ("/api/analytics/charts", 3.0),  # Charts generation
            ]
            
            performance_results = {}
            
            for endpoint, max_time in endpoints:
                response_start = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=max_time + 1)
                response_time = time.time() - response_start
                
                self.assertEqual(response.status_code, 200)
                self.assertLessEqual(response_time, max_time, 
                                   f"{endpoint} took {response_time:.2f}s, expected < {max_time}s")
                
                performance_results[endpoint] = response_time
            
            duration = time.time() - start_time
            
            # Calculate average response time
            avg_response_time = sum(performance_results.values()) / len(performance_results)
            
            details = f"Avg response time: {avg_response_time:.2f}s, All endpoints under limits"
            self.log_test_result("Performance Integration", "PASS", details, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Performance Integration", "FAIL", 
                               f"Performance integration failed: {str(e)}", duration)
            self.fail(f"Performance integration failed: {e}")
    
    def test_error_handling_integration(self):
        """Test 8: Error handling integration"""
        start_time = time.time()
        
        try:
            # Test 404 error handling
            response = requests.get(f"{self.base_url}/api/nonexistent-endpoint", timeout=10)
            self.assertEqual(response.status_code, 404)
            
            # Test invalid request handling
            invalid_response = requests.post(
                f"{self.base_url}/api/tasks/invalid",
                json={"invalid": "data"},
                timeout=10
            )
            # Should return 404 for invalid task ID
            self.assertEqual(invalid_response.status_code, 404)
            
            # Test analytics error handling
            analytics_error_response = requests.get(f"{self.base_url}/api/analytics/invalid", timeout=10)
            self.assertEqual(analytics_error_response.status_code, 404)
            
            duration = time.time() - start_time
            self.log_test_result("Error Handling Integration", "PASS", 
                               "Error handling working correctly", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Error Handling Integration", "FAIL", 
                               f"Error handling failed: {str(e)}", duration)
            self.fail(f"Error handling integration failed: {e}")
    
    def test_data_flow_integration(self):
        """Test 9: Data flow integration between components"""
        start_time = time.time()
        
        try:
            # Test data consistency across components
            
            # 1. Get tasks data
            tasks_response = requests.get(f"{self.base_url}/api/tasks", timeout=10)
            tasks_data = tasks_response.json()
            
            # 2. Get analytics data
            analytics_response = requests.get(f"{self.base_url}/api/analytics/tasks", timeout=10)
            analytics_data = analytics_response.json()
            
            # 3. Get real-time metrics
            metrics_response = requests.get(f"{self.base_url}/api/realtime/metrics/live", timeout=10)
            metrics_data = metrics_response.json()
            
            # Verify data structure consistency
            self.assertIn('status', tasks_data)
            self.assertIn('status', analytics_data)
            self.assertIn('status', metrics_data)
            
            # Verify all components return success status
            self.assertEqual(tasks_data['status'], 'success')
            self.assertEqual(analytics_data['status'], 'success')
            self.assertEqual(metrics_data['status'], 'success')
            
            duration = time.time() - start_time
            self.log_test_result("Data Flow Integration", "PASS", 
                               "Data flow consistent across components", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Data Flow Integration", "FAIL", 
                               f"Data flow integration failed: {str(e)}", duration)
            self.fail(f"Data flow integration failed: {e}")
    
    def test_concurrent_access_integration(self):
        """Test 10: Concurrent access integration"""
        start_time = time.time()
        
        try:
            # Test concurrent requests to different endpoints
            endpoints = [
                "/api/health",
                "/api/tasks",
                "/api/analytics/health",
                "/api/realtime/dashboard/live",
                "/api/analytics/charts"
            ]
            
            def make_request(endpoint):
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                    return response.status_code == 200
                except:
                    return False
            
            # Create threads for concurrent requests
            threads = []
            results = []
            
            for endpoint in endpoints:
                thread = threading.Thread(target=lambda e=endpoint: results.append(make_request(e)))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Verify all requests succeeded
            self.assertEqual(len(results), len(endpoints))
            self.assertTrue(all(results), "Some concurrent requests failed")
            
            duration = time.time() - start_time
            self.log_test_result("Concurrent Access Integration", "PASS", 
                               f"All {len(endpoints)} concurrent requests succeeded", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Concurrent Access Integration", "FAIL", 
                               f"Concurrent access failed: {str(e)}", duration)
            self.fail(f"Concurrent access integration failed: {e}")
    
    @classmethod
    def generate_integration_report(cls):
        """Generate detailed integration test report"""
        report = {
            "test_suite": "Phase 11: System Integration Tests",
            "start_time": cls.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_tests": len(cls.test_results),
            "passed": sum(1 for r in cls.test_results if r['status'] == 'PASS'),
            "failed": sum(1 for r in cls.test_results if r['status'] == 'FAIL'),
            "success_rate": 0,
            "test_results": cls.test_results
        }
        
        if report["total_tests"] > 0:
            report["success_rate"] = (report["passed"] / report["total_tests"]) * 100
        
        # Save report to file
        report_filename = f"phase11_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved to: {report_filename}")
        
        return report

def run_phase11_integration_tests():
    """Run Phase 11 integration tests"""
    print("🚀 Starting Phase 11: System Integration Tests")
    print("=" * 60)
    
    # Check if application is running
    try:
        response = requests.get("http://localhost:5001/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Application not running on localhost:5001")
            print("   Please start the application before running integration tests")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to application on localhost:5001")
        print("   Please start the application before running integration tests")
        return False
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(Phase11IntegrationTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_phase11_integration_tests()
    exit(0 if success else 1)
