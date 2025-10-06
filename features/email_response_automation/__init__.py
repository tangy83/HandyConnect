"""
Email Response Automation Module

This module handles automated email responses and communication.
Features:
- Automated response generation
- Email template management
- Response scheduling and queuing
- Multi-channel communication
- Response tracking and analytics
"""

from .response_generator import ResponseGenerator
from .email_templates import EmailTemplates
from .response_scheduler import ResponseScheduler
from .communication_tracker import CommunicationTracker

__all__ = [
    'ResponseGenerator',
    'EmailTemplates',
    'ResponseScheduler',
    'CommunicationTracker'
]






