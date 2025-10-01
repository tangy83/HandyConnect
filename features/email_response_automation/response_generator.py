#!/usr/bin/env python3
"""
Email Response Generator for HandyConnect Phase 12
Advanced AI-powered email response automation
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import openai

logger = logging.getLogger(__name__)

@dataclass
class EmailResponse:
    """Email response data structure"""
    id: str
    task_id: str
    recipient_email: str
    subject: str
    body: str
    response_type: str  # acknowledgment, information_request, resolution, escalation, follow_up, closure
    priority: str
    tone: str  # professional, friendly, urgent, apologetic
    language: str
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: str = "draft"  # draft, scheduled, sent, failed
    metadata: Dict[str, Any] = None

@dataclass
class ResponseTemplate:
    """Email response template"""
    id: str
    name: str
    response_type: str
    subject_template: str
    body_template: str
    tone: str
    language: str
    variables: List[str]
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

class ResponseGenerator:
    """Advanced AI-powered email response generator"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.templates = self._load_templates()
        self.response_history = []
        
    def _load_templates(self) -> Dict[str, ResponseTemplate]:
        """Load response templates from storage"""
        templates = {}
        
        # Default templates
        default_templates = [
            ResponseTemplate(
                id="acknowledgment",
                name="Acknowledgment Response",
                response_type="acknowledgment",
                subject_template="Re: {original_subject} - We've received your request",
                body_template="""Dear {customer_name},

Thank you for contacting us regarding {issue_summary}. We have received your request and it has been assigned case number {case_id}.

Our team will review your request and respond within {response_time}. We appreciate your patience.

If you have any urgent concerns, please don't hesitate to contact us directly.

Best regards,
HandyConnect Support Team""",
                tone="professional",
                language="en",
                variables=["customer_name", "issue_summary", "case_id", "response_time"]
            ),
            ResponseTemplate(
                id="information_request",
                name="Information Request Response",
                response_type="information_request",
                subject_template="Re: {original_subject} - Additional Information Needed",
                body_template="""Dear {customer_name},

Thank you for your request regarding {issue_summary}. To better assist you, we need some additional information:

{information_needed}

Please provide this information at your earliest convenience so we can proceed with resolving your request.

Best regards,
HandyConnect Support Team""",
                tone="professional",
                language="en",
                variables=["customer_name", "issue_summary", "information_needed"]
            ),
            ResponseTemplate(
                id="resolution",
                name="Resolution Response",
                response_type="resolution",
                subject_template="Re: {original_subject} - Issue Resolved",
                body_template="""Dear {customer_name},

Good news! We have resolved your request regarding {issue_summary}.

{solution_details}

If you have any questions or if the issue persists, please don't hesitate to contact us.

Thank you for choosing HandyConnect.

Best regards,
HandyConnect Support Team""",
                tone="professional",
                language="en",
                variables=["customer_name", "issue_summary", "solution_details"]
            ),
            ResponseTemplate(
                id="escalation",
                name="Escalation Response",
                response_type="escalation",
                subject_template="Re: {original_subject} - Escalated to Specialized Team",
                body_template="""Dear {customer_name},

Thank you for your request regarding {issue_summary}. This matter has been escalated to our specialized {escalation_team} team for review.

Your case number is {case_id} and our specialized team will contact you within {escalation_time}.

We appreciate your patience as we work to provide you with the best possible solution.

Best regards,
HandyConnect Support Team""",
                tone="professional",
                language="en",
                variables=["customer_name", "issue_summary", "escalation_team", "case_id", "escalation_time"]
            )
        ]
        
        for template in default_templates:
            templates[template.id] = template
            
        return templates
    
    def generate_response(self, task_data: Dict[str, Any], response_type: str = None) -> EmailResponse:
        """Generate an AI-powered email response"""
        try:
            # Determine response type if not specified
            if not response_type:
                response_type = self._determine_response_type(task_data)
            
            # Get appropriate template
            template = self._get_template(response_type, task_data)
            
            # Generate response using AI
            response_content = self._generate_with_ai(task_data, template)
            
            # Create response object
            response = EmailResponse(
                id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_data.get('id', 'unknown')}",
                task_id=task_data.get('id', ''),
                recipient_email=task_data.get('sender', {}).get('email', ''),
                subject=response_content['subject'],
                body=response_content['body'],
                response_type=response_type,
                priority=task_data.get('priority', 'Medium'),
                tone=template.tone,
                language=template.language,
                created_at=datetime.now(timezone.utc),
                metadata={
                    'template_id': template.id,
                    'ai_generated': True,
                    'confidence_score': response_content.get('confidence', 0.8)
                }
            )
            
            # Store response history
            self.response_history.append(response)
            
            logger.info(f"Generated {response_type} response for task {task_data.get('id')}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def _determine_response_type(self, task_data: Dict[str, Any]) -> str:
        """Determine the most appropriate response type based on task data"""
        try:
            # Use AI to determine response type
            prompt = f"""
            Based on the following customer support task, determine the most appropriate response type:
            
            Task Data:
            - Summary: {task_data.get('summary', '')}
            - Category: {task_data.get('category', '')}
            - Priority: {task_data.get('priority', '')}
            - Status: {task_data.get('status', '')}
            - Sentiment: {task_data.get('sentiment', '')}
            
            Available response types:
            - acknowledgment: For new requests that need confirmation
            - information_request: When more details are needed
            - resolution: When the issue has been resolved
            - escalation: When the issue needs specialized attention
            - follow_up: For checking on progress
            - closure: For closing resolved cases
            
            Respond with just the response type name.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert customer service manager. Determine the most appropriate response type."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            response_type = response.choices[0].message.content.strip().lower()
            
            # Validate response type
            valid_types = ['acknowledgment', 'information_request', 'resolution', 'escalation', 'follow_up', 'closure']
            if response_type not in valid_types:
                response_type = 'acknowledgment'  # Default fallback
                
            return response_type
            
        except Exception as e:
            logger.error(f"Error determining response type: {e}")
            return 'acknowledgment'  # Default fallback
    
    def _get_template(self, response_type: str, task_data: Dict[str, Any]) -> ResponseTemplate:
        """Get the appropriate template for the response type"""
        # Try to get template by response type
        if response_type in self.templates:
            return self.templates[response_type]
        
        # Fallback to acknowledgment template
        return self.templates.get('acknowledgment', self.templates[list(self.templates.keys())[0]])
    
    def _generate_with_ai(self, task_data: Dict[str, Any], template: ResponseTemplate) -> Dict[str, str]:
        """Generate response content using AI"""
        try:
            # Extract customer name from email
            customer_name = self._extract_customer_name(task_data)
            
            # Prepare template variables
            template_vars = {
                'customer_name': customer_name,
                'original_subject': task_data.get('subject', 'Your Request'),
                'issue_summary': task_data.get('summary', 'your inquiry'),
                'case_id': task_data.get('id', 'N/A'),
                'response_time': self._get_response_time(task_data.get('priority', 'Medium')),
                'escalation_team': self._get_escalation_team(task_data.get('category', '')),
                'escalation_time': '2-4 hours',
                'information_needed': self._generate_information_request(task_data),
                'solution_details': self._generate_solution_details(task_data)
            }
            
            # Use AI to enhance the template
            prompt = f"""
            Generate a professional email response using the following template and context:
            
            Template:
            Subject: {template.subject_template}
            Body: {template.body_template}
            
            Task Context:
            - Customer: {customer_name}
            - Issue: {task_data.get('summary', '')}
            - Category: {task_data.get('category', '')}
            - Priority: {task_data.get('priority', '')}
            - Sentiment: {task_data.get('sentiment', '')}
            
            Template Variables:
            {json.dumps(template_vars, indent=2)}
            
            Please generate a professional email response that:
            1. Fills in the template variables appropriately
            2. Maintains the {template.tone} tone
            3. Is clear and helpful
            4. Includes any additional context that would be helpful
            
            Respond with a JSON object containing:
            {{
                "subject": "Generated subject line",
                "body": "Generated email body",
                "confidence": 0.0-1.0
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional customer service representative. Generate helpful and appropriate email responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                response_data = json.loads(content)
                return {
                    'subject': response_data.get('subject', template.subject_template.format(**template_vars)),
                    'body': response_data.get('body', template.body_template.format(**template_vars)),
                    'confidence': response_data.get('confidence', 0.8)
                }
            except json.JSONDecodeError:
                # Fallback to template formatting
                return {
                    'subject': template.subject_template.format(**template_vars),
                    'body': template.body_template.format(**template_vars),
                    'confidence': 0.6
                }
                
        except Exception as e:
            logger.error(f"Error generating with AI: {e}")
            # Fallback to basic template formatting
            return {
                'subject': f"Re: {task_data.get('subject', 'Your Request')}",
                'body': f"Dear Customer,\n\nThank you for your request. We are reviewing your inquiry and will respond soon.\n\nBest regards,\nHandyConnect Support Team",
                'confidence': 0.3
            }
    
    def _extract_customer_name(self, task_data: Dict[str, Any]) -> str:
        """Extract customer name from task data"""
        sender = task_data.get('sender', {})
        name = sender.get('name', '')
        if name:
            return name
        
        email = sender.get('email', '')
        if email:
            return email.split('@')[0].replace('.', ' ').title()
        
        return 'Customer'
    
    def _get_response_time(self, priority: str) -> str:
        """Get response time based on priority"""
        response_times = {
            'Urgent': '1 hour',
            'High': '4 hours',
            'Medium': '24 hours',
            'Low': '48 hours'
        }
        return response_times.get(priority, '24 hours')
    
    def _get_escalation_team(self, category: str) -> str:
        """Get escalation team based on category"""
        team_mapping = {
            'Technical Issue': 'Technical Support',
            'Billing Question': 'Billing Department',
            'Feature Request': 'Product Development',
            'Complaint': 'Customer Relations',
            'Account Issue': 'Account Management',
            'General Inquiry': 'General Support'
        }
        return team_mapping.get(category, 'Specialized Support')
    
    def _generate_information_request(self, task_data: Dict[str, Any]) -> str:
        """Generate information request details"""
        category = task_data.get('category', '')
        summary = task_data.get('summary', '')
        
        if 'billing' in category.lower():
            return "Please provide your account number, billing period, and any relevant payment information."
        elif 'technical' in category.lower():
            return "Please provide details about your device, browser, and any error messages you're seeing."
        elif 'account' in category.lower():
            return "Please provide your account details and describe the specific issue you're experiencing."
        else:
            return "Please provide any additional details that would help us better understand your request."
    
    def _generate_solution_details(self, task_data: Dict[str, Any]) -> str:
        """Generate solution details for resolved issues"""
        category = task_data.get('category', '')
        summary = task_data.get('summary', '')
        
        if 'technical' in category.lower():
            return "The technical issue has been resolved. Please try accessing your account again and let us know if you experience any further problems."
        elif 'billing' in category.lower():
            return "Your billing inquiry has been addressed. You should see the changes reflected in your next billing cycle."
        elif 'account' in category.lower():
            return "Your account issue has been resolved. You should now have full access to all features."
        else:
            return "Your request has been successfully processed. Please let us know if you need any further assistance."
    
    def get_response_history(self, task_id: str = None) -> List[EmailResponse]:
        """Get response history for a specific task or all responses"""
        if task_id:
            return [resp for resp in self.response_history if resp.task_id == task_id]
        return self.response_history
    
    def save_template(self, template: ResponseTemplate) -> bool:
        """Save a new or updated template"""
        try:
            template.updated_at = datetime.now(timezone.utc)
            if not template.created_at:
                template.created_at = template.updated_at
            
            self.templates[template.id] = template
            logger.info(f"Saved template: {template.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving template: {e}")
            return False
    
    def get_template(self, template_id: str) -> Optional[ResponseTemplate]:
        """Get a specific template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[ResponseTemplate]:
        """List all available templates"""
        return list(self.templates.values())
    
    def validate_response(self, response: EmailResponse) -> Dict[str, Any]:
        """Validate a generated response for quality and compliance"""
        validation_results = {
            'is_valid': True,
            'issues': [],
            'suggestions': [],
            'score': 100
        }
        
        # Check required fields
        if not response.recipient_email:
            validation_results['issues'].append('Missing recipient email')
            validation_results['score'] -= 20
        
        if not response.subject:
            validation_results['issues'].append('Missing subject line')
            validation_results['score'] -= 15
        
        if not response.body:
            validation_results['issues'].append('Missing email body')
            validation_results['score'] -= 25
        
        # Check content quality
        if len(response.body) < 50:
            validation_results['issues'].append('Email body too short')
            validation_results['score'] -= 10
        
        if len(response.subject) > 100:
            validation_results['suggestions'].append('Subject line might be too long')
            validation_results['score'] -= 5
        
        # Check for professional tone indicators
        if any(word in response.body.lower() for word in ['urgent', 'immediately', 'asap']):
            if response.priority != 'Urgent' and response.priority != 'High':
                validation_results['suggestions'].append('Consider adjusting priority based on urgent language')
        
        # Overall validation
        if validation_results['score'] < 70:
            validation_results['is_valid'] = False
        
        return validation_results
