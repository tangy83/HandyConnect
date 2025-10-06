#!/usr/bin/env python3
"""
Simple script to get Microsoft authentication code
"""
import os
import pathlib
from dotenv import load_dotenv

# Load environment variables
env_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from features.core_services.email_service import EmailService

print("\n" + "="*70)
print("MICROSOFT GRAPH API AUTHENTICATION")
print("="*70 + "\n")

email_service = EmailService()

print("Requesting authentication code...")
print("Please wait...\n")

# This will display the code and URL
token = email_service.get_access_token(open_browser=False)

if token:
    print("\n" + "="*70)
    print("✅ SUCCESS! Authentication complete")
    print("="*70)
else:
    print("\n" + "="*70)
    print("❌ Authentication failed or canceled")
    print("="*70)

