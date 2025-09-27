#!/usr/bin/env python3
"""
Test authentication with Handymyjob@outlook.com account
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from features.core_services.email_service import EmailService

def test_new_account():
    print("🔐 Testing authentication with Handymyjob@outlook.com")
    print("=" * 60)
    
    try:
        # Create email service
        email_service = EmailService()
        print("✅ EmailService created successfully")
        
        # Test authentication
        print("\n🔧 Starting authentication process...")
        print("⚠️  This will open a browser window and show you a code.")
        print("⚠️  Make sure to sign in with Handymyjob@outlook.com account!")
        print("\n" + "=" * 60)
        print("🚨 AUTHENTICATION CODE WILL APPEAR BELOW:")
        print("=" * 60)
        
        # Get access token
        token = email_service.get_access_token()
        
        if token:
            print(f"\n✅ AUTHENTICATION SUCCESSFUL!")
            print(f"Token acquired: {token[:50]}...")
            
            # Test user info
            print("\n🔍 Testing user info...")
            user_info = email_service.get_user_info()
            if user_info:
                print(f"✅ User: {user_info.get('displayName', 'Unknown')}")
                print(f"✅ Email: {user_info.get('userPrincipalName', 'Unknown')}")
                print(f"✅ Mail: {user_info.get('mail', 'Unknown')}")
                
                # Check if it's the right account
                email = user_info.get('userPrincipalName', '') or user_info.get('mail', '')
                if 'handymyjob' in email.lower():
                    print("\n🎉 SUCCESS! Connected to Handymyjob@outlook.com account!")
                else:
                    print(f"\n⚠️  WARNING: Connected to {email}, not Handymyjob@outlook.com")
            else:
                print("❌ Failed to get user info")
                
            # Test email reading
            print("\n📧 Testing email reading...")
            emails = email_service.get_emails(top=5)
            if emails:
                print(f"✅ Found {len(emails)} emails!")
                for i, email in enumerate(emails[:3], 1):
                    print(f"{i}. {email.get('subject', 'No subject')}")
            else:
                print("❌ No emails found")
                
        else:
            print("❌ Authentication failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test completed!")

if __name__ == "__main__":
    test_new_account()
