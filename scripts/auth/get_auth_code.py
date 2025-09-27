#!/usr/bin/env python3
"""
Get Microsoft Authentication Code for Handymyjob@outlook.com
This script will show you the code to enter on Microsoft's website.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🔐 MICROSOFT AUTHENTICATION CODE")
    print("=" * 50)
    print()
    
    # Check if CLIENT_ID is available
    client_id = os.getenv('CLIENT_ID')
    if not client_id:
        print("❌ ERROR: CLIENT_ID not found in .env file")
        return
    
    print(f"✅ CLIENT_ID: {client_id[:8]}...")
    print()
    
    try:
        import msal
        
        # Configuration
        authority = 'https://login.microsoftonline.com/consumers'
        scopes = ['User.Read', 'Mail.Read']
        
        # Create MSAL app
        app = msal.PublicClientApplication(
            client_id=client_id,
            authority=authority
        )
        
        # Initiate device flow
        flow = app.initiate_device_flow(scopes=scopes)
        
        if "user_code" not in flow:
            print(f"❌ Device flow failed: {flow}")
            return
        
        # Display the authentication information
        print("🔑 AUTHENTICATION REQUIRED")
        print("-" * 30)
        print()
        print("1. Open this URL in your browser:")
        print(f"   {flow['verification_uri']}")
        print()
        print("2. Enter this code:")
        print(f"   {flow['user_code']}")
        print()
        print("3. Sign in with: Handymyjob@outlook.com")
        print()
        print("✅ Code generated successfully!")
        print("   Complete the authentication in your browser")
        
    except ImportError:
        print("❌ ERROR: MSAL library not found")
        print("Install with: pip install msal")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()
