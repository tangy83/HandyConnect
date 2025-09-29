#!/usr/bin/env python3
"""
Quick TDD Test Runner for HandyConnect
Author: Sunayana
"""

import subprocess
import sys
import time
import requests

def check_app_running():
    """Check if the application is running"""
    try:
        response = requests.get("http://localhost:5001/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_app():
    """Start the application"""
    print("🚀 Starting HandyConnect application...")
    try:
        # Set environment variables and start app
        env = {
            'OPENAI_API_KEY': 'test-key',
            'SECRET_KEY': 'dev-secret'
        }
        
        # Start app in background
        process = subprocess.Popen(
            ['python', 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for app to start
        print("⏳ Waiting for application to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_app_running():
                print("✅ Application started successfully!")
                return process
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ Application failed to start within 30 seconds")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return None

def run_tdd_tests():
    """Run TDD tests"""
    print("\n🧪 Running TDD Tests...")
    try:
        result = subprocess.run([sys.executable, 'tests/comprehensive_tdd.py'], 
                              capture_output=True, text=True, timeout=60)
        
        print("=" * 60)
        print("TDD TEST OUTPUT:")
        print("=" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ TDD tests timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Failed to run TDD tests: {e}")
        return False

def main():
    """Main TDD test runner"""
    print("🎯 HandyConnect TDD Test Runner")
    print("=" * 40)
    
    # Check if app is already running
    if check_app_running():
        print("✅ Application is already running")
        app_process = None
    else:
        # Start the application
        app_process = start_app()
        if not app_process:
            print("❌ Cannot run tests without application running")
            return False
    
    try:
        # Run TDD tests
        success = run_tdd_tests()
        
        if success:
            print("\n🎉 TDD TESTS COMPLETED SUCCESSFULLY!")
        else:
            print("\n⚠️ SOME TDD TESTS FAILED!")
            
        return success
        
    finally:
        # Clean up
        if app_process:
            print("\n🛑 Stopping application...")
            app_process.terminate()
            app_process.wait()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
