#!/usr/bin/env python3
"""
Simple script to show the Microsoft authentication code clearly
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

def show_auth_code():
    """Show the authentication code clearly"""
    print("\n" + "="*60)
    print("🔐 MICROSOFT AUTHENTICATION CODE")
    print("="*60)
    
    # Initialize email service
    email_service = EmailService()
    
    # Get access token (this will show the code)
    print("📧 Getting authentication code...")
    print("   This will open a browser window for authentication.")
    print("   Please use the code shown below to authenticate.")
    print("\n" + "-"*60)
    
    token = email_service.get_access_token(open_browser=True)
    
    if token:
        print("\n✅ Authentication successful!")
        print("   You are now connected to the correct email account.")
    else:
        print("\n❌ Authentication failed!")
        print("   Please try again with the correct code.")

if __name__ == "__main__":
    show_auth_code()
