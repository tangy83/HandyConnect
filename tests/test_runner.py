"""
Comprehensive test runner for HandyConnect application
"""
import pytest
import sys
import os
import argparse
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_unit_tests():
    """Run unit tests only"""
    return pytest.main([
        '-m', 'unit',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=features.analytics',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov/unit',
        'tests/'
    ])

def run_integration_tests():
    """Run integration tests only"""
    return pytest.main([
        '-m', 'integration',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=features.analytics',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov/integration',
        'tests/'
    ])

def run_api_tests():
    """Run API tests only"""
    return pytest.main([
        '-m', 'api',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=features.analytics',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov/api',
        'tests/'
    ])

def run_analytics_tests():
    """Run analytics tests only"""
    return pytest.main([
        '-m', 'analytics',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=features.analytics',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov/analytics',
        'tests/'
    ])

def run_performance_tests():
    """Run performance tests only"""
    return pytest.main([
        '-m', 'performance',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=features.analytics',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov/performance',
        'tests/'
    ])

def run_e2e_tests():
    """Run end-to-end tests only"""
    return pytest.main([
        '-m', 'e2e',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=features.analytics',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov/e2e',
        'tests/'
    ])

def run_slow_tests():
    """Run slow tests only"""
    return pytest.main([
        '-m', 'slow',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=features.analytics',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov/slow',
        'tests/'
    ])

def run_all_tests():
    """Run all tests"""
    return pytest.main([
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=.',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov/all',
        '--cov-exclude=tests/*',
        '--cov-exclude=venv/*',
        '--cov-exclude=env/*',
        'tests/'
    ])

def run_fast_tests():
    """Run fast tests only (exclude slow tests)"""
    return pytest.main([
        '-v',
        '--tb=short',
        '--disable-warnings',
        '-m', 'not slow',
        '--cov=.',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov/fast',
        '--cov-exclude=tests/*',
        '--cov-exclude=venv/*',
        '--cov-exclude=env/*',
        'tests/'
    ])

def run_specific_test_file(test_file):
    """Run specific test file"""
    return pytest.main([
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=features.analytics',
        '--cov-report=term-missing',
        f'tests/{test_file}'
    ])

def run_specific_test_class(test_file, test_class):
    """Run specific test class"""
    return pytest.main([
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=features.analytics',
        '--cov-report=term-missing',
        f'tests/{test_file}::{test_class}'
    ])

def run_specific_test_method(test_file, test_class, test_method):
    """Run specific test method"""
    return pytest.main([
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=features.analytics',
        '--cov-report=term-missing',
        f'tests/{test_file}::{test_class}::{test_method}'
    ])

def generate_test_report():
    """Generate comprehensive test report"""
    import subprocess
    import json
    from datetime import datetime
    
    # Run tests with JSON output
    result = subprocess.run([
        'python', '-m', 'pytest',
        '--json-report',
        '--json-report-file=test_report.json',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--cov=.',
        '--cov-report=json:coverage.json',
        '--cov-exclude=tests/*',
        '--cov-exclude=venv/*',
        '--cov-exclude=env/*',
        'tests/'
    ], capture_output=True, text=True)
    
    # Generate HTML report
    if os.path.exists('test_report.json'):
        with open('test_report.json', 'r') as f:
            report_data = json.load(f)
        
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>HandyConnect Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                .test-results {{ margin: 20px 0; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .skipped {{ color: orange; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>HandyConnect Test Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>Test Summary</h2>
                <p><strong>Total Tests:</strong> {report_data.get('summary', {}).get('total', 0)}</p>
                <p><strong>Passed:</strong> <span class="passed">{report_data.get('summary', {}).get('passed', 0)}</span></p>
                <p><strong>Failed:</strong> <span class="failed">{report_data.get('summary', {}).get('failed', 0)}</span></p>
                <p><strong>Skipped:</strong> <span class="skipped">{report_data.get('summary', {}).get('skipped', 0)}</span></p>
                <p><strong>Duration:</strong> {report_data.get('summary', {}).get('duration', 0):.2f} seconds</p>
            </div>
            
            <div class="test-results">
                <h2>Test Results</h2>
                <table>
                    <tr>
                        <th>Test</th>
                        <th>Status</th>
                        <th>Duration</th>
                    </tr>
        """
        
        for test in report_data.get('tests', []):
            status_class = test.get('outcome', '').lower()
            html_content += f"""
                    <tr>
                        <td>{test.get('nodeid', '')}</td>
                        <td class="{status_class}">{test.get('outcome', '')}</td>
                        <td>{test.get('duration', 0):.3f}s</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        
        with open('test_report.html', 'w') as f:
            f.write(html_content)
        
        print("Test report generated: test_report.html")
    
    return result.returncode

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='HandyConnect Test Runner')
    parser.add_argument('--type', choices=[
        'unit', 'integration', 'api', 'analytics', 'performance', 
        'e2e', 'slow', 'all', 'fast'
    ], default='all', help='Type of tests to run')
    parser.add_argument('--file', help='Specific test file to run')
    parser.add_argument('--class', dest='test_class', help='Specific test class to run')
    parser.add_argument('--method', help='Specific test method to run')
    parser.add_argument('--report', action='store_true', help='Generate test report')
    
    args = parser.parse_args()
    
    # Create coverage directories
    os.makedirs('htmlcov', exist_ok=True)
    
    if args.report:
        return generate_test_report()
    
    if args.file:
        if args.test_class and args.method:
            return run_specific_test_method(args.file, args.test_class, args.method)
        elif args.test_class:
            return run_specific_test_class(args.file, args.test_class)
        else:
            return run_specific_test_file(args.file)
    
    # Run tests based on type
    test_functions = {
        'unit': run_unit_tests,
        'integration': run_integration_tests,
        'api': run_api_tests,
        'analytics': run_analytics_tests,
        'performance': run_performance_tests,
        'e2e': run_e2e_tests,
        'slow': run_slow_tests,
        'all': run_all_tests,
        'fast': run_fast_tests
    }
    
    test_function = test_functions.get(args.type, run_all_tests)
    return test_function()

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
