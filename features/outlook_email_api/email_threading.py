"""
Email Threading and Conversation Management
Handles grouping related emails into conversation threads
"""

import re
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class EmailThread:
    """Represents a conversation thread"""
    thread_id: str
    subject: str
    participants: set
    emails: List[Dict]
    created_at: datetime
    updated_at: datetime
    status: str  # 'active', 'resolved', 'archived'
    priority: str  # 'low', 'medium', 'high', 'urgent'
    category: str
    summary: str

class EmailThreadingService:
    """Service for managing email threads and conversations"""
    
    def __init__(self):
        self.threads: Dict[str, EmailThread] = {}
        self.email_to_thread: Dict[str, str] = {}  # email_id -> thread_id
    
    def extract_thread_identifier(self, email: Dict) -> str:
        """
        Extract a unique identifier for the email thread
        Uses subject normalization and participant matching
        """
        # Normalize subject by removing common prefixes
        subject = email.get('subject', '')
        normalized_subject = self._normalize_subject(subject)
        
        # Get participants (sender + any recipients)
        participants = self._extract_participants(email)
        
        # Create thread identifier
        thread_key = f"{normalized_subject}:{':'.join(sorted(participants))}"
        return hashlib.md5(thread_key.encode()).hexdigest()[:12]
    
    def _normalize_subject(self, subject: str) -> str:
        """Normalize email subject for thread matching"""
        if not subject:
            return "no-subject"
        
        # Remove common prefixes
        prefixes_to_remove = [
            r'^re:\s*',
            r'^fwd:\s*',
            r'^fw:\s*',
            r'^\[.*?\]\s*',
            r'^\(.*?\)\s*'
        ]
        
        normalized = subject.lower().strip()
        for prefix in prefixes_to_remove:
            normalized = re.sub(prefix, '', normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def _extract_participants(self, email: Dict) -> set:
        """Extract all participants from email"""
        participants = set()
        
        # Add sender
        sender_email = email.get('sender', {}).get('email', '')
        if sender_email:
            participants.add(sender_email.lower())
        
        # Add recipients (if available)
        recipients = email.get('recipients', [])
        for recipient in recipients:
            if isinstance(recipient, dict):
                email_addr = recipient.get('email', '')
            else:
                email_addr = recipient
            if email_addr:
                participants.add(email_addr.lower())
        
        return participants
    
    def create_or_update_thread(self, email: Dict) -> str:
        """
        Create a new thread or add email to existing thread
        Returns the thread_id
        """
        thread_id = self.extract_thread_identifier(email)
        email_id = email.get('id')
        
        if thread_id in self.threads:
            # Add email to existing thread
            thread = self.threads[thread_id]
            thread.emails.append(email)
            thread.updated_at = datetime.utcnow()
            thread.participants.update(self._extract_participants(email))
            
            # Update thread status based on email content
            self._update_thread_status(thread, email)
        else:
            # Create new thread
            thread = EmailThread(
                thread_id=thread_id,
                subject=email.get('subject', 'No Subject'),
                participants=self._extract_participants(email),
                emails=[email],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                status='active',
                priority=self._determine_thread_priority(email),
                category=self._determine_thread_category(email),
                summary=self._generate_thread_summary(email)
            )
            self.threads[thread_id] = thread
        
        # Map email to thread
        if email_id:
            self.email_to_thread[email_id] = thread_id
        
        return thread_id
    
    def _update_thread_status(self, thread: EmailThread, email: Dict) -> None:
        """Update thread status based on email content"""
        content = email.get('body', '').lower()
        
        # Check for resolution keywords
        resolution_keywords = [
            'resolved', 'fixed', 'completed', 'solved', 'closed',
            'thank you', 'thanks', 'appreciate', 'working now'
        ]
        
        if any(keyword in content for keyword in resolution_keywords):
            thread.status = 'resolved'
        
        # Check for urgent keywords
        urgent_keywords = [
            'urgent', 'asap', 'immediately', 'critical', 'emergency',
            'escalate', 'manager', 'supervisor'
        ]
        
        if any(keyword in content for keyword in urgent_keywords):
            thread.priority = 'urgent'
    
    def _determine_thread_priority(self, email: Dict) -> str:
        """Determine thread priority based on email content"""
        content = email.get('body', '').lower()
        subject = email.get('subject', '').lower()
        
        urgent_keywords = [
            'urgent', 'asap', 'immediately', 'critical', 'emergency',
            'escalate', 'manager', 'supervisor', 'down', 'broken'
        ]
        
        high_keywords = [
            'important', 'priority', 'issue', 'problem', 'error',
            'not working', 'help needed', 'assistance'
        ]
        
        if any(keyword in content or keyword in subject for keyword in urgent_keywords):
            return 'urgent'
        elif any(keyword in content or keyword in subject for keyword in high_keywords):
            return 'high'
        else:
            return 'medium'
    
    def _determine_thread_category(self, email: Dict) -> str:
        """Determine thread category based on email content"""
        content = email.get('body', '').lower()
        subject = email.get('subject', '').lower()
        
        # Technical issue keywords
        tech_keywords = [
            'login', 'password', 'access', 'error', 'bug', 'crash',
            'slow', 'loading', 'connection', 'server', 'database'
        ]
        
        # Billing keywords
        billing_keywords = [
            'billing', 'payment', 'invoice', 'charge', 'refund',
            'subscription', 'plan', 'cost', 'price'
        ]
        
        # Feature request keywords
        feature_keywords = [
            'feature', 'request', 'suggestion', 'improvement',
            'enhancement', 'new', 'add', 'implement'
        ]
        
        if any(keyword in content or keyword in subject for keyword in tech_keywords):
            return 'Technical Issue'
        elif any(keyword in content or keyword in subject for keyword in billing_keywords):
            return 'Billing Question'
        elif any(keyword in content or keyword in subject for keyword in feature_keywords):
            return 'Feature Request'
        else:
            return 'General Inquiry'
    
    def _generate_thread_summary(self, email: Dict) -> str:
        """Generate a summary for the thread"""
        subject = email.get('subject', 'No Subject')
        body = email.get('body', '')
        
        # Extract first meaningful sentence
        sentences = body.split('.')
        first_sentence = sentences[0].strip() if sentences else ''
        
        if len(first_sentence) > 100:
            first_sentence = first_sentence[:100] + '...'
        
        return f"{subject}: {first_sentence}" if first_sentence else subject
    
    def get_thread(self, thread_id: str) -> Optional[EmailThread]:
        """Get a specific thread by ID"""
        return self.threads.get(thread_id)
    
    def get_thread_by_email(self, email_id: str) -> Optional[EmailThread]:
        """Get thread containing a specific email"""
        thread_id = self.email_to_thread.get(email_id)
        return self.threads.get(thread_id) if thread_id else None
    
    def get_all_threads(self, status: Optional[str] = None, 
                       priority: Optional[str] = None,
                       category: Optional[str] = None) -> List[EmailThread]:
        """Get all threads with optional filtering"""
        threads = list(self.threads.values())
        
        if status:
            threads = [t for t in threads if t.status == status]
        
        if priority:
            threads = [t for t in threads if t.priority == priority]
        
        if category:
            threads = [t for t in threads if t.category == category]
        
        # Sort by updated_at descending
        threads.sort(key=lambda x: x.updated_at, reverse=True)
        return threads
    
    def update_thread_status(self, thread_id: str, status: str) -> bool:
        """Update thread status"""
        thread = self.threads.get(thread_id)
        if thread:
            thread.status = status
            thread.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_thread_priority(self, thread_id: str, priority: str) -> bool:
        """Update thread priority"""
        thread = self.threads.get(thread_id)
        if thread:
            thread.priority = priority
            thread.updated_at = datetime.utcnow()
            return True
        return False
    
    def add_thread_notes(self, thread_id: str, notes: str) -> bool:
        """Add notes to thread"""
        thread = self.threads.get(thread_id)
        if thread:
            if not hasattr(thread, 'notes'):
                thread.notes = []
            thread.notes.append({
                'timestamp': datetime.utcnow().isoformat(),
                'content': notes
            })
            thread.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_thread_statistics(self) -> Dict:
        """Get thread statistics"""
        threads = list(self.threads.values())
        
        stats = {
            'total_threads': len(threads),
            'active_threads': len([t for t in threads if t.status == 'active']),
            'resolved_threads': len([t for t in threads if t.status == 'resolved']),
            'archived_threads': len([t for t in threads if t.status == 'archived']),
            'priority_breakdown': {
                'urgent': len([t for t in threads if t.priority == 'urgent']),
                'high': len([t for t in threads if t.priority == 'high']),
                'medium': len([t for t in threads if t.priority == 'medium']),
                'low': len([t for t in threads if t.priority == 'low'])
            },
            'category_breakdown': {}
        }
        
        # Category breakdown
        categories = defaultdict(int)
        for thread in threads:
            categories[thread.category] += 1
        stats['category_breakdown'] = dict(categories)
        
        return stats
    
    def search_threads(self, query: str) -> List[EmailThread]:
        """Search threads by content"""
        query = query.lower()
        matching_threads = []
        
        for thread in self.threads.values():
            # Search in subject
            if query in thread.subject.lower():
                matching_threads.append(thread)
                continue
            
            # Search in emails
            for email in thread.emails:
                if (query in email.get('body', '').lower() or 
                    query in email.get('subject', '').lower()):
                    matching_threads.append(thread)
                    break
        
        return matching_threads
    
    def merge_threads(self, thread_id1: str, thread_id2: str) -> bool:
        """Merge two threads (if they should be the same conversation)"""
        thread1 = self.threads.get(thread_id1)
        thread2 = self.threads.get(thread_id2)
        
        if not thread1 or not thread2:
            return False
        
        # Merge thread2 into thread1
        thread1.emails.extend(thread2.emails)
        thread1.participants.update(thread2.participants)
        thread1.updated_at = datetime.utcnow()
        
        # Update email-to-thread mapping
        for email in thread2.emails:
            email_id = email.get('id')
            if email_id:
                self.email_to_thread[email_id] = thread_id1
        
        # Remove thread2
        del self.threads[thread_id2]
        
        return True




