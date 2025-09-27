#!/usr/bin/env python3
"""
Simple email integration test - no interactive prompts
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.core_services.email_service import EmailService

def main():
    """Run a simple email integration test"""
    print("HandyConnect Simple Email Integration Test")
    print("=" * 50)
    
    # Test 1: Configuration
    print("🔧 Step 1: Testing Configuration...")
    client_id = os.getenv('CLIENT_ID')
    authority = os.getenv('AUTHORITY')
    scopes = os.getenv('SCOPES')
    
    print(f"CLIENT_ID: {client_id}")
    print(f"AUTHORITY: {authority}")
    print(f"SCOPES: {scopes}")
    
    if not client_id or client_id == 'your_azure_app_client_id':
        print("❌ CLIENT_ID not configured properly")
        return
    
    print("✅ Configuration looks good!")
    
    # Test 2: EmailService initialization
    print("\n🔧 Step 2: Testing EmailService Initialization...")
    try:
        email_service = EmailService()
        print("✅ EmailService initialized successfully")
    except Exception as e:
        print(f"❌ EmailService initialization failed: {e}")
        return
    
    # Test 3: Token acquisition (this is where it might hang)
    print("\n🔧 Step 3: Testing Token Acquisition...")
    print("⚠️  This will attempt device flow authentication...")
    print("⚠️  Look for a code in the output below!")
    print("⚠️  You'll need to complete authentication in your browser...")
    
    try:
        print("Attempting to get access token...")
        token = email_service.get_access_token()
        
        if token:
            print("✅ Token acquired successfully!")
            print(f"Token (first 20 chars): {token[:20]}...")
        else:
            print("❌ Token acquisition failed")
            return
    except Exception as e:
        print(f"❌ Token acquisition error: {e}")
        return
    
    # Test 4: User info
    print("\n🔧 Step 4: Testing User Info Retrieval...")
    try:
        user_info = email_service.get_user_info()
        if user_info:
            print("✅ User info retrieved successfully!")
            print(f"Name: {user_info.get('displayName', 'Unknown')}")
            print(f"Email: {user_info.get('mail', 'Unknown')}")
        else:
            print("❌ Failed to get user info")
    except Exception as e:
        print(f"❌ User info error: {e}")
    
    # Test 5: Email reading
    print("\n🔧 Step 5: Testing Email Reading...")
    try:
        emails = email_service.get_emails(top=3)
        if emails:
            print(f"✅ Successfully retrieved {len(emails)} emails!")
            for i, email in enumerate(emails[:2], 1):
                print(f"   {i}. {email['subject'][:50]}... (from: {email['sender']['email']})")
        else:
            print("⚠️  No emails found (this might be normal if inbox is empty)")
    except Exception as e:
        print(f"❌ Email reading error: {e}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    main()
