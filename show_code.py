#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.append(str(Path(__file__).parent))

from features.core_services.email_service import EmailService

def show_auth_code():
    print("\n" + "="*80)
    print("🔐 HANDYCONNECT AUTHENTICATION")
    print("="*80)
    print("📧 Account: Handymyjob@outlook.com")
    print("="*80)
    print("🔄 Starting authentication process...")
    print("   Please wait for the code to appear...")
    print("="*80)
    
    email_service = EmailService()
    
    # This will show the code in terminal
    token = email_service.get_access_token(open_browser=True)
    
    if token:
        print("\n" + "="*80)
        print("✅ SUCCESS! Authentication completed!")
        print("   Connected to: Handymyjob@outlook.com")
        print("   Application memory has been reset.")
        print("="*80)
        return True
    else:
        print("\n" + "="*80)
        print("❌ FAILED! Authentication unsuccessful.")
        print("   Please try again.")
        print("="*80)
        return False

if __name__ == "__main__":
    print("Starting authentication...")
    success = show_auth_code()
    
    if success:
        print("\n🎉 Ready to start the application!")
        print("   Run: python app.py")
    else:
        print("\n🔄 Please try again:")
        print("   Run: python show_code.py")
    
    # Keep terminal open
    input("\nPress Enter to exit...")
