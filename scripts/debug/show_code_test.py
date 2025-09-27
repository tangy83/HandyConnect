#!/usr/bin/env python3
"""
Test that shows the authentication code clearly
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
    print("=" * 60)
    print("🔐 HANDYCONNECT EMAIL AUTHENTICATION TEST")
    print("=" * 60)
    
    # Create EmailService
    email_service = EmailService()
    print("✅ EmailService created successfully")
    
    print("\n🔧 Starting authentication process...")
    print("⚠️  This will open a browser window and show you a code to enter.")
    print("⚠️  Look for the code below in this terminal window!")
    print("\n" + "=" * 60)
    print("🚨 AUTHENTICATION CODE WILL APPEAR BELOW:")
    print("=" * 60)
    
    try:
        # This will show the code in the terminal
        token = email_service.get_access_token()
        
        if token:
            print("\n" + "=" * 60)
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print("=" * 60)
            print(f"Token acquired: {token[:20]}...")
            
            # Test user info
            print("\n🔧 Testing user info...")
            user_info = email_service.get_user_info()
            if user_info:
                print(f"✅ User: {user_info.get('displayName', 'Unknown')}")
                print(f"✅ Email: {user_info.get('mail', 'Unknown')}")
            
            # Test email reading
            print("\n🔧 Testing email reading...")
            emails = email_service.get_emails(top=3)
            if emails:
                print(f"✅ Found {len(emails)} emails!")
                for i, email in enumerate(emails[:2], 1):
                    print(f"   {i}. {email['subject'][:50]}...")
            else:
                print("⚠️  No emails found (inbox might be empty)")
                
        else:
            print("\n❌ Authentication failed - no token received")
            
    except Exception as e:
        print(f"\n❌ Error during authentication: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    main()
