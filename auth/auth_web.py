#!/usr/bin/env python3
"""
Web-based authentication code display - FIXED VERSION
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template_string, jsonify, request
import msal

load_dotenv()
sys.path.append(str(Path(__file__).parent))

from features.core_services.email_service import EmailService

app = Flask(__name__)

# Global variables to store auth info
auth_info = {
    'status': 'waiting',
    'verification_uri': '',
    'user_code': '',
    'message': 'Initializing authentication...'
}

def start_auth_process():
    """Start the authentication process in a separate thread"""
    global auth_info
    
    try:
        print("🔄 Starting authentication process...")
        auth_info['status'] = 'connecting'
        auth_info['message'] = 'Connecting to Microsoft...'
        
        email_service = EmailService()
        
        # Get access token (this will show the code)
        print("📧 Getting access token...")
        token = email_service.get_access_token(open_browser=True)
        
        if token:
            print("✅ Authentication successful!")
            auth_info['status'] = 'success'
            auth_info['message'] = '✅ Authentication successful! Connected to Handymyjob@outlook.com'
        else:
            print("❌ Authentication failed!")
            auth_info['status'] = 'failed'
            auth_info['message'] = '❌ Authentication failed. Please try again.'
            
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        auth_info['status'] = 'error'
        auth_info['message'] = f'❌ Error: {str(e)}'

# Custom email service that updates the web display
class WebEmailService(EmailService):
    def get_access_token(self, open_browser=False):
        """Get access token using device flow (delegated permissions)"""
        try:
            if not self.client_id:
                print("Missing CLIENT_ID in .env file")
                return None
            
            # Load token cache
            cache = msal.SerializableTokenCache()
            if self.token_cache_path.exists():
                try:
                    cache.deserialize(self.token_cache_path.read_text())
                except Exception:
                    pass
            
            # Create app instance
            app = msal.PublicClientApplication(
                self.client_id, 
                authority=self.authority, 
                token_cache=cache
            )
            
            # Try to get token silently first
            accounts = app.get_accounts()
            result = app.acquire_token_silent(self.scopes, account=accounts[0]) if accounts else None
            
            if not result:
                # Use device flow for authentication
                flow = app.initiate_device_flow(scopes=self.scopes)
                if "user_code" not in flow:
                    print(f"Device flow failed: {flow}")
                    return None
                
                # Update web display with auth info
                global auth_info
                auth_info['verification_uri'] = flow['verification_uri']
                auth_info['user_code'] = flow['user_code']
                auth_info['status'] = 'connecting'
                auth_info['message'] = f'Enter this code: {flow["user_code"]}'
                
                print(f"\n" + "="*60)
                print(f"🔐 MICROSOFT AUTHENTICATION CODE")
                print(f"="*60)
                print(f"🌐 Open this URL: {flow['verification_uri']}")
                print(f"🔑 Enter this code: {flow['user_code']}")
                print(f"="*60)
                
                # Only open browser if explicitly requested
                if open_browser:
                    try:
                        webbrowser.open(flow["verification_uri"])
                    except:
                        pass
                
                result = app.acquire_token_by_device_flow(flow)
            
            # Save token cache
            if cache.has_state_changed:
                self.token_cache_path.write_text(cache.serialize())
            
            if "access_token" not in result:
                print(f"Authentication error: {result}")
                return None
            
            return result["access_token"]
                
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None

@app.route('/')
def auth_display():
    """Display the authentication page"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HandyConnect Authentication</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 600px;
                width: 100%;
            }
            .header {
                color: #333;
                margin-bottom: 30px;
            }
            .code-display {
                background: #f8f9fa;
                border: 3px solid #007bff;
                border-radius: 15px;
                padding: 40px;
                margin: 20px 0;
                font-size: 36px;
                font-weight: bold;
                color: #007bff;
                letter-spacing: 5px;
                font-family: 'Courier New', monospace;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .status {
                margin: 20px 0;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 18px;
            }
            .waiting { background: #fff3cd; color: #856404; }
            .connecting { background: #d1ecf1; color: #0c5460; }
            .success { background: #d4edda; color: #155724; }
            .failed { background: #f8d7da; color: #721c24; }
            .error { background: #f8d7da; color: #721c24; }
            .instructions {
                background: #e7f3ff;
                border-left: 4px solid #007bff;
                padding: 20px;
                margin: 20px 0;
                text-align: left;
            }
            .refresh-btn {
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
            }
            .refresh-btn:hover {
                background: #0056b3;
            }
            .url-display {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
                font-family: monospace;
                word-break: break-all;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🔐 HandyConnect Authentication</h1>
            <p><strong>Account:</strong> Handymyjob@outlook.com</p>
            
            <div class="instructions">
                <h3>📋 Instructions:</h3>
                <ol>
                    <li>Wait for the authentication code to appear below</li>
                    <li>A Microsoft login page will open in your browser</li>
                    <li>Enter the code shown below on the Microsoft page</li>
                    <li>Sign in with <strong>Handymyjob@outlook.com</strong></li>
                    <li>Grant the required permissions</li>
                </ol>
            </div>
            
            <div id="status" class="status {{ status_class }}">
                {{ message }}
            </div>
            
            {% if user_code %}
            <div class="code-display">
                {{ user_code }}
            </div>
            <p><strong>🔑 Enter this code on the Microsoft page</strong></p>
            {% endif %}
            
            {% if verification_uri %}
            <div class="url-display">
                <strong>🌐 Microsoft URL:</strong><br>
                {{ verification_uri }}
            </div>
            {% endif %}
            
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Status</button>
            {% if verification_uri %}
            <button class="refresh-btn" onclick="window.open('{{ verification_uri }}', '_blank')">🌐 Open Microsoft Login</button>
            {% endif %}
        </div>
        
        <script>
            // Auto-refresh every 3 seconds
            setTimeout(function() {
                location.reload();
            }, 3000);
        </script>
    </body>
    </html>
    """
    
    status_class = auth_info['status']
    return render_template_string(template, 
                                message=auth_info['message'],
                                user_code=auth_info['user_code'],
                                verification_uri=auth_info['verification_uri'],
                                status_class=status_class)

@app.route('/api/status')
def get_status():
    """Get current authentication status"""
    return jsonify(auth_info)

def start_auth():
    """Start authentication process"""
    global auth_info
    try:
        print("🔄 Starting authentication process...")
        auth_info['status'] = 'connecting'
        auth_info['message'] = 'Connecting to Microsoft...'
        
        email_service = WebEmailService()
        token = email_service.get_access_token(open_browser=True)
        
        if token:
            print("✅ Authentication successful!")
            auth_info['status'] = 'success'
            auth_info['message'] = '✅ Authentication successful! Connected to Handymyjob@outlook.com'
        else:
            print("❌ Authentication failed!")
            auth_info['status'] = 'failed'
            auth_info['message'] = '❌ Authentication failed. Please try again.'
            
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        auth_info['status'] = 'error'
        auth_info['message'] = f'❌ Error: {str(e)}'

if __name__ == '__main__':
    print("🚀 Starting HandyConnect Authentication Display")
    print("=" * 50)
    print("📧 Account: Handymyjob@outlook.com")
    print("🌐 Web interface: http://localhost:5002")
    print("=" * 50)
    
    # Start authentication in background thread
    auth_thread = threading.Thread(target=start_auth)
    auth_thread.daemon = True
    auth_thread.start()
    
    # Start web server
    app.run(host='0.0.0.0', port=5002, debug=False)
