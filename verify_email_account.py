#!/usr/bin/env python3
"""
Script to verify we're connected to the correct email account
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from features.core_services.email_service import EmailService

def verify_email_account():
    """Verify we're connected to the correct email account"""
    print("🔍 Verifying Email Account Connection")
    print("=" * 50)
    
    # Initialize email service
    email_service = EmailService()
    
    # Get access token
    print("📧 Getting access token...")
    token = email_service.get_access_token(open_browser=True)
    
    if not token:
        print("❌ Failed to get access token")
        return False
    
    print("✅ Access token obtained successfully")
    
    # Get user info to verify account
    print("\n👤 Getting user information...")
    user_info = email_service.get_user_info(token)
    
    if user_info:
        print(f"✅ Connected to account: {user_info.get('userPrincipalName', 'Unknown')}")
        print(f"   Display Name: {user_info.get('displayName', 'Unknown')}")
        print(f"   Mail: {user_info.get('mail', 'Unknown')}")
        
        # Check if this is the correct account
        email = user_info.get('userPrincipalName', '').lower()
        if 'handymyjob@outlook.com' in email:
            print("✅ CORRECT ACCOUNT: Handymyjob@outlook.com")
            return True
        else:
            print(f"❌ WRONG ACCOUNT: {email}")
            print("   Please re-authenticate with Handymyjob@outlook.com")
            return False
    else:
        print("❌ Failed to get user information")
        return False

if __name__ == "__main__":
    success = verify_email_account()
    if success:
        print("\n🎉 Email account verification successful!")
        print("   The application is now configured for Handymyjob@outlook.com")
    else:
        print("\n⚠️  Email account verification failed!")
        print("   Please ensure you authenticate with Handymyjob@outlook.com")
    
    sys.exit(0 if success else 1)
