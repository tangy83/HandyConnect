#!/usr/bin/env python3
"""
Simple CI/CD health check - validates code can be imported
"""
import sys
import os

print("🔍 HandyConnect CI/CD Health Check")
print("=" * 60)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

checks_passed = 0
checks_total = 0

def check_import(module_name, description):
    """Try to import a module"""
    global checks_passed, checks_total
    checks_total += 1
    try:
        __import__(module_name)
        print(f"✅ {description}")
        checks_passed += 1
        return True
    except Exception as e:
        print(f"❌ {description}: {str(e)[:50]}")
        return False

# Check core imports
print("\n📦 Core Modules:")
print("-" * 60)
check_import("flask", "Flask framework")
check_import("requests", "HTTP requests")
check_import("dotenv", "Environment variables")

# Check features (without actually importing - just check files exist)
print("\n📁 Feature Files:")
print("-" * 60)
from pathlib import Path

files_to_check = [
    ("features/core_services/task_service.py", "Task Service"),
    ("features/core_services/email_service.py", "Email Service"),
    ("features/core_services/llm_service.py", "LLM Service"),
    ("features/analytics/analytics_framework.py", "Analytics Framework"),
    ("data/tasks.json", "Tasks data file"),
]

for filepath, desc in files_to_check:
    checks_total += 1
    if Path(filepath).exists():
        print(f"✅ {desc}")
        checks_passed += 1
    else:
        print(f"❌ {desc} - NOT FOUND")

# Summary
print("\n" + "=" * 60)
print(f"📊 RESULTS: {checks_passed}/{checks_total} checks passed")
success_rate = (checks_passed / checks_total * 100) if checks_total > 0 else 0
print(f"📈 Success Rate: {success_rate:.1f}%")

if checks_passed == checks_total:
    print("🎉 ALL CHECKS PASSED!")
    sys.exit(0)
else:
    print("⚠️  SOME CHECKS FAILED")
    sys.exit(1)

