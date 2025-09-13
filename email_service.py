import msal
import requests
import os
from datetime import datetime, timedelta

class EmailService:
    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.tenant_id = os.getenv('TENANT_ID')
        self.scope = os.getenv('SCOPE', 'https://graph.microsoft.com/.default')
        self.graph_url = "https://graph.microsoft.com/v1.0"
        
    def get_access_token(self):
        """Get access token using client credentials flow"""
        try:
            authority = f"https://login.microsoftonline.com/{self.tenant_id}"
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=authority,
                client_credential=self.client_secret
            )
            
            result = app.acquire_token_silent([self.scope], account=None)
            if not result:
                result = app.acquire_token_for_client(scopes=[self.scope])
            
            if "access_token" in result:
                return result["access_token"]
            else:
                raise Exception(f"Error getting access token: {result.get('error_description')}")
                
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
            
            # Get emails from the last 24 hours
            since_time = datetime.utcnow() - timedelta(hours=24)
            filter_param = f"receivedDateTime ge {since_time.isoformat()}Z"
            
            url = f"{self.graph_url}/me/mailFolders/{folder}/messages"
            params = {
                '$filter': filter_param,
                '$top': top,
                '$orderby': 'receivedDateTime desc',
                '$select': 'id,subject,from,bodyPreview,receivedDateTime,importance'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
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
                        'importance': item.get('importance', 'normal')
                    }
                    emails.append(email)
                
                return emails
            else:
                print(f"Error fetching emails: {response.status_code} - {response.text}")
                return []
                
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
                '$select': 'body'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('body', {}).get('content', '')
            else:
                print(f"Error fetching email body: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in get_email_body: {e}")
            return None
