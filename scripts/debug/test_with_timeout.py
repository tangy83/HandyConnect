#!/usr/bin/env python3
"""
Test with timeout to see what's happening
"""

import os
import sys
import signal
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def timeout_handler(signum, frame):
    print("\n⏰ Timeout reached! The process was taking too long.")
    print("This suggests the device flow authentication is waiting for user interaction.")
    sys.exit(1)

# Set a timeout of 30 seconds
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)

try:
    print("🚀 Starting timeout test...")
    
    from features.core_services.email_service import EmailService
    print("✅ EmailService imported")
    
    email_service = EmailService()
    print("✅ EmailService created")
    
    print("🔧 Attempting token acquisition with 30-second timeout...")
    print("⚠️  If this hangs, it means device flow is waiting for browser interaction...")
    
    token = email_service.get_access_token()
    
    if token:
        print(f"✅ Token acquired: {token[:20]}...")
    else:
        print("❌ Token acquisition returned None")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    signal.alarm(0)  # Cancel the alarm
    print("🎉 Test completed!")
