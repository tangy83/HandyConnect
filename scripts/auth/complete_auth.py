#!/usr/bin/env python3
"""
Complete authentication process for Handymyjob@outlook.com
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🔐 COMPLETE AUTHENTICATION FOR HANDYMYJOB@OUTLOOK.COM")
    print("=" * 70)
    print()
    
    client_id = os.getenv('CLIENT_ID')
    if not client_id:
        print("❌ CLIENT_ID not found")
        return
    
    try:
        import msal
        import requests
        
        # Create app
        app = msal.PublicClientApplication(
            client_id=client_id,
            authority='https://login.microsoftonline.com/consumers'
        )
        
        # Check for existing accounts
        accounts = app.get_accounts()
        if accounts:
            print(f"✅ Found {len(accounts)} existing account(s)")
            for account in accounts:
                print(f"   - {account.get('username', 'Unknown')}")
        
        # Try to get token silently first
        result = None
        if accounts:
            result = app.acquire_token_silent(['User.Read', 'Mail.Read'], account=accounts[0])
        
        # If no token, start device flow
        if not result or 'access_token' not in result:
            print("\n🔧 Starting device flow authentication...")
            flow = app.initiate_device_flow(scopes=['User.Read', 'Mail.Read'])
            
            if "user_code" not in flow:
                print(f"❌ Device flow failed: {flow}")
                return
            
            print("\n🔑 AUTHENTICATION REQUIRED")
            print("-" * 40)
            print(f"1. Open: {flow['verification_uri']}")
            print(f"2. Enter code: {flow['user_code']}")
            print("3. Sign in with: Handymyjob@outlook.com")
            print()
            
            # Try to open browser
            try:
                import webbrowser
                webbrowser.open(flow["verification_uri"])
                print("✅ Browser opened automatically")
            except:
                print("⚠️  Please open the URL manually")
            
            print("\n⏳ Waiting for authentication...")
            result = app.acquire_token_by_device_flow(flow)
        
        if result and 'access_token' in result:
            print("\n🎉 AUTHENTICATION SUCCESSFUL!")
            print("=" * 70)
            
            # Test the token
            headers = {
                'Authorization': f"Bearer {result['access_token']}",
                'Content-Type': 'application/json'
            }
            
            # Get user info
            print("🔍 Testing connection...")
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me?$select=displayName,userPrincipalName,mail",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ User: {user_info.get('displayName', 'Unknown')}")
                print(f"✅ Email: {user_info.get('userPrincipalName', 'Unknown')}")
                
                email = user_info.get('userPrincipalName', '') or user_info.get('mail', '')
                if 'handymyjob' in email.lower():
                    print("\n🎯 SUCCESS! Connected to Handymyjob@outlook.com!")
                    
                    # Test email reading
                    print("\n📧 Testing email reading...")
                    email_response = requests.get(
                        "https://graph.microsoft.com/v1.0/me/messages?$top=5",
                        headers=headers,
                        timeout=30
                    )
                    
                    if email_response.status_code == 200:
                        emails = email_response.json().get('value', [])
                        print(f"✅ Found {len(emails)} emails!")
                        for i, email in enumerate(emails[:3], 1):
                            print(f"  {i}. {email.get('subject', 'No subject')}")
                        
                        print("\n🎉 EMAIL INTEGRATION IS READY!")
                        print("✅ You can now send emails to Handymyjob@outlook.com")
                        print("✅ The application will process them automatically")
                    else:
                        print(f"❌ Failed to read emails: {email_response.status_code}")
                else:
                    print(f"\n⚠️  WARNING: Connected to {email}")
                    print("   This is not the Handymyjob@outlook.com account")
            else:
                print(f"❌ Failed to get user info: {response.status_code}")
        else:
            print("\n❌ AUTHENTICATION FAILED")
            print(f"Error: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
