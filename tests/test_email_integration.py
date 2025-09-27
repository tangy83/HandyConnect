#!/usr/bin/env python3
"""
Test script for the updated email integration
Tests the device flow authentication and email reading
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.core_services.email_service import EmailService

def test_email_integration():
    """Test the email integration with device flow authentication"""
    print("🔧 Testing Email Integration with Device Flow Authentication")
    print("=" * 60)
    
    # Initialize email service
    email_service = EmailService()
    
    # Test 1: Check configuration
    print("\n1️⃣ Checking Configuration...")
    client_id = os.getenv('CLIENT_ID')
    authority = os.getenv('AUTHORITY')
    scopes = os.getenv('SCOPES')
    
    if not client_id or client_id == 'your_azure_app_client_id':
        print("❌ CLIENT_ID not configured. Please update .env file with your Azure app client ID.")
        return False
    
    print(f"✅ CLIENT_ID: {client_id}")
    print(f"✅ AUTHORITY: {authority}")
    print(f"✅ SCOPES: {scopes}")
    
    # Test 2: Test authentication
    print("\n2️⃣ Testing Authentication...")
    try:
        token = email_service.get_access_token()
        if token:
            print("✅ Authentication successful!")
            print("🔑 Token acquired (first 20 chars):", token[:20] + "...")
        else:
            print("❌ Authentication failed!")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Test 3: Test user info
    print("\n3️⃣ Testing User Info...")
    try:
        user_info = email_service.get_user_info()
        if user_info:
            print("✅ User info retrieved successfully!")
            print(f"👤 Name: {user_info.get('displayName', 'Unknown')}")
            print(f"📧 Email: {user_info.get('mail', 'Unknown')}")
        else:
            print("❌ Failed to get user info!")
            return False
    except Exception as e:
        print(f"❌ User info error: {e}")
        return False
    
    # Test 4: Test email reading
    print("\n4️⃣ Testing Email Reading...")
    try:
        emails = email_service.get_emails(top=5)
        if emails:
            print(f"✅ Successfully retrieved {len(emails)} emails!")
            for i, email in enumerate(emails[:3], 1):
                print(f"   {i}. {email['subject'][:50]}... (from: {email['sender']['email']})")
        else:
            print("⚠️  No emails found (this might be normal if inbox is empty)")
    except Exception as e:
        print(f"❌ Email reading error: {e}")
        return False
    
    # Test 5: Test email body reading (if emails exist)
    if emails:
        print("\n5️⃣ Testing Email Body Reading...")
        try:
            first_email = emails[0]
            email_body = email_service.get_email_body(first_email['id'])
            if email_body:
                print("✅ Email body retrieved successfully!")
                print(f"📄 Body preview (first 100 chars): {email_body[:100]}...")
            else:
                print("❌ Failed to get email body!")
                return False
        except Exception as e:
            print(f"❌ Email body error: {e}")
            return False
    
    print("\n🎉 All tests passed! Email integration is working correctly.")
    return True

def main():
    """Main function"""
    print("HandyConnect Email Integration Test")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your Azure app configuration.")
        return
    
    # Run tests
    success = test_email_integration()
    
    if success:
        print("\n✅ Email integration is ready to use!")
        print("\nNext steps:")
        print("1. Update your .env file with actual Azure app credentials")
        print("2. Run the main application: python app.py")
        print("3. Test the email processing pipeline")
    else:
        print("\n❌ Email integration needs attention.")
        print("Please check the error messages above and fix any issues.")

if __name__ == "__main__":
    main()
