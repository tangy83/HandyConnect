import unittest
from unittest.mock import patch, MagicMock
from features.outlook_email_api.email_threading import EmailThreadingService, EmailThread
from datetime import datetime

class TestEmailThreadingService(unittest.TestCase):
    """Test cases for EmailThreadingService"""
    
    def setUp(self):
        """Set up test environment"""
        self.threading_service = EmailThreadingService()
    
    def test_extract_thread_identifier(self):
        """Test thread identifier extraction"""
        email1 = {
            'subject': 'Re: Login Issue',
            'sender': {'email': 'user1@example.com'},
            'recipients': [{'email': 'support@example.com'}]
        }
        
        email2 = {
            'subject': 'Fwd: Login Issue',
            'sender': {'email': 'user2@example.com'},
            'recipients': [{'email': 'support@example.com'}]
        }
        
        # Same normalized subject and participants should create same thread ID
        thread_id1 = self.threading_service.extract_thread_identifier(email1)
        thread_id2 = self.threading_service.extract_thread_identifier(email2)
        
        # Should be different because different participants
        self.assertNotEqual(thread_id1, thread_id2)
    
    def test_create_new_thread(self):
        """Test creating a new thread"""
        email = {
            'id': 'email1',
            'subject': 'Login Issue',
            'sender': {'email': 'user@example.com', 'name': 'Test User'},
            'body': 'I cannot log into my account',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        thread_id = self.threading_service.create_or_update_thread(email)
        
        # Should create a new thread
        self.assertIsNotNone(thread_id)
        self.assertIn(thread_id, self.threading_service.threads)
        
        thread = self.threading_service.threads[thread_id]
        self.assertEqual(len(thread.emails), 1)
        self.assertEqual(thread.subject, 'Login Issue')
        self.assertIn('user@example.com', thread.participants)
        self.assertIn('support@example.com', thread.participants)
    
    def test_add_email_to_existing_thread(self):
        """Test adding email to existing thread"""
        email1 = {
            'id': 'email1',
            'subject': 'Login Issue',
            'sender': {'email': 'user@example.com'},
            'body': 'I cannot log into my account',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        email2 = {
            'id': 'email2',
            'subject': 'Re: Login Issue',
            'sender': {'email': 'support@example.com'},
            'body': 'We are looking into this issue',
            'recipients': [{'email': 'user@example.com'}]
        }
        
        # Create first thread
        thread_id1 = self.threading_service.create_or_update_thread(email1)
        
        # Add second email (should go to same thread)
        thread_id2 = self.threading_service.create_or_update_thread(email2)
        
        # Should be the same thread
        self.assertEqual(thread_id1, thread_id2)
        
        thread = self.threading_service.threads[thread_id1]
        self.assertEqual(len(thread.emails), 2)
        self.assertIn('user@example.com', thread.participants)
        self.assertIn('support@example.com', thread.participants)
    
    def test_thread_priority_detection(self):
        """Test thread priority detection"""
        urgent_email = {
            'id': 'urgent1',
            'subject': 'URGENT: System Down',
            'sender': {'email': 'user@example.com'},
            'body': 'The system is completely down and we need immediate help!',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        normal_email = {
            'id': 'normal1',
            'subject': 'Question about features',
            'sender': {'email': 'user@example.com'},
            'body': 'I have a question about the new features',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        # Test urgent email
        thread_id1 = self.threading_service.create_or_update_thread(urgent_email)
        thread1 = self.threading_service.threads[thread_id1]
        self.assertEqual(thread1.priority, 'urgent')
        
        # Test normal email
        thread_id2 = self.threading_service.create_or_update_thread(normal_email)
        thread2 = self.threading_service.threads[thread_id2]
        self.assertEqual(thread2.priority, 'medium')
    
    def test_thread_category_detection(self):
        """Test thread category detection"""
        tech_email = {
            'id': 'tech1',
            'subject': 'Login Error',
            'sender': {'email': 'user@example.com'},
            'body': 'I am getting an error when trying to login',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        billing_email = {
            'id': 'billing1',
            'subject': 'Billing Question',
            'sender': {'email': 'user@example.com'},
            'body': 'I have a question about my invoice',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        # Test technical issue
        thread_id1 = self.threading_service.create_or_update_thread(tech_email)
        thread1 = self.threading_service.threads[thread_id1]
        self.assertEqual(thread1.category, 'Technical Issue')
        
        # Test billing question
        thread_id2 = self.threading_service.create_or_update_thread(billing_email)
        thread2 = self.threading_service.threads[thread_id2]
        self.assertEqual(thread2.category, 'Billing Question')
    
    def test_thread_status_update(self):
        """Test thread status update"""
        email = {
            'id': 'email1',
            'subject': 'Login Issue',
            'sender': {'email': 'user@example.com'},
            'body': 'I cannot log into my account',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        thread_id = self.threading_service.create_or_update_thread(email)
        thread = self.threading_service.threads[thread_id]
        
        # Initially should be active
        self.assertEqual(thread.status, 'active')
        
        # Update status
        success = self.threading_service.update_thread_status(thread_id, 'resolved')
        self.assertTrue(success)
        
        # Check updated status
        updated_thread = self.threading_service.threads[thread_id]
        self.assertEqual(updated_thread.status, 'resolved')
    
    def test_thread_priority_update(self):
        """Test thread priority update"""
        email = {
            'id': 'email1',
            'subject': 'Login Issue',
            'sender': {'email': 'user@example.com'},
            'body': 'I cannot log into my account',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        thread_id = self.threading_service.create_or_update_thread(email)
        thread = self.threading_service.threads[thread_id]
        
        # Update priority
        success = self.threading_service.update_thread_priority(thread_id, 'high')
        self.assertTrue(success)
        
        # Check updated priority
        updated_thread = self.threading_service.threads[thread_id]
        self.assertEqual(updated_thread.priority, 'high')
    
    def test_add_thread_notes(self):
        """Test adding notes to thread"""
        email = {
            'id': 'email1',
            'subject': 'Login Issue',
            'sender': {'email': 'user@example.com'},
            'body': 'I cannot log into my account',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        thread_id = self.threading_service.create_or_update_thread(email)
        
        # Add notes
        success = self.threading_service.add_thread_notes(thread_id, 'Escalated to technical team')
        self.assertTrue(success)
        
        # Check notes were added
        thread = self.threading_service.threads[thread_id]
        self.assertTrue(hasattr(thread, 'notes'))
        self.assertEqual(len(thread.notes), 1)
        self.assertEqual(thread.notes[0]['content'], 'Escalated to technical team')
    
    def test_get_thread_statistics(self):
        """Test getting thread statistics"""
        # Create some test threads
        emails = [
            {
                'id': f'email{i}',
                'subject': f'Test Subject {i}',
                'sender': {'email': f'user{i}@example.com'},
                'body': f'Test body {i}',
                'recipients': [{'email': 'support@example.com'}]
            }
            for i in range(3)
        ]
        
        for email in emails:
            self.threading_service.create_or_update_thread(email)
        
        stats = self.threading_service.get_thread_statistics()
        
        self.assertEqual(stats['total_threads'], 3)
        self.assertEqual(stats['active_threads'], 3)
        self.assertEqual(stats['resolved_threads'], 0)
        self.assertEqual(stats['archived_threads'], 0)
    
    def test_search_threads(self):
        """Test searching threads"""
        email1 = {
            'id': 'email1',
            'subject': 'Login Issue',
            'sender': {'email': 'user@example.com'},
            'body': 'I cannot log into my account',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        email2 = {
            'id': 'email2',
            'subject': 'Billing Question',
            'sender': {'email': 'user@example.com'},
            'body': 'I have a question about my invoice',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        # Create threads
        self.threading_service.create_or_update_thread(email1)
        self.threading_service.create_or_update_thread(email2)
        
        # Search for login
        results = self.threading_service.search_threads('login')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].subject, 'Login Issue')
        
        # Search for billing
        results = self.threading_service.search_threads('billing')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].subject, 'Billing Question')
    
    def test_merge_threads(self):
        """Test merging threads"""
        email1 = {
            'id': 'email1',
            'subject': 'Login Issue',
            'sender': {'email': 'user1@example.com'},
            'body': 'I cannot log into my account',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        email2 = {
            'id': 'email2',
            'subject': 'Password Problem',
            'sender': {'email': 'user2@example.com'},
            'body': 'Still having login problems',
            'recipients': [{'email': 'support@example.com'}]
        }
        
        # Create two separate threads (different participants)
        thread_id1 = self.threading_service.create_or_update_thread(email1)
        thread_id2 = self.threading_service.create_or_update_thread(email2)
        
        # Verify they are separate threads
        self.assertNotEqual(thread_id1, thread_id2)
        
        # Merge threads
        success = self.threading_service.merge_threads(thread_id1, thread_id2)
        self.assertTrue(success)
        
        # Check that thread1 now has both emails
        thread1 = self.threading_service.threads[thread_id1]
        self.assertEqual(len(thread1.emails), 2)
        
        # Check that thread2 no longer exists
        self.assertNotIn(thread_id2, self.threading_service.threads)

if __name__ == '__main__':
    unittest.main()
