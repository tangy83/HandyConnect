#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv('CLIENT_ID')
if not client_id:
    print("❌ CLIENT_ID not found")
    exit(1)

import msal

app = msal.PublicClientApplication(
    client_id=client_id,
    authority='https://login.microsoftonline.com/consumers'
)

flow = app.initiate_device_flow(scopes=['User.Read', 'Mail.Read'])

if "user_code" in flow:
    print("\n" + "="*60)
    print("🔐 MICROSOFT AUTHENTICATION CODE")
    print("="*60)
    print()
    print("1. Open this URL:")
    print(f"   {flow['verification_uri']}")
    print()
    print("2. Enter this code:")
    print(f"   {flow['user_code']}")
    print()
    print("3. Sign in with: Handymyjob@outlook.com")
    print("="*60)
else:
    print(f"❌ Error: {flow}")
