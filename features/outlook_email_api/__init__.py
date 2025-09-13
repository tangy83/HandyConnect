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

from .email_fetcher import EmailFetcher
from .email_parser import EmailParser
from .email_filter import EmailFilter
from .attachment_handler import AttachmentHandler

__all__ = [
    'EmailFetcher',
    'EmailParser', 
    'EmailFilter',
    'AttachmentHandler'
]
