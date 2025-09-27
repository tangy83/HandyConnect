#!/usr/bin/env python3
"""
Microsoft Authentication Code Generator for Handymyjob@outlook.com
This script will generate the authentication code you need to enter on Microsoft's website.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🔐 MICROSOFT AUTHENTICATION FOR HANDYMYJOB@OUTLOOK.COM")
    print("=" * 70)
    print()
    
    # Check if CLIENT_ID is available
    client_id = os.getenv('CLIENT_ID')
    if not client_id:
        print("❌ ERROR: CLIENT_ID not found in .env file")
        print("Please make sure your .env file contains:")
        print("CLIENT_ID=your_client_id_here")
        return
    
    print(f"✅ CLIENT_ID found: {client_id[:8]}...")
    print()
    
    try:
        import msal
        print("✅ MSAL library imported successfully")
    except ImportError:
        print("❌ ERROR: MSAL library not found")
        print("Please install it with: pip install msal")
        return
    
    # Configuration
    authority = os.getenv('AUTHORITY', 'https://login.microsoftonline.com/consumers')
    scopes = os.getenv('SCOPES', 'User.Read Mail.Read').split()
    
    print(f"✅ Authority: {authority}")
    print(f"✅ Scopes: {', '.join(scopes)}")
    print()
    
    # Create MSAL app
    try:
        app = msal.PublicClientApplication(
            client_id=client_id,
            authority=authority
        )
        print("✅ MSAL app created successfully")
    except Exception as e:
        print(f"❌ ERROR creating MSAL app: {e}")
        return
    
    print()
    print("🚀 STARTING DEVICE FLOW AUTHENTICATION")
    print("=" * 70)
    print()
    
    try:
        # Initiate device flow
        flow = app.initiate_device_flow(scopes=scopes)
        
        if "user_code" not in flow:
            print(f"❌ Device flow failed: {flow}")
            return
        
        # Display the authentication information
        print("🔑 AUTHENTICATION REQUIRED")
        print("-" * 40)
        print()
        print("1. Open this URL in your browser:")
        print(f"   {flow['verification_uri']}")
        print()
        print("2. Enter this code when prompted:")
        print(f"   {flow['user_code']}")
        print()
        print("3. Sign in with: Handymyjob@outlook.com")
        print()
        print("⏳ Waiting for authentication...")
        print("   (This may take up to 5 minutes)")
        print()
        
        # Try to open browser
        try:
            import webbrowser
            webbrowser.open(flow["verification_uri"])
            print("✅ Browser opened automatically")
        except:
            print("⚠️  Could not open browser automatically")
            print("   Please manually open the URL above")
        
        print()
        print("🔄 Polling for authentication result...")
        
        # Poll for result
        result = app.acquire_token_by_device_flow(flow)
        
        if "access_token" in result:
            print()
            print("🎉 AUTHENTICATION SUCCESSFUL!")
            print("=" * 70)
            print(f"✅ Token acquired: {result['access_token'][:50]}...")
            print()
            
            # Test the token by getting user info
            print("🔍 Testing connection...")
            try:
                import requests
                headers = {
                    'Authorization': f"Bearer {result['access_token']}",
                    'Content-Type': 'application/json'
                }
                
                # Get user info
                user_response = requests.get(
                    "https://graph.microsoft.com/v1.0/me?$select=displayName,userPrincipalName,mail",
                    headers=headers,
                    timeout=30
                )
                
                if user_response.status_code == 200:
                    user_info = user_response.json()
                    print(f"✅ User: {user_info.get('displayName', 'Unknown')}")
                    print(f"✅ Email: {user_info.get('userPrincipalName', 'Unknown')}")
                    print(f"✅ Mail: {user_info.get('mail', 'Unknown')}")
                    
                    # Check if it's the right account
                    email = user_info.get('userPrincipalName', '') or user_info.get('mail', '')
                    if 'handymyjob' in email.lower():
                        print()
                        print("🎯 SUCCESS! Connected to Handymyjob@outlook.com!")
                        print("✅ You can now use this account for email processing")
                    else:
                        print()
                        print(f"⚠️  WARNING: Connected to {email}")
                        print("   This is not the Handymyjob@outlook.com account")
                        print("   Please sign out and try again with the correct account")
                else:
                    print(f"❌ Failed to get user info: {user_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing connection: {e}")
                
        else:
            print()
            print("❌ AUTHENTICATION FAILED")
            print("=" * 70)
            print(f"Error: {result}")
            print()
            print("Possible reasons:")
            print("- You didn't complete the authentication in time")
            print("- You signed in with the wrong account")
            print("- The authentication code expired")
            print()
            print("Please try running this script again")
            
    except Exception as e:
        print(f"❌ ERROR during authentication: {e}")
        print()
        print("Please check your internet connection and try again")

if __name__ == "__main__":
    main()
