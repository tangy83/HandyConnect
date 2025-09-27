#!/usr/bin/env python3
"""
Debug test - very simple to see what's happening
"""

print("🚀 Starting debug test...")

import os
print("✅ os imported")

from dotenv import load_dotenv
print("✅ dotenv imported")

load_dotenv()
print("✅ .env loaded")

client_id = os.getenv('CLIENT_ID')
print(f"✅ CLIENT_ID: {client_id}")

print("🔧 Testing basic imports...")

try:
    import msal
    print("✅ msal imported")
except Exception as e:
    print(f"❌ msal import failed: {e}")

try:
    import requests
    print("✅ requests imported")
except Exception as e:
    print(f"❌ requests import failed: {e}")

print("🔧 Testing EmailService import...")

try:
    from features.core_services.email_service import EmailService
    print("✅ EmailService imported")
except Exception as e:
    print(f"❌ EmailService import failed: {e}")

print("🔧 Testing EmailService creation...")

try:
    email_service = EmailService()
    print("✅ EmailService created")
    print(f"Client ID: {email_service.client_id}")
except Exception as e:
    print(f"❌ EmailService creation failed: {e}")

print("🎉 Debug test completed!")
