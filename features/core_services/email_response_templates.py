"""
Email Response Templates for Automated Acknowledgment System
Provides tone-appropriate email templates based on customer sentiment and urgency
"""

from typing import Dict, Optional
from datetime import datetime, timedelta

class EmailResponseTemplates:
    """
    Manages email response templates for different tones and urgency levels.
    Templates are customized based on customer tone analysis.
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.sla_timelines = self._initialize_sla_timelines()
    
    def _initialize_sla_timelines(self) -> Dict:
        """Initialize SLA response timelines based on priority"""
        return {
            'critical': {
                'response_time': '2 hours',
                'resolution_target': '4-8 hours',
                'description': 'Immediate priority'
            },
            'high': {
                'response_time': '4 hours',
                'resolution_target': '24 hours',
                'description': 'High priority'
            },
            'medium': {
                'response_time': '1 business day',
                'resolution_target': '2-3 business days',
                'description': 'Standard priority'
            },
            'low': {
                'response_time': '2 business days',
                'resolution_target': '3-5 business days',
                'description': 'Standard inquiry'
            }
        }
    
    def _initialize_templates(self) -> Dict:
        """Initialize all email templates organized by tone"""
        return {
            'urgent': {
                'subject': 'Case #{case_number} - URGENT: Immediate Action Initiated',
                'greeting': self._urgent_greeting,
                'acknowledgment': self._urgent_acknowledgment,
                'next_steps': self._urgent_next_steps,
                'closing': self._urgent_closing,
                'priority_level': 'CRITICAL'
            },
            'angry': {
                'subject': 'Case #{case_number} - Your Concerns Are Our Priority',
                'greeting': self._angry_greeting,
                'acknowledgment': self._angry_acknowledgment,
                'next_steps': self._angry_next_steps,
                'closing': self._angry_closing,
                'priority_level': 'HIGH'
            },
            'frustrated': {
                'subject': 'Case #{case_number} - We\'re Here to Help',
                'greeting': self._frustrated_greeting,
                'acknowledgment': self._frustrated_acknowledgment,
                'next_steps': self._frustrated_next_steps,
                'closing': self._frustrated_closing,
                'priority_level': 'HIGH'
            },
            'concerned': {
                'subject': 'Case #{case_number} - We Understand Your Concerns',
                'greeting': self._concerned_greeting,
                'acknowledgment': self._concerned_acknowledgment,
                'next_steps': self._concerned_next_steps,
                'closing': self._concerned_closing,
                'priority_level': 'MEDIUM'
            },
            'confused': {
                'subject': 'Case #{case_number} - We\'re Here to Clarify',
                'greeting': self._confused_greeting,
                'acknowledgment': self._confused_acknowledgment,
                'next_steps': self._confused_next_steps,
                'closing': self._confused_closing,
                'priority_level': 'MEDIUM'
            },
            'polite': {
                'subject': 'Case #{case_number} - Request Received',
                'greeting': self._polite_greeting,
                'acknowledgment': self._polite_acknowledgment,
                'next_steps': self._polite_next_steps,
                'closing': self._polite_closing,
                'priority_level': 'MEDIUM'
            },
            'grateful': {
                'subject': 'Case #{case_number} - Thank You for Contacting Us',
                'greeting': self._grateful_greeting,
                'acknowledgment': self._grateful_acknowledgment,
                'next_steps': self._grateful_next_steps,
                'closing': self._grateful_closing,
                'priority_level': 'LOW'
            },
            'calm': {
                'subject': 'Case #{case_number} - Request Received',
                'greeting': self._calm_greeting,
                'acknowledgment': self._calm_acknowledgment,
                'next_steps': self._calm_next_steps,
                'closing': self._calm_closing,
                'priority_level': 'MEDIUM'
            }
        }
    
    # ============ URGENT TONE TEMPLATES ============
    
    def _urgent_greeting(self, customer_name: str, **kwargs) -> str:
        return f"""Dear {customer_name},

