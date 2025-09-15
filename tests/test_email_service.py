import unittest
from unittest.mock import patch, MagicMock
import os
from email_service import EmailService

class TestEmailService(unittest.TestCase):
    """Test cases for EmailService"""
    
    def setUp(self):
        """Set up test environment"""
        self.email_service = EmailService()
    
    @patch.dict(os.environ, {
        'CLIENT_ID': 'test_client_id',
        'CLIENT_SECRET': 'test_client_secret',
        'TENANT_ID': 'test_tenant_id'
    })
    @patch('email_service.msal.ConfidentialClientApplication')
    def test_get_access_token_success(self, mock_msal_app):
        """Test successful access token retrieval"""
        # Mock the MSAL app and token acquisition
        mock_app_instance = MagicMock()
        mock_msal_app.return_value = mock_app_instance
        
        # Mock successful token acquisition
        mock_app_instance.acquire_token_silent.return_value = None
        mock_app_instance.acquire_token_for_client.return_value = {
            'access_token': 'test_access_token'
        }
        
        token = self.email_service.get_access_token()
        self.assertEqual(token, 'test_access_token')
    
    @patch.dict(os.environ, {
        'CLIENT_ID': 'test_client_id',
        'CLIENT_SECRET': 'test_client_secret',
        'TENANT_ID': 'test_tenant_id'
    })
    @patch('email_service.msal.ConfidentialClientApplication')
    def test_get_access_token_failure(self, mock_msal_app):
        """Test access token retrieval failure"""
        # Mock the MSAL app and token acquisition failure
        mock_app_instance = MagicMock()
        mock_msal_app.return_value = mock_app_instance
        
        # Mock failed token acquisition
        mock_app_instance.acquire_token_silent.return_value = None
        mock_app_instance.acquire_token_for_client.return_value = {
            'error': 'invalid_client',
            'error_description': 'Invalid client credentials'
        }
        
        token = self.email_service.get_access_token()
        self.assertIsNone(token)
    
    @patch('email_service.requests.get')
    @patch.object(EmailService, 'get_access_token')
    def test_get_emails_success(self, mock_get_token, mock_requests_get):
        """Test successful email retrieval"""
        # Mock access token
        mock_get_token.return_value = 'test_access_token'
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'value': [
                {
                    'id': 'email1',
                    'subject': 'Test Email 1',
                    'from': {
                        'emailAddress': {
                            'name': 'Test User 1',
                            'address': 'test1@example.com'
                        }
                    },
                    'bodyPreview': 'Test email content 1',
                    'receivedDateTime': '2024-01-01T10:00:00Z',
                    'importance': 'normal'
                },
                {
                    'id': 'email2',
                    'subject': 'Test Email 2',
                    'from': {
                        'emailAddress': {
                            'name': 'Test User 2',
                            'address': 'test2@example.com'
                        }
                    },
                    'bodyPreview': 'Test email content 2',
                    'receivedDateTime': '2024-01-01T11:00:00Z',
                    'importance': 'high'
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        emails = self.email_service.get_emails()
        
        self.assertEqual(len(emails), 2)
        self.assertEqual(emails[0]['id'], 'email1')
        self.assertEqual(emails[0]['subject'], 'Test Email 1')
        self.assertEqual(emails[0]['sender']['name'], 'Test User 1')
        self.assertEqual(emails[0]['sender']['email'], 'test1@example.com')
        self.assertEqual(emails[0]['importance'], 'normal')
        
        self.assertEqual(emails[1]['id'], 'email2')
        self.assertEqual(emails[1]['subject'], 'Test Email 2')
        self.assertEqual(emails[1]['sender']['name'], 'Test User 2')
        self.assertEqual(emails[1]['sender']['email'], 'test2@example.com')
        self.assertEqual(emails[1]['importance'], 'high')
    
    @patch('email_service.requests.get')
    @patch.object(EmailService, 'get_access_token')
    def test_get_emails_no_token(self, mock_get_token, mock_requests_get):
        """Test email retrieval when no access token is available"""
        # Mock no access token
        mock_get_token.return_value = None
        
        emails = self.email_service.get_emails()
        self.assertEqual(emails, [])
        mock_requests_get.assert_not_called()
    
    @patch('email_service.requests.get')
    @patch.object(EmailService, 'get_access_token')
    def test_get_emails_api_error(self, mock_get_token, mock_requests_get):
        """Test email retrieval when API returns error"""
        # Mock access token
        mock_get_token.return_value = 'test_access_token'
        
        # Mock API error response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_requests_get.return_value = mock_response
        
        emails = self.email_service.get_emails()
        self.assertEqual(emails, [])
    
    @patch('email_service.requests.get')
    @patch.object(EmailService, 'get_access_token')
    def test_get_email_body_success(self, mock_get_token, mock_requests_get):
        """Test successful email body retrieval"""
        # Mock access token
        mock_get_token.return_value = 'test_access_token'
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'body': {
                'content': 'Full email body content'
            }
        }
        mock_requests_get.return_value = mock_response
        
        body = self.email_service.get_email_body('email1')
        self.assertEqual(body, 'Full email body content')
    
    @patch('email_service.requests.get')
    @patch.object(EmailService, 'get_access_token')
    def test_get_email_body_no_token(self, mock_get_token, mock_requests_get):
        """Test email body retrieval when no access token is available"""
        # Mock no access token
        mock_get_token.return_value = None
        
        body = self.email_service.get_email_body('email1')
        self.assertIsNone(body)
        mock_requests_get.assert_not_called()
    
    @patch('email_service.requests.get')
    @patch.object(EmailService, 'get_access_token')
    def test_get_email_body_api_error(self, mock_get_token, mock_requests_get):
        """Test email body retrieval when API returns error"""
        # Mock access token
        mock_get_token.return_value = 'test_access_token'
        
        # Mock API error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'Not Found'
        mock_requests_get.return_value = mock_response
        
        body = self.email_service.get_email_body('email1')
        self.assertIsNone(body)

if __name__ == '__main__':
    unittest.main()

