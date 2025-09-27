#!/usr/bin/env python3
"""
Test only the token acquisition part
"""

print("🚀 Starting token acquisition test...")

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.core_services.email_service import EmailService

print("✅ Imports successful")

# Create EmailService
email_service = EmailService()
print("✅ EmailService created")

print("🔧 Attempting token acquisition...")
print("⚠️  This will try to open a browser and show you a code...")

try:
    token = email_service.get_access_token()
    print(f"✅ Token acquired: {token[:20] if token else 'None'}...")
except Exception as e:
    print(f"❌ Token acquisition failed: {e}")

print("🎉 Token test completed!")
