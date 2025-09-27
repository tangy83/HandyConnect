#!/usr/bin/env python3
"""
Script to get and display Microsoft authentication code clearly
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from features.core_services.email_service import EmailService

def get_auth_code():
    """Get and display the authentication code"""
    print("\n" + "="*70)
    print("🔐 MICROSOFT AUTHENTICATION FOR HANDYCONNECT")
    print("="*70)
    print("📧 Connecting to: Handymyjob@outlook.com")
    print("🌐 This will open a browser window for authentication")
    print("="*70)
    
    # Initialize email service
    email_service = EmailService()
    
    try:
        # Get access token (this will show the code)
        print("\n🔄 Initiating authentication...")
        print("   Please wait for the authentication code to appear...")
        print("\n" + "-"*70)
        
        # This will display the code and open browser
        token = email_service.get_access_token(open_browser=True)
        
        if token:
            print("\n" + "="*70)
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print("   You are now connected to Handymyjob@outlook.com")
            print("   The application memory has been reset.")
            print("="*70)
            return True
        else:
            print("\n" + "="*70)
            print("❌ AUTHENTICATION FAILED!")
            print("   Please try again with the correct code.")
            print("="*70)
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Authentication cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Error during authentication: {e}")
        return False

if __name__ == "__main__":
    print("Starting authentication process...")
    success = get_auth_code()
    
    if success:
        print("\n🎉 Ready to start the application!")
        print("   Run: python app.py")
    else:
        print("\n🔄 Please try again:")
        print("   Run: python get_auth_code.py")
    
    # Keep the script running so you can see the output
    input("\nPress Enter to exit...")
