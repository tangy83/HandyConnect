"""
Acknowledgment Email Service for HandyConnect
Automatically sends tone-appropriate acknowledgment emails when cases are created
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AcknowledgmentService:
    """
    Service for sending automated case acknowledgment emails.
    Analyzes customer tone and sends appropriate response.
    """
    
    def __init__(self):
        from .llm_service import LLMService
        from .email_response_templates import EmailResponseTemplates
        from .email_service import EmailService
        
        self.llm_service = LLMService()
        self.templates = EmailResponseTemplates()
        self.email_service = EmailService()
        
        logger.info("AcknowledgmentService initialized")
    
    def send_acknowledgment(self, case_id: str, customer_email: str, 
                           original_email: Dict = None, case_data: Dict = None) -> bool:
        """
        Send automated acknowledgment email to customer.
        
        Args:
            case_id: The case ID
            customer_email: Customer's email address
            original_email: Original email data (for tone analysis)
            case_data: Case information
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            if not case_data:
                logger.error(f"Case data not provided for acknowledgment email (Case: {case_id})")
                return False
            
            # Step 1: Analyze customer tone from original email
            tone_analysis = self._analyze_customer_tone(original_email)
            logger.info(f"Tone analysis for case {case_id}: {tone_analysis['tone']} "
                       f"(urgency: {tone_analysis['urgency_level']}, "
                       f"confidence: {tone_analysis['confidence_score']:.2f})")
            
            # Step 2: Build email context from case data
            email_context = self._build_email_context(case_data, tone_analysis)
            
            # Step 3: Generate email using appropriate template
            email_body = self.templates.build_email_body(
                tone=tone_analysis['tone'],
                context=email_context
            )
            
            subject = self.templates.get_subject_line(
                tone=tone_analysis['tone'],
                case_number=case_data.get('case_number', 'N/A')
            )
            
            # Step 4: Send email via Microsoft Graph API
            email_sent = self._send_email(
                recipient_email=customer_email,
                subject=subject,
                body=email_body,
                case_id=case_id
            )
            
            if email_sent:
                # Step 5: Log acknowledgment in case timeline
                self._log_acknowledgment(case_id, customer_email, tone_analysis, subject)
                
                # Step 6: Log email to case threads
                self._log_thread(case_id, customer_email, subject, email_body)
                
                logger.info(f"✉️ Acknowledgment email sent for case {case_data.get('case_number')} "
                           f"to {customer_email} (tone: {tone_analysis['tone']})")
                return True
            else:
                logger.error(f"Failed to send acknowledgment email for case {case_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending acknowledgment for case {case_id}: {e}")
            return False
    
    def _analyze_customer_tone(self, original_email: Optional[Dict]) -> Dict:
        """Analyze tone from original customer email"""
        try:
            if not original_email:
                # Return default tone if no email provided
                return {
                    'tone': 'calm',
                    'urgency_level': 'medium',
                    'emotional_indicators': [],
                    'requires_immediate_attention': False,
                    'confidence_score': 0.5,
                    'empathy_required': False,
                    'response_priority': 'standard',
                    'tone_explanation': 'No email content available for analysis'
                }
            
            # Extract email content
            email_subject = original_email.get('subject', '')
            email_body = original_email.get('body', '')
            
            # Analyze tone using LLM service
            tone_analysis = self.llm_service.analyze_email_tone(
                email_content=email_body,
                email_subject=email_subject
            )
            
            return tone_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing customer tone: {e}")
            # Return safe default
            return {
                'tone': 'calm',
                'urgency_level': 'medium',
                'emotional_indicators': [],
                'requires_immediate_attention': False,
                'confidence_score': 0.5,
                'empathy_required': False,
                'response_priority': 'standard',
                'tone_explanation': 'Error during tone analysis'
            }
    
    def _build_email_context(self, case_data: Dict, tone_analysis: Dict) -> Dict:
        """Build email context from case data and tone analysis"""
        try:
            customer_info = case_data.get('customer_info', {})
            case_metadata = case_data.get('case_metadata', {})
            
            # Extract customer name
            customer_name = customer_info.get('name', 'Valued Customer')
            
            # Build brief summary
            brief_summary = case_data.get('case_title', 'Your request')
            if len(brief_summary) > 100:
                brief_summary = brief_summary[:97] + '...'
            
            # Build context dictionary
            context = {
                'customer_name': customer_name,
                'case_number': case_data.get('case_number', 'N/A'),
                'brief_summary': brief_summary,
                'case_type': case_data.get('case_type', 'General'),
                'priority': case_data.get('priority', 'Medium'),
                'status': case_data.get('status', 'New'),
                'urgency_level': tone_analysis.get('urgency_level', 'medium'),
                'property_number': customer_info.get('property_number'),
                'block_number': customer_info.get('block_number'),
                'property_address': customer_info.get('property_address'),
                'created_at': case_data.get('created_at', datetime.now().isoformat()),
                'sla_due_date': case_data.get('sla_due_date'),
                'tone': tone_analysis.get('tone', 'calm'),
                'empathy_required': tone_analysis.get('empathy_required', False),
                'requires_immediate_attention': tone_analysis.get('requires_immediate_attention', False)
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error building email context: {e}")
            return {
                'customer_name': 'Valued Customer',
                'case_number': case_data.get('case_number', 'N/A'),
                'brief_summary': 'Your request',
                'urgency_level': 'medium',
                'tone': 'calm'
            }
    
    def _send_email(self, recipient_email: str, subject: str, body: str, case_id: str) -> bool:
        """Send email using Microsoft Graph API"""
        try:
            # Use the email service to send via Graph API
            # Note: email_service.send_email_response expects case_id and formats with case details
            # For acknowledgment, we want to send the pre-formatted body as-is
            
            # Get access token
            access_token = self.email_service.get_access_token()
            if not access_token:
                logger.error("Failed to get access token for sending acknowledgment email")
                return False
            
            # Prepare email message for Microsoft Graph API
            import requests
            
            email_message = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "Text",
                        "content": body
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
            
            # Send email
            send_url = f"{self.email_service.graph_url}/me/sendMail"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(send_url, headers=headers, json=email_message)
            
            if response.status_code == 202:
                logger.info(f"✉️ Acknowledgment email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send acknowledgment email. Status: {response.status_code}, "
                           f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending acknowledgment email: {e}")
            return False
    
    def _log_acknowledgment(self, case_id: str, customer_email: str, 
                           tone_analysis: Dict, subject: str) -> None:
        """Log acknowledgment email sending in case timeline"""
        try:
            from .case_service import CaseService
            
            case_service = CaseService()
            cases = case_service.load_cases()
            
            # Find the case
            for case in cases:
                if case.get('case_id') == case_id:
                    # Create timeline event
                    import uuid
                    timeline_event = {
                        'event_id': str(uuid.uuid4()),
                        'event_type': 'acknowledgment_email_sent',
                        'timestamp': datetime.utcnow().isoformat(),
                        'actor': 'system',
                        'description': f'Acknowledgment email sent to customer ({tone_analysis["tone"]} tone)',
                        'metadata': {
                            'recipient': customer_email,
                            'subject': subject,
                            'tone': tone_analysis['tone'],
                            'urgency_level': tone_analysis['urgency_level'],
                            'confidence_score': tone_analysis['confidence_score'],
                            'empathy_required': tone_analysis.get('empathy_required', False)
                        }
                    }
                    
                    # Add to case timeline
                    if 'timeline' not in case:
                        case['timeline'] = []
                    case['timeline'].append(timeline_event)
                    
                    # Update case metadata
                    if 'case_metadata' not in case:
                        case['case_metadata'] = {}
                    case['case_metadata']['acknowledgment_sent'] = True
                    case['case_metadata']['acknowledgment_sent_at'] = datetime.utcnow().isoformat()
                    case['updated_at'] = datetime.utcnow().isoformat()
                    
                    # Save updated cases
                    case_service.save_cases(cases)
                    logger.info(f"Logged acknowledgment email in case timeline for {case_id}")
                    break
                    
        except Exception as e:
            logger.error(f"Error logging acknowledgment in timeline: {e}")
    
    def retry_failed_acknowledgment(self, case_id: str, max_retries: int = 3) -> bool:
        """
        Retry sending acknowledgment email for failed attempts.
        
        Args:
            case_id: The case ID
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if successful on retry, False otherwise
        """
        try:
            from .case_service import CaseService
            import time
            
            case_service = CaseService()
            case = case_service.get_case_by_id(case_id)
            
            if not case:
                logger.error(f"Case not found for retry: {case_id}")
                return False
            
            customer_info = case.get('customer_info', {})
            customer_email = customer_info.get('email')
            
            if not customer_email:
                logger.error(f"No customer email found for case {case_id}")
                return False
            
            # Retry with exponential backoff
            for attempt in range(max_retries):
                logger.info(f"Retry attempt {attempt + 1}/{max_retries} for case {case_id}")
                
                success = self.send_acknowledgment(
                    case_id=case_id,
                    customer_email=customer_email,
                    original_email=None,  # Won't be available for retry
                    case_data=case
                )
                
                if success:
                    logger.info(f"Acknowledgment email sent successfully on retry {attempt + 1}")
                    return True
                
                # Wait before retry (exponential backoff: 1s, 2s, 4s)
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
            
            logger.error(f"Failed to send acknowledgment after {max_retries} retries")
            return False
            
        except Exception as e:
            logger.error(f"Error retrying acknowledgment for case {case_id}: {e}")
            return False
    
    def get_acknowledgment_status(self, case_id: str) -> Dict:
        """
        Get acknowledgment email status for a case.
        
        Returns:
            Dictionary with acknowledgment status information
        """
        try:
            from .case_service import CaseService
            
            case_service = CaseService()
            case = case_service.get_case_by_id(case_id)
            
            if not case:
                return {'sent': False, 'error': 'Case not found'}
            
            case_metadata = case.get('case_metadata', {})
            
            return {
                'sent': case_metadata.get('acknowledgment_sent', False),
                'sent_at': case_metadata.get('acknowledgment_sent_at'),
                'case_number': case.get('case_number'),
                'customer_email': case.get('customer_info', {}).get('email')
            }
            
        except Exception as e:
            logger.error(f"Error getting acknowledgment status: {e}")
            return {'sent': False, 'error': str(e)}
    
    def _log_thread(self, case_id: str, customer_email: str, subject: str, body: str) -> None:
        """Log acknowledgment email to case threads"""
        try:
            from .case_service import CaseService
            
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
                logger.info(f"✅ Logged acknowledgment email to case threads for case {case_id}")
            else:
                logger.warning(f"⚠️  Failed to log acknowledgment email to threads for case {case_id}")
                
        except Exception as e:
            logger.error(f"Error logging thread for case {case_id}: {e}")

