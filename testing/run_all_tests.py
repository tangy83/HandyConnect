#!/usr/bin/env python3
"""
Comprehensive Test Runner for HandyConnect Application
Runs both unit tests and integration tests
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_app_running():
    """Check if the application is running"""
    try:
        import requests
        response = requests.get("http://localhost:5001/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def run_unit_tests():
    """Run unit tests using pytest"""
    print_header("RUNNING UNIT TESTS")
    
    # Find all unit test files
    unit_test_files = [
        "tests/test_task_service.py",
        "tests/test_llm_service.py",
        "tests/test_email_service.py",
        "tests/test_analytics.py"
    ]
    
    # Filter existing files
    existing_tests = [f for f in unit_test_files if os.path.exists(f)]
    
    if not existing_tests:
        print("No unit test files found.")
        return {"passed": 0, "failed": 0, "total": 0}
    
    print(f"Found {len(existing_tests)} unit test files")
    
    # Run pytest
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "-v", "--tb=short"] + existing_tests,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        # Parse results (basic parsing)
        output = result.stdout
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        
        return {"passed": passed, "failed": failed, "total": passed + failed}
        
    except subprocess.TimeoutExpired:
        print("Unit tests timed out after 5 minutes")
        return {"passed": 0, "failed": 0, "total": 0, "timeout": True}
    except Exception as e:
        print(f"Error running unit tests: {e}")
        return {"passed": 0, "failed": 0, "total": 0, "error": str(e)}

def run_integration_tests_simple():
    """Run simple integration tests without external dependencies"""
    print_header("RUNNING INTEGRATION TESTS (Simple)")
    
    try:
        import requests
        
        results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": []
        }
        
        # Test endpoints
        endpoints = [
            ("http://localhost:5001/api/health", "Health Check"),
            ("http://localhost:5001/api/tasks", "Tasks API"),
            ("http://localhost:5001/", "Main Dashboard"),
            ("http://localhost:5001/api/analytics/health", "Analytics Health"),
        ]
        
        for url, name in endpoints:
            results["total"] += 1
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"[PASS] {name}")
                    results["passed"] += 1
                    results["details"].append({"test": name, "status": "PASS"})
                else:
                    print(f"[FAIL] {name} - Status {response.status_code}")
                    results["failed"] += 1
                    results["details"].append({"test": name, "status": "FAIL"})
            except Exception as e:
                print(f"[FAIL] {name} - {str(e)[:50]}")
                results["failed"] += 1
                results["details"].append({"test": name, "status": "FAIL", "error": str(e)[:50]})
        
        return results
        
    except ImportError:
        print("requests library not available - skipping integration tests")
        return {"passed": 0, "failed": 0, "total": 0, "skipped": True}

def run_integration_tests_full():
    """Run full integration tests using existing test runner"""
    print_header("RUNNING INTEGRATION TESTS (Full Suite)")
    
    if os.path.exists("run_phase11_tests.py"):
        try:
            result = subprocess.run(
                ["python", "run_phase11_tests.py"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            
            # Try to parse the JSON report
            import glob
            reports = glob.glob("phase11_integration_test_report_*.json")
            if reports:
                latest_report = max(reports, key=os.path.getmtime)
                with open(latest_report, 'r') as f:
                    report_data = json.load(f)
                    summary = report_data.get('summary', {})
                    return {
                        "passed": summary.get('passed', 0),
                        "failed": summary.get('failed', 0),
                        "total": summary.get('total_tests', 0),
                        "report_file": latest_report
                    }
            
            return {"passed": 0, "failed": 0, "total": 0}
            
        except subprocess.TimeoutExpired:
            print("Integration tests timed out")
            return {"passed": 0, "failed": 0, "total": 0, "timeout": True}
        except Exception as e:
            print(f"Error running integration tests: {e}")
            return {"passed": 0, "failed": 0, "total": 0, "error": str(e)}
    else:
        print("Phase 11 integration test runner not found")
        return {"passed": 0, "failed": 0, "total": 0, "not_found": True}

def generate_summary_report(unit_results, integration_results):
    """Generate comprehensive test summary report"""
    print_header("COMPREHENSIVE TEST SUMMARY")
    
    total_passed = unit_results.get("passed", 0) + integration_results.get("passed", 0)
    total_failed = unit_results.get("failed", 0) + integration_results.get("failed", 0)
    total_tests = unit_results.get("total", 0) + integration_results.get("total", 0)
    
    print(f"\nUnit Tests:")
    print(f"  Total: {unit_results.get('total', 0)}")
    print(f"  Passed: {unit_results.get('passed', 0)}")
    print(f"  Failed: {unit_results.get('failed', 0)}")
    
    print(f"\nIntegration Tests:")
    print(f"  Total: {integration_results.get('total', 0)}")
    print(f"  Passed: {integration_results.get('passed', 0)}")
    print(f"  Failed: {integration_results.get('failed', 0)}")
    
    print(f"\nOVERALL RESULTS:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_failed}")
    
    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        print(f"  Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n[SUCCESS] EXCELLENT! Test suite passed with high success rate!")
        elif success_rate >= 70:
            print("\n[GOOD] Most tests passed. Review failures above.")
        elif success_rate >= 50:
            print("\n[WARNING] Many tests failed. Review issues above.")
        else:
            print("\n[CRITICAL] Most tests failed. Immediate attention required.")
    else:
        print("\n[WARNING] No tests were executed.")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "unit_tests": unit_results,
        "integration_tests": integration_results,
        "summary": {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0
        }
    }
    
    report_file = f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")
    print("="*70)

def main():
    """Main test execution"""
    print_header("HANDYCONNECT COMPREHENSIVE TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if app is running
    app_running = check_app_running()
    if app_running:
        print("[OK] Application is running on localhost:5001")
    else:
        print("[WARNING] Application is NOT running - integration tests will be limited")
    
    # Run unit tests
    print("\n" + "-"*70)
    unit_results = run_unit_tests()
    
    # Run integration tests
    print("\n" + "-"*70)
    if app_running:
        # Try full integration tests first
        integration_results = run_integration_tests_full()
        
        # If that fails, try simple integration tests
        if integration_results.get("total", 0) == 0:
            integration_results = run_integration_tests_simple()
    else:
        print("Skipping integration tests - application not running")
        print("To run integration tests, start the application with: python app.py")
        integration_results = {"passed": 0, "failed": 0, "total": 0, "skipped": True}
    
    # Generate summary
    print("\n" + "-"*70)
    generate_summary_report(unit_results, integration_results)
    
    # Return exit code
    total_failed = unit_results.get("failed", 0) + integration_results.get("failed", 0)
    return 0 if total_failed == 0 else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

