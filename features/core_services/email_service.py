import msal
import requests
import os
import webbrowser
from pathlib import Path
from datetime import datetime, timedelta

class EmailService:
    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.authority = os.getenv('AUTHORITY', 'https://login.microsoftonline.com/consumers')
        self.scopes = os.getenv('SCOPES', 'User.Read Mail.Read').split()
        self.token_cache_path = Path('.token_cache.bin')
        self.graph_url = "https://graph.microsoft.com/v1.0"
        
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
                
                print(f"\n" + "="*60)
                print(f"🔐 MICROSOFT AUTHENTICATION CODE")
                print(f"="*60)
                print(f"🌐 Open this URL: {flow['verification_uri']}")
                print(f"🔑 Enter this code: {flow['user_code']}")
                print(f"="*60)
                
                # Store auth info for web display
                global auth_info
                if 'auth_info' in globals():
                    auth_info['verification_uri'] = flow['verification_uri']
                    auth_info['user_code'] = flow['user_code']
                    auth_info['status'] = 'connecting'
                    auth_info['message'] = f'Enter code: {flow["user_code"]}'
                
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
    
    def get_emails(self, folder='Inbox', top=50):
        """Fetch emails from Outlook using Microsoft Graph API"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return []
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Use the working approach from friend's code
            url = f"{self.graph_url}/me/messages"
            params = {
                '$top': top,
                '$orderby': 'receivedDateTime desc',
                '$select': 'id,subject,from,receivedDateTime,bodyPreview,isRead,importance'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            emails_data = response.json()
            emails = []
            
            for item in emails_data.get('value', []):
                email = {
                    'id': item.get('id'),
                    'subject': item.get('subject', 'No Subject'),
                    'sender': {
                        'name': item.get('from', {}).get('emailAddress', {}).get('name', 'Unknown'),
                        'email': item.get('from', {}).get('emailAddress', {}).get('address', 'unknown@example.com')
                    },
                    'body': item.get('bodyPreview', ''),
                    'received_date': item.get('receivedDateTime'),
                    'importance': item.get('importance', 'normal'),
                    'is_read': item.get('isRead', True)
                }
                emails.append(email)
            
            return emails
                
        except Exception as e:
            print(f"Error in get_emails: {e}")
            return []
    
    def get_email_body(self, message_id):
        """Get full email body for a specific message ID"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.graph_url}/me/messages/{message_id}"
            params = {
                '$select': 'body,subject,from,receivedDateTime'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('body', {}).get('content', '')
                
        except Exception as e:
            print(f"Error in get_email_body: {e}")
            return None
    
    def get_user_info(self):
        """Get user information"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.graph_url}/me?$select=displayName,userPrincipalName,mail"
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
                
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None


