"""
Outlook Email API Module

This module handles all interactions with Microsoft Graph API for Outlook emails.
Features:
- Email fetching and polling
- Email parsing and content extraction
- Attachment handling
- Email filtering and search
- Real-time email monitoring
"""

from .email_threading import EmailThreadingService, EmailThread
from .thread_api import thread_bp
from .graph_testing import graph_test_bp

__all__ = [
    'EmailThreadingService',
    'EmailThread',
    'thread_bp',
    'graph_test_bp'
]