We understand the URGENCY of your situation and have immediately prioritized your case. Your safety and comfort are our top priority."""
    
    def _urgent_acknowledgment(self, case_number: str, brief_summary: str, property_details: str, **kwargs) -> str:
        return f"""
🚨 CASE DETAILS - CRITICAL PRIORITY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Case Number: {case_number}
• Priority Level: CRITICAL
• Issue: {brief_summary}
{property_details}

Your case has been ESCALATED to our emergency response team and is receiving immediate attention."""
    
    def _urgent_next_steps(self, response_time: str, **kwargs) -> str:
        return f"""
⚡ IMMEDIATE ACTIONS IN PROGRESS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Your case has been flagged as critical priority
✓ Emergency response team has been notified
✓ A senior technician will contact you within {response_time}
✓ Real-time updates will be provided throughout the process

We are mobilizing our resources to address this situation as quickly as possible."""
    
    def _urgent_closing(self, **kwargs) -> str:
        return """
For IMMEDIATE assistance or emergencies, please call our 24/7 emergency line.

We take your situation very seriously and are committed to resolving this urgently.

Emergency Response Team
HandyConnect Property Management"""
    
    # ============ ANGRY TONE TEMPLATES ============
    
    def _angry_greeting(self, customer_name: str, **kwargs) -> str:
        return f"""Dear {customer_name},

