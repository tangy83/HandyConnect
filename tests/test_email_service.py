import unittest
from unittest.mock import patch, MagicMock
import os
from features.core_services.email_service import EmailService

class TestEmailService(unittest.TestCase):
    """Test cases for EmailService with device flow authentication"""
    
    def setUp(self):
        """Set up test environment"""
        self.email_service = EmailService()
    
    @patch.dict(os.environ, {
        'CLIENT_ID': 'test_client_id',
        'AUTHORITY': 'https://login.microsoftonline.com/consumers',
        'SCOPES': 'Mail.Read'
    })
    @patch('features.core_services.email_service.msal.PublicClientApplication')
    def test_get_access_token_success(self, mock_msal_app):
        """Test successful access token retrieval with device flow"""
        # Mock the MSAL app and token acquisition
        mock_app_instance = MagicMock()
        mock_msal_app.return_value = mock_app_instance
        
        # Mock successful token acquisition
        mock_app_instance.get_accounts.return_value = []
        mock_app_instance.acquire_token_silent.return_value = None
        mock_app_instance.initiate_device_flow.return_value = {
            'user_code': 'test_code',
            'verification_uri': 'https://localhost:8080/device'
        }
        mock_app_instance.acquire_token_by_device_flow.return_value = {
            'access_token': 'test_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
        
        # Test the method
        result = self.email_service.get_access_token()
        
        # Assertions
        self.assertEqual(result, 'test_access_token')
        mock_msal_app.assert_called_once()
        mock_app_instance.acquire_token_by_device_flow.assert_called_once()
    
    @patch.dict(os.environ, {
        'CLIENT_ID': 'test_client_id',
        'AUTHORITY': 'https://login.microsoftonline.com/consumers',
        'SCOPES': 'Mail.Read'
    })
    @patch('features.core_services.email_service.msal.PublicClientApplication')
    def test_get_access_token_failure(self, mock_msal_app):
        """Test access token retrieval failure"""
        # Mock the MSAL app and token acquisition failure
        mock_app_instance = MagicMock()
        mock_msal_app.return_value = mock_app_instance
        
        # Mock failed token acquisition
        mock_app_instance.get_accounts.return_value = []
        mock_app_instance.acquire_token_silent.return_value = None
        mock_app_instance.initiate_device_flow.return_value = {
            'user_code': 'test_code',
            'verification_uri': 'https://localhost:8080/device'
        }
        mock_app_instance.acquire_token_by_device_flow.return_value = {
            'error': 'invalid_client',
            'error_description': 'Invalid client credentials'
        }
        
        # Test the method
        result = self.email_service.get_access_token()
        
        # Assertions
        self.assertIsNone(result)
        mock_msal_app.assert_called_once()
    
    @patch.dict(os.environ, {
        'CLIENT_ID': '',
        'AUTHORITY': 'https://login.microsoftonline.com/consumers',
        'SCOPES': 'Mail.Read'
    })
    def test_get_access_token_no_client_id(self):
        """Test access token retrieval with missing CLIENT_ID"""
        # Create EmailService instance after mocking environment variables
        email_service = EmailService()
        result = email_service.get_access_token()
        self.assertIsNone(result)
    
    @patch('features.core_services.email_service.EmailService.get_access_token')
    @patch('features.core_services.email_service.requests.get')
    def test_get_emails_success(self, mock_get, mock_token):
        """Test successful email retrieval"""
        # Mock access token
        mock_token.return_value = 'test_access_token'
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'value': [
                {
                    'id': '1',
                    'subject': 'Test Email',
                    'from': {
                        'emailAddress': {
                            'name': 'Test User',
                            'address': 'test@example.com'
                        }
                    },
                    'bodyPreview': 'Test email body',
                    'receivedDateTime': '2025-01-01T00:00:00Z',
                    'importance': 'normal',
                    'isRead': False
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Test the method
        result = self.email_service.get_emails()
        
        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['subject'], 'Test Email')
        self.assertEqual(result[0]['sender']['email'], 'test@example.com')
        mock_token.assert_called_once()
        mock_get.assert_called_once()
    
    @patch('features.core_services.email_service.EmailService.get_access_token')
    def test_get_emails_no_token(self, mock_token):
        """Test email retrieval with no access token"""
        # Mock no access token
        mock_token.return_value = None
        
        # Test the method
        result = self.email_service.get_emails()
        
        # Assertions
        self.assertEqual(result, [])
        mock_token.assert_called_once()
    
    @patch('features.core_services.email_service.EmailService.get_access_token')
    @patch('features.core_services.email_service.requests.get')
    def test_get_email_body_success(self, mock_get, mock_token):
        """Test successful email body retrieval"""
        # Mock access token
        mock_token.return_value = 'test_access_token'
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'body': {
                'content': 'Test email body content'
            }
        }
        mock_get.return_value = mock_response
        
        # Test the method
        result = self.email_service.get_email_body('test_message_id')
        
        # Assertions
        self.assertEqual(result, 'Test email body content')
        mock_token.assert_called_once()
        mock_get.assert_called_once()
    
    @patch('features.core_services.email_service.EmailService.get_access_token')
    def test_get_email_body_no_token(self, mock_token):
        """Test email body retrieval with no access token"""
        # Mock no access token
        mock_token.return_value = None
        
        # Test the method
        result = self.email_service.get_email_body('test_message_id')
        
        # Assertions
        self.assertIsNone(result)
        mock_token.assert_called_once()
    
    @patch('features.core_services.email_service.EmailService.get_access_token')
    @patch('features.core_services.email_service.requests.get')
    def test_get_user_info_success(self, mock_get, mock_token):
        """Test successful user info retrieval"""
        # Mock access token
        mock_token.return_value = 'test_access_token'
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'displayName': 'Test User',
            'mail': 'test@example.com',
            'userPrincipalName': 'test@example.com'
        }
        mock_get.return_value = mock_response
        
        # Test the method
        result = self.email_service.get_user_info()
        
        # Assertions
        self.assertEqual(result['displayName'], 'Test User')
        self.assertEqual(result['mail'], 'test@example.com')
        mock_token.assert_called_once()
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main()
