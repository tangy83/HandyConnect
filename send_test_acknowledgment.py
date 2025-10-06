#!/usr/bin/env python3
"""
Send acknowledgment email for Anika's case
"""
import os
import pathlib
from dotenv import load_dotenv

# Load .env
env_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from features.core_services.acknowledgment_service import AcknowledgmentService
from features.core_services.case_service import CaseService

print("\n🔍 Finding Anika's case...")

case_service = CaseService()
cases = case_service.load_cases()

# Find Anika's case
anika_case = None
for case in cases:
    if case.get('customer_info', {}).get('email') == 'anika.tanuj@gmail.com':
        anika_case = case
        break

if not anika_case:
    print("❌ Case not found")
    exit(1)

print(f"✅ Found case: {anika_case['case_number']}")
print(f"   Customer: {anika_case['customer_info']['name']}")
print(f"   Email: {anika_case['customer_info']['email']}")
print(f"   Title: {anika_case['case_title']}")

print("\n📧 Sending acknowledgment email...")

ack_service = AcknowledgmentService()

# Simulate the original email
original_email = {
    'subject': anika_case['case_title'],
    'body': anika_case.get('case_metadata', {}).get('description', 'Please fix it. This is about Property 222 and block c'),
    'sender': {
        'name': anika_case['customer_info']['name'],
        'email': anika_case['customer_info']['email']
    }
}

success = ack_service.send_acknowledgment(
    case_id=anika_case['case_id'],
    customer_email=anika_case['customer_info']['email'],
    original_email=original_email,
    case_data=anika_case
)

if success:
    print("\n" + "="*70)
    print("✅ SUCCESS! Acknowledgment email sent to anika.tanuj@gmail.com")
    print("="*70)
    print(f"\n📬 Check the inbox for: anika.tanuj@gmail.com")
    print(f"📧 Subject: Case #{anika_case['case_number']} - ...")
    print(f"\nThe email should arrive within 1-2 minutes!")
else:
    print("\n" + "="*70)
    print("❌ Failed to send acknowledgment email")
    print("="*70)
    print("\nCheck logs for errors:")
    print("tail -50 logs/app.log | grep -i acknowledgment")