We sincerely apologize for the situation you're experiencing. Your frustration is completely valid, and we take full responsibility for addressing your concerns immediately."""
    
    def _angry_acknowledgment(self, case_number: str, brief_summary: str, property_details: str, **kwargs) -> str:
        return f"""
📋 CASE DETAILS - HIGH PRIORITY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Case Number: {case_number}
• Priority Level: HIGH
• Issue: {brief_summary}
{property_details}

We understand this situation is unacceptable, and we are personally committed to making this right."""
    
    def _angry_next_steps(self, response_time: str, **kwargs) -> str:
        return f"""
🎯 WHAT WE'RE DOING RIGHT NOW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ A senior team member will personally review your case
✓ You will receive a response within {response_time}
✓ We will provide regular updates on our progress
✓ Your case has been escalated for immediate attention

Your satisfaction is important to us, and we will work tirelessly to resolve this matter."""
    
    def _angry_closing(self, **kwargs) -> str:
        return """
We value your patience and trust as we work to resolve this. Please don't hesitate to reach out if you need anything.

With sincere apologies,
Senior Support Team
HandyConnect Property Management"""
    
    # ============ FRUSTRATED TONE TEMPLATES ============
    
    def _frustrated_greeting(self, customer_name: str, **kwargs) -> str:
        return f"""Dear {customer_name},

We sincerely apologize for the inconvenience you've experienced. We understand your frustration, and we're committed to making this right."""
    
    def _frustrated_acknowledgment(self, case_number: str, brief_summary: str, property_details: str, **kwargs) -> str:
        return f"""
📋 CASE DETAILS - HIGH PRIORITY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Case Number: {case_number}
• Priority Level: HIGH
• Issue: {brief_summary}
{property_details}

Your concerns are receiving dedicated attention from our team."""
    
    def _frustrated_next_steps(self, response_time: str, **kwargs) -> str:
        return f"""
💪 OUR COMMITMENT TO YOU:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Your case is being personally monitored
✓ A dedicated team member will respond within {response_time}
✓ We'll keep you informed every step of the way
✓ We're committed to a swift resolution

We take your feedback seriously and will ensure this is handled properly."""
    
    def _frustrated_closing(self, **kwargs) -> str:
        return """
Thank you for your patience. We're here to support you.

Sincerely,
Support Team
HandyConnect Property Management"""
    
    # ============ CONCERNED TONE TEMPLATES ============
    
    def _concerned_greeting(self, customer_name: str, **kwargs) -> str:
        return f"""Dear {customer_name},

Thank you for bringing this to our attention. We understand your concerns and want to assure you that we're here to help."""
    
    def _concerned_acknowledgment(self, case_number: str, brief_summary: str, property_details: str, **kwargs) -> str:
        return f"""
📋 CASE DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Case Number: {case_number}
• Priority Level: MEDIUM
• Issue: {brief_summary}
{property_details}

We take your concerns seriously and will address them thoroughly."""
    
    def _concerned_next_steps(self, response_time: str, **kwargs) -> str:
        return f"""
📌 NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Our team will review your case carefully
✓ You'll receive a detailed response within {response_time}
✓ We'll address all your concerns comprehensively
✓ You'll be kept informed of any developments

Rest assured, we're taking the appropriate steps to resolve this."""
    
    def _concerned_closing(self, **kwargs) -> str:
        return """
If you have any additional concerns, please don't hesitate to reach out.

Best regards,
Support Team
HandyConnect Property Management"""
    
    # ============ CONFUSED TONE TEMPLATES ============
    
    def _confused_greeting(self, customer_name: str, **kwargs) -> str:
        return f"""Dear {customer_name},

Thank you for reaching out. We're here to help clarify things and provide the assistance you need."""
    
    def _confused_acknowledgment(self, case_number: str, brief_summary: str, property_details: str, **kwargs) -> str:
        return f"""
📋 CASE DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Case Number: {case_number}
• Issue: {brief_summary}
{property_details}

We've received your inquiry and will provide clear, helpful information."""
    
    def _confused_next_steps(self, response_time: str, **kwargs) -> str:
        return f"""
🤝 HOW WE'LL HELP:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ A knowledgeable team member will review your inquiry
✓ We'll provide a clear, easy-to-understand response within {response_time}
✓ If you need further clarification, we're here to help
✓ Feel free to ask any additional questions

Our goal is to ensure you have all the information you need."""
    
    def _confused_closing(self, **kwargs) -> str:
        return """
Don't hesitate to reach out if you need any clarification. We're happy to help!

Best regards,
Support Team
HandyConnect Property Management"""
    
    # ============ POLITE TONE TEMPLATES ============
    
    def _polite_greeting(self, customer_name: str, **kwargs) -> str:
        return f"""Dear {customer_name},

Thank you for contacting HandyConnect. We appreciate your patience and courteous communication."""
    
    def _polite_acknowledgment(self, case_number: str, brief_summary: str, property_details: str, **kwargs) -> str:
        return f"""
📋 CASE DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Case Number: {case_number}
• Issue: {brief_summary}
{property_details}

We've successfully received your request and created a case for tracking."""
    
    def _polite_next_steps(self, response_time: str, **kwargs) -> str:
        return f"""
📌 NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Our team will review your request within {response_time}
✓ You'll receive updates as we progress
✓ Please reference Case #{kwargs.get('case_number', 'N/A')} in any future correspondence
✓ We're committed to providing excellent service

Thank you for giving us the opportunity to assist you."""
    
    def _polite_closing(self, **kwargs) -> str:
        return """
Thank you for choosing HandyConnect. We look forward to serving you.

Best regards,
Support Team
HandyConnect Property Management"""
    
    # ============ GRATEFUL TONE TEMPLATES ============
    
    def _grateful_greeting(self, customer_name: str, **kwargs) -> str:
        return f"""Dear {customer_name},

Thank you for your kind words and for contacting HandyConnect. We truly appreciate your feedback."""
    
    def _grateful_acknowledgment(self, case_number: str, brief_summary: str, property_details: str, **kwargs) -> str:
        return f"""
📋 CASE DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Case Number: {case_number}
• Issue: {brief_summary}
{property_details}

We're pleased to assist you and have logged your request."""
    
    def _grateful_next_steps(self, response_time: str, **kwargs) -> str:
        return f"""
📌 NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ We'll review your request within {response_time}
✓ Our team will handle this with the care you deserve
✓ You'll receive updates on our progress
✓ We're here if you need anything else

Your satisfaction is our priority."""
    
    def _grateful_closing(self, **kwargs) -> str:
        return """
Thank you again for your trust in HandyConnect. It's a pleasure serving you.

Warmest regards,
Support Team
HandyConnect Property Management"""
    
    # ============ CALM TONE TEMPLATES ============
    
    def _calm_greeting(self, customer_name: str, **kwargs) -> str:
        return f"""Dear {customer_name},

Thank you for contacting HandyConnect. We've received your request and are here to help."""
    
    def _calm_acknowledgment(self, case_number: str, brief_summary: str, property_details: str, **kwargs) -> str:
        return f"""
📋 CASE DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Case Number: {case_number}
• Issue: {brief_summary}
{property_details}

Your request has been logged and will be addressed by our team."""
    
    def _calm_next_steps(self, response_time: str, **kwargs) -> str:
        return f"""
📌 NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Our team will review your case within {response_time}
✓ You'll receive updates as we make progress
✓ Please reference Case #{kwargs.get('case_number', 'N/A')} in future correspondence
✓ We're committed to resolving this efficiently

Thank you for your patience."""
    
    def _calm_closing(self, **kwargs) -> str:
        return """
If you have any questions, please don't hesitate to reach out.

Best regards,
Support Team
HandyConnect Property Management"""
    
    # ============ UTILITY METHODS ============
    
    def get_template(self, tone: str) -> Optional[Dict]:
        """Get template for a specific tone"""
        # Default to 'calm' if tone not found
        return self.templates.get(tone.lower(), self.templates.get('calm'))
    
    def get_sla_timeline(self, urgency_level: str) -> Dict:
        """Get SLA timeline based on urgency level"""
        return self.sla_timelines.get(urgency_level.lower(), self.sla_timelines['medium'])
    
    def format_property_details(self, property_number: Optional[str], 
                                block_number: Optional[str],
                                property_address: Optional[str]) -> str:
        """Format property details for email"""
        details = []
        
        if property_number:
            details.append(f"• Property Number: {property_number}")
        if block_number:
            details.append(f"• Block/Building: {block_number}")
        if property_address:
            details.append(f"• Address: {property_address}")
        
        if details:
            return "\n".join(details)
        return ""
    
    def build_email_body(self, tone: str, context: Dict) -> str:
        """
        Build complete email body from template and context.
        
        Args:
            tone: The detected tone (urgent, angry, frustrated, etc.)
            context: Dictionary containing case details, customer info, etc.
        
        Returns:
            Complete email body as string
        """
        template = self.get_template(tone)
        if not template:
            template = self.templates['calm']
        
        # Extract context values
        customer_name = context.get('customer_name', 'Valued Customer')
        case_number = context.get('case_number', 'N/A')
        brief_summary = context.get('brief_summary', 'Your request')
        urgency_level = context.get('urgency_level', 'medium')
        property_number = context.get('property_number')
        block_number = context.get('block_number')
        property_address = context.get('property_address')
        
        # Format property details
        property_details = self.format_property_details(
            property_number, block_number, property_address
        )
        
        # Get SLA timeline
        sla = self.get_sla_timeline(urgency_level)
        response_time = sla['response_time']
        
        # Build email sections
        greeting = template['greeting'](customer_name=customer_name)
        acknowledgment = template['acknowledgment'](
            case_number=case_number,
            brief_summary=brief_summary,
            property_details=property_details
        )
        next_steps = template['next_steps'](
            response_time=response_time,
            case_number=case_number
        )
        closing = template['closing']()
        
        # Combine all sections
        email_body = f"""{greeting}

{acknowledgment}

{next_steps}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 NEED HELP?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Reply to this email with your case number
• Reference Case #{case_number} in all correspondence
• For urgent matters, contact our emergency line

{closing}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This email was sent from HandyConnect Case Management System
Case ID: {case_number} | Sent: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
"""
        
        return email_body.strip()
    
    def get_subject_line(self, tone: str, case_number: str) -> str:
        """Get appropriate subject line based on tone"""
        template = self.get_template(tone)
        if not template:
            template = self.templates['calm']
        
        return template['subject'].format(case_number=case_number)

