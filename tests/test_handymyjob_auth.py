#!/usr/bin/env python3
"""
Test authentication with Handymyjob@outlook.com account
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_auth():
    print("🔐 Testing Handymyjob@outlook.com Authentication")
    print("=" * 60)
    
    # Check environment
    client_id = os.getenv('CLIENT_ID')
    print(f"CLIENT_ID: {client_id[:8] if client_id else 'None'}...")
    
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
        
        # Try to get token silently first (from cache)
        accounts = app.get_accounts()
        if accounts:
            print(f"✅ Found {len(accounts)} cached account(s)")
            result = app.acquire_token_silent(['User.Read', 'Mail.Read'], account=accounts[0])
            
            if result and 'access_token' in result:
                print("✅ Token acquired from cache!")
                
                # Test the token
                headers = {
                    'Authorization': f"Bearer {result['access_token']}",
                    'Content-Type': 'application/json'
                }
                
                # Get user info
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
                        print("🎉 SUCCESS! Connected to Handymyjob@outlook.com!")
                        
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
                        else:
                            print(f"❌ Failed to read emails: {email_response.status_code}")
                    else:
                        print(f"⚠️  Connected to {email}, not Handymyjob@outlook.com")
                else:
                    print(f"❌ Failed to get user info: {response.status_code}")
            else:
                print("❌ No valid token in cache")
        else:
            print("❌ No cached accounts found")
            print("You may need to authenticate again")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth()
