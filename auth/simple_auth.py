#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.append(str(Path(__file__).parent))

from features.core_services.email_service import EmailService

print("\n" + "="*80)
print("🔐 MICROSOFT AUTHENTICATION CODE")
print("="*80)
print("📧 Account: Handymyjob@outlook.com")
print("="*80)

email_service = EmailService()
token = email_service.get_access_token(open_browser=True)

if token:
    print("\n✅ SUCCESS! Connected to Handymyjob@outlook.com")
else:
    print("\n❌ FAILED! Please try again")
