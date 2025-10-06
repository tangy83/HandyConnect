import msal
import requests
import os
import webbrowser
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.authority = os.getenv('AUTHORITY', 'https://login.microsoftonline.com/consumers')
        self.scopes = os.getenv('SCOPES', 'User.Read Mail.Read Mail.Send').split()
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
            logger.error(f"Error getting user info: {e}")
            return None
    
    def get_emails_with_case_context(self, case_id: str = None, limit: int = 50) -> List[Dict]:
        """Get emails with case context information"""
        try:
            # Get basic emails
            emails = self.get_emails(limit=limit)
            if not emails:
                return []
            
            # If case_id is provided, filter emails for that case
            if case_id:
                # This would require integration with case service to get email IDs
                # For now, return all emails
                pass
            
            # Add case context to each email
            enriched_emails = []
            for email in emails:
                enriched_email = email.copy()
                
                # Add case context metadata
                enriched_email['case_context'] = {
                    'has_related_case': False,
                    'case_id': None,
                    'case_number': None,
                    'case_status': None,
                    'sla_status': None
                }
                
                enriched_emails.append(enriched_email)
            
            logger.info(f"Retrieved {len(enriched_emails)} emails with case context")
            return enriched_emails
            
        except Exception as e:
            logger.error(f"Error getting emails with case context: {e}")
            return []
    
    def send_email_response(self, case_id: str, response_text: str, 
                          recipient_email: str, subject: str = None, 
                          include_case_details: bool = True) -> bool:
        """Send email response for a case using Microsoft Graph API"""
        try:
            # Get access token
            access_token = self.get_access_token()
            if not access_token:
                logger.error("Failed to get access token for sending email")
                return False
            
            # Get case information for context
            case_context = self._get_case_context(case_id)
            if not case_context:
                logger.error(f"Case context not found for case {case_id}")
                return False
            
            # Prepare email content
            email_subject = subject or f"Re: {case_context.get('case_title', 'Case Update')}"
            
            # Build email body with optional case details
            email_body = response_text
            
            if include_case_details:
                case_details = f"""

---
Case Information:
- Case Number: {case_context.get('case_number', 'N/A')}
- Status: {case_context.get('status', 'N/A')}
- Priority: {case_context.get('priority', 'N/A')}

This email was sent from HandyConnect Case Management System.
If you have any questions, please reference the case number above in your reply.
"""
                email_body += case_details
            
            # Prepare the email message in Microsoft Graph format
            email_message = {
                "message": {
                    "subject": email_subject,
                    "body": {
                        "contentType": "Text",
                        "content": email_body
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": recipient_email
                            }
                        }
                    ]
                },
                "saveToSentItems": "true"
            }
            
            # Send email using Microsoft Graph API
            send_url = f"{self.graph_url}/me/sendMail"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(send_url, headers=headers, json=email_message)
            
            if response.status_code == 202:
                logger.info(f"✉️ Email sent successfully for case {case_context.get('case_number')} to {recipient_email}")
                
                # Log email to case threads
                self._log_outbound_email_to_thread(
                    case_id=case_id,
                    recipient_email=recipient_email,
                    subject=email_subject,
                    body=email_body
                )
                
                return True
            else:
                logger.error(f"Failed to send email. Status: {response.status_code}, Response: {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Error sending email response for case {case_id}: {e}")
            return False
    
    def _get_case_context(self, case_id: str) -> Optional[Dict]:
        """Get case context information"""
        try:
            # Import case service to get case information
            from .case_service import CaseService
            case_service = CaseService()
            
            case = case_service.get_case_by_id(case_id)
            if case:
                return {
                    'case_id': case.get('case_id'),
                    'case_number': case.get('case_number'),
                    'case_title': case.get('case_title'),
                    'status': case.get('status'),
                    'priority': case.get('priority'),
                    'assigned_to': case.get('assigned_to'),
                    'customer_info': case.get('customer_info', {}),
                    'sla_status': case.get('sla_status')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting case context for {case_id}: {e}")
            return None
    
    def get_case_email_thread(self, case_id: str) -> List[Dict]:
        """Get all emails related to a specific case"""
        try:
            # Get case information
            case_context = self._get_case_context(case_id)
            if not case_context:
                logger.error(f"Case context not found for case {case_id}")
                return []
            
            # Get customer email
            customer_email = case_context.get('customer_info', {}).get('email')
            if not customer_email:
                logger.error(f"Customer email not found for case {case_id}")
                return []
            
            # Get all emails and filter by customer email
            all_emails = self.get_emails(limit=100)
            case_emails = []
            
            for email in all_emails:
                sender_email = email.get('sender', {}).get('email', '').lower()
                if sender_email == customer_email.lower():
                    # Add case context to email
                    enriched_email = email.copy()
                    enriched_email['case_context'] = case_context
                    case_emails.append(enriched_email)
            
            # Sort by date (newest first)
            case_emails.sort(key=lambda x: x.get('receivedDateTime', ''), reverse=True)
            
            logger.info(f"Retrieved {len(case_emails)} emails for case {case_context.get('case_number')}")
            return case_emails
            
        except Exception as e:
            logger.error(f"Error getting case email thread for {case_id}: {e}")
            return []
    
    def _log_outbound_email_to_thread(self, case_id: str, recipient_email: str, 
                                     subject: str, body: str) -> None:
        """Log outbound manual email response to case threads"""
        try:
            from .case_service import CaseService
            from datetime import datetime
            
            case_service = CaseService()
            
            thread_data = {
                'direction': 'Outbound',
                'sender_name': 'HandyConnect Support',
                'sender_email': 'handymyjob@outlook.com',
                'subject': subject,
                'body': body,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            success = case_service.add_thread_to_case(case_id, thread_data)
            
            if success:
                logger.info(f"✅ Logged manual email response to case threads for case {case_id}")
            else:
                logger.warning(f"⚠️  Failed to log manual email response to threads for case {case_id}")
                
        except Exception as e:
            logger.error(f"Error logging outbound email thread for case {case_id}: {e}")


