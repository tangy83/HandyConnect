#!/usr/bin/env python3
"""
Step-by-step email integration test
Tests each component individually to identify where issues occur
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.core_services.email_service import EmailService

def test_step_1_configuration():
    """Test 1: Check if configuration is loaded correctly"""
    print("🔧 Step 1: Testing Configuration...")
    print("=" * 50)
    
    client_id = os.getenv('CLIENT_ID')
    authority = os.getenv('AUTHORITY')
    scopes = os.getenv('SCOPES')
    
    print(f"CLIENT_ID: {client_id}")
    print(f"AUTHORITY: {authority}")
    print(f"SCOPES: {scopes}")
    
    if not client_id or client_id == 'your_azure_app_client_id':
        print("❌ CLIENT_ID not configured properly")
        return False
    
    print("✅ Configuration looks good!")
    return True

def test_step_2_email_service_init():
    """Test 2: Test EmailService initialization"""
    print("\n🔧 Step 2: Testing EmailService Initialization...")
    print("=" * 50)
    
    try:
        email_service = EmailService()
        print("✅ EmailService initialized successfully")
        print(f"Client ID: {email_service.client_id}")
        print(f"Authority: {email_service.authority}")
        print(f"Scopes: {email_service.scopes}")
        return email_service
    except Exception as e:
        print(f"❌ EmailService initialization failed: {e}")
        return None

def test_step_3_token_acquisition():
    """Test 3: Test token acquisition (this is where it might hang)"""
    print("\n🔧 Step 3: Testing Token Acquisition...")
    print("=" * 50)
    print("⚠️  This step may take a moment and will open a browser window...")
    print("⚠️  Look for a code in the terminal output!")
    
    try:
        email_service = EmailService()
        print("Attempting to get access token...")
        token = email_service.get_access_token()
        
        if token:
            print("✅ Token acquired successfully!")
            print(f"Token (first 20 chars): {token[:20]}...")
            return token
        else:
            print("❌ Token acquisition failed")
            return None
    except Exception as e:
        print(f"❌ Token acquisition error: {e}")
        return None

def test_step_4_user_info():
    """Test 4: Test user info retrieval"""
    print("\n🔧 Step 4: Testing User Info Retrieval...")
    print("=" * 50)
    
    try:
        email_service = EmailService()
        token = email_service.get_access_token()
        
        if not token:
            print("❌ No token available, skipping user info test")
            return False
        
        print("Getting user info...")
        user_info = email_service.get_user_info()
        
        if user_info:
            print("✅ User info retrieved successfully!")
            print(f"Name: {user_info.get('displayName', 'Unknown')}")
            print(f"Email: {user_info.get('mail', 'Unknown')}")
            return True
        else:
            print("❌ Failed to get user info")
            return False
    except Exception as e:
        print(f"❌ User info error: {e}")
        return False

def test_step_5_email_reading():
    """Test 5: Test email reading"""
    print("\n🔧 Step 5: Testing Email Reading...")
    print("=" * 50)
    
    try:
        email_service = EmailService()
        token = email_service.get_access_token()
        
        if not token:
            print("❌ No token available, skipping email reading test")
            return False
        
        print("Reading emails...")
        emails = email_service.get_emails(top=3)
        
        if emails:
            print(f"✅ Successfully retrieved {len(emails)} emails!")
            for i, email in enumerate(emails[:2], 1):
                print(f"   {i}. {email['subject'][:50]}... (from: {email['sender']['email']})")
            return True
        else:
            print("⚠️  No emails found (this might be normal if inbox is empty)")
            return True
    except Exception as e:
        print(f"❌ Email reading error: {e}")
        return False

def main():
    """Run all tests step by step"""
    print("HandyConnect Step-by-Step Email Integration Test")
    print("=" * 60)
    
    # Test 1: Configuration
    if not test_step_1_configuration():
        print("\n❌ Configuration test failed. Please check your .env file.")
        return
    
    # Test 2: EmailService initialization
    email_service = test_step_2_email_service_init()
    if not email_service:
        print("\n❌ EmailService initialization failed.")
        return
    
    # Test 3: Token acquisition (this is the critical step)
    print("\n" + "="*60)
    print("🚨 CRITICAL STEP: Token Acquisition")
    print("="*60)
    print("This step will:")
    print("1. Open a browser window")
    print("2. Show you a code in the terminal")
    print("3. Ask you to enter that code in the browser")
    print("4. Wait for you to complete authentication")
    print("\nPress Enter when you're ready to continue...")
    input()
    
    token = test_step_3_token_acquisition()
    if not token:
        print("\n❌ Token acquisition failed. This is likely where the issue is.")
        return
    
    # Test 4: User info
    test_step_4_user_info()
    
    # Test 5: Email reading
    test_step_5_email_reading()
    
    print("\n🎉 All tests completed!")
    print("If you see this message, your email integration is working!")

if __name__ == "__main__":
    main()
