import unittest
from unittest.mock import patch, MagicMock
import os
from llm_service import LLMService

class TestLLMService(unittest.TestCase):
    """Test cases for LLMService"""
    
    def setUp(self):
        """Set up test environment"""
        self.llm_service = LLMService()
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_openai_key'})
    @patch('llm_service.openai.OpenAI')
    def test_process_email_success(self, mock_openai):
        """Test successful email processing"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {
            "summary": "Customer is experiencing login issues with their account",
            "category": "Technical Issue",
            "priority": "High",
            "sentiment": "Frustrated",
            "action_required": "Investigate login system and provide solution"
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test email data
        email = {
            'subject': 'Login Issues',
            'sender': {'name': 'John Doe', 'email': 'john@example.com'},
            'body': 'I cannot log into my account. Please help.'
        }
        
        result = self.llm_service.process_email(email)
        
        self.assertEqual(result['summary'], 'Customer is experiencing login issues with their account')
        self.assertEqual(result['category'], 'Technical Issue')
        self.assertEqual(result['priority'], 'High')
        self.assertEqual(result['sentiment'], 'Frustrated')
        self.assertEqual(result['action_required'], 'Investigate login system and provide solution')
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_openai_key'})
    @patch('llm_service.openai.OpenAI')
    def test_process_email_json_parsing_failure(self, mock_openai):
        """Test email processing when JSON parsing fails"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Invalid JSON response'
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test email data
        email = {
            'subject': 'Test Email',
            'sender': {'name': 'Test User', 'email': 'test@example.com'},
            'body': 'Test content'
        }
        
        result = self.llm_service.process_email(email)
        
        # Should return fallback values
        self.assertEqual(result['summary'], 'Invalid JSON response')
        self.assertEqual(result['category'], 'General Inquiry')
        self.assertEqual(result['priority'], 'Medium')
        self.assertEqual(result['sentiment'], 'Neutral')
        self.assertEqual(result['action_required'], 'Review and respond')
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_openai_key'})
    @patch('llm_service.openai.OpenAI')
    def test_process_email_api_error(self, mock_openai):
        """Test email processing when API call fails"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock API error
        mock_client.chat.completions.create.side_effect = Exception('API Error')
        
        # Test email data
        email = {
            'subject': 'Test Email',
            'sender': {'name': 'Test User', 'email': 'test@example.com'},
            'body': 'Test content'
        }
        
        result = self.llm_service.process_email(email)
        
        # Should return default values
        self.assertEqual(result['summary'], 'Email from Test User: Test Email')
        self.assertEqual(result['category'], 'General Inquiry')
        self.assertEqual(result['priority'], 'Medium')
        self.assertEqual(result['sentiment'], 'Neutral')
        self.assertEqual(result['action_required'], 'Review and respond')
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_openai_key'})
    @patch('llm_service.openai.OpenAI')
    def test_generate_response_suggestion_success(self, mock_openai):
        """Test successful response suggestion generation"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Thank you for contacting us. We are investigating the login issue and will get back to you within 24 hours.'
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test task data
        task = MagicMock()
        task.category = 'Technical Issue'
        task.priority = 'High'
        task.summary = 'Login issues'
        task.content = 'I cannot log into my account'
        
        result = self.llm_service.generate_response_suggestion(task)
        
        self.assertEqual(result, 'Thank you for contacting us. We are investigating the login issue and will get back to you within 24 hours.')
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_openai_key'})
    @patch('llm_service.openai.OpenAI')
    def test_generate_response_suggestion_error(self, mock_openai):
        """Test response suggestion generation when API call fails"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock API error
        mock_client.chat.completions.create.side_effect = Exception('API Error')
        
        # Test task data
        task = MagicMock()
        task.category = 'Technical Issue'
        task.priority = 'High'
        task.summary = 'Login issues'
        task.content = 'I cannot log into my account'
        
        result = self.llm_service.generate_response_suggestion(task)
        
        # Should return default response
        self.assertEqual(result, 'Thank you for contacting us. We are reviewing your request and will get back to you soon.')
    
    def test_process_email_with_missing_fields(self):
        """Test email processing with missing email fields"""
        # Test email with missing fields
        email = {
            'subject': 'Test Email',
            'sender': {'name': 'Test User', 'email': 'test@example.com'}
            # Missing 'body' field
        }
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_openai_key'}):
            with patch('llm_service.openai.OpenAI') as mock_openai:
                mock_client = MagicMock()
                mock_openai.return_value = mock_client
                
                # Mock API error
                mock_client.chat.completions.create.side_effect = Exception('API Error')
                
                result = self.llm_service.process_email(email)
                
                # Should return default values
                self.assertEqual(result['summary'], 'Email from Test User: Test Email')
                self.assertEqual(result['category'], 'General Inquiry')
                self.assertEqual(result['priority'], 'Medium')
                self.assertEqual(result['sentiment'], 'Neutral')
                self.assertEqual(result['action_required'], 'Review and respond')

if __name__ == '__main__':
    unittest.main()


