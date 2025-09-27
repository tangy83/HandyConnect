#!/usr/bin/env python3
"""
Show Microsoft Authentication Code for Handymyjob@outlook.com
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("\n" + "="*80)
    print("🔐 MICROSOFT AUTHENTICATION FOR HANDYMYJOB@OUTLOOK.COM")
    print("="*80)
    print()
    
    client_id = os.getenv('CLIENT_ID')
    if not client_id:
        print("❌ ERROR: CLIENT_ID not found in .env file")
        return
    
    try:
        import msal
        
        # Create app
        app = msal.PublicClientApplication(
            client_id=client_id,
            authority='https://login.microsoftonline.com/consumers'
        )
        
        # Start device flow
        flow = app.initiate_device_flow(scopes=['User.Read', 'Mail.Read'])
        
        if "user_code" not in flow:
            print(f"❌ Device flow failed: {flow}")
            return
        
        print("🔑 AUTHENTICATION REQUIRED")
        print("-" * 50)
        print()
        print("STEP 1: Open this URL in your browser:")
        print()
        print(f"   🌐 {flow['verification_uri']}")
        print()
        print("STEP 2: Enter this code when prompted:")
        print()
        print(f"   🔢 {flow['user_code']}")
        print()
        print("STEP 3: Sign in with: Handymyjob@outlook.com")
        print()
        print("="*80)
        print("⚠️  IMPORTANT: Make sure to sign in with Handymyjob@outlook.com")
        print("   (NOT your personal Hotmail account)")
        print("="*80)
        print()
        
        # Try to open browser
        try:
            import webbrowser
            webbrowser.open(flow["verification_uri"])
            print("✅ Browser opened automatically")
        except:
            print("⚠️  Please open the URL manually")
        
        print("\n⏳ Waiting for you to complete authentication...")
        print("   (This will wait for up to 5 minutes)")
        print()
        
        # Wait for authentication
        result = app.acquire_token_by_device_flow(flow)
        
        if result and 'access_token' in result:
            print("\n🎉 AUTHENTICATION SUCCESSFUL!")
            print("="*50)
            
            # Test the connection
            import requests
            headers = {
                'Authorization': f"Bearer {result['access_token']}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me?$select=displayName,userPrincipalName,mail",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_info = response.json()
                email = user_info.get('userPrincipalName', '') or user_info.get('mail', '')
                
                print(f"✅ User: {user_info.get('displayName', 'Unknown')}")
                print(f"✅ Email: {email}")
                
                if 'handymyjob' in email.lower():
                    print("\n🎯 SUCCESS! Connected to Handymyjob@outlook.com!")
                    print("✅ Email integration is now ready!")
                    print("✅ You can send emails to Handymyjob@outlook.com")
                else:
                    print(f"\n⚠️  WARNING: Connected to {email}")
                    print("   This is not the Handymyjob@outlook.com account")
            else:
                print(f"❌ Failed to verify connection: {response.status_code}")
        else:
            print("\n❌ AUTHENTICATION FAILED")
            print("Please try again")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
