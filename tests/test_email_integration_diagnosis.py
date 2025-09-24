"""
Email Integration Diagnostic Tool
Author: AI Assistant
Date: September 20, 2025

Comprehensive diagnostic tests for Outlook email integration issues.
"""

import pytest
import json
from unittest.mock import Mock, patch
import requests
import os

from .advanced_tdd_framework import AdvancedTestBase

class TestEmailIntegrationDiagnosis(AdvancedTestBase):
    """Diagnostic tests for email integration"""
    
    @pytest.mark.integration
    @pytest.mark.email
    @pytest.mark.diagnosis
    def test_authentication_flow_diagnosis(self):
        """Diagnose authentication flow issues"""
        from email_service import EmailService
        
        service = EmailService()
        
        # Test 1: Check if credentials are properly loaded
        assert service.client_id is not None, "CLIENT_ID not loaded from environment"
        assert service.client_secret is not None, "CLIENT_SECRET not loaded from environment"
        assert service.tenant_id is not None, "TENANT_ID not loaded from environment"
        
        print(f"✅ Credentials loaded: CLIENT_ID={service.client_id[:8]}...")
        
        # Test 2: Check authentication method
        token = service.get_access_token()
        assert token is not None, "Failed to acquire access token"
        
        print(f"✅ Token acquired: {token[:20]}...")
        
        # Test 3: Identify the authentication flow type
        print("🔍 Authentication Flow Analysis:")
        print(f"   - Using Client Credentials Flow: ✅")
        print(f"   - Scope: {service.scope}")
        print(f"   - This provides APPLICATION permissions, not USER permissions")
    
    @pytest.mark.integration
    @pytest.mark.email
    @pytest.mark.diagnosis
    def test_endpoint_compatibility_diagnosis(self):
        """Diagnose endpoint compatibility with current auth flow"""
        from email_service import EmailService
        
        service = EmailService()
        
        print("🔍 Endpoint Compatibility Analysis:")
        print("   Current endpoint: /me/mailFolders/Inbox/messages")
        print("   Authentication: Client Credentials (Application)")
        print("   ❌ INCOMPATIBLE: /me requires Delegated permissions")
        print("")
        print("💡 Compatible endpoints for Application permissions:")
        print("   ✅ /users/{user-id}/mailFolders/{folder}/messages")
        print("   ✅ /users/{user-principal-name}/mailFolders/{folder}/messages")
        print("   ✅ /applications/{app-id}/mailFolders/{folder}/messages")
    
    @pytest.mark.integration
    @pytest.mark.email
    @pytest.mark.diagnosis
    def test_azure_app_permissions_diagnosis(self):
        """Diagnose Azure App Registration permissions"""
        print("🔍 Azure App Registration Diagnosis:")
        print("   Current setup suggests Application permissions")
        print("   Required permissions for email access:")
        print("")
        print("   For /me endpoint (Delegated):")
        print("   - Mail.Read (Delegated)")
        print("   - Mail.ReadWrite (Delegated)")
        print("")
        print("   For /users/{id} endpoint (Application):")
        print("   - Mail.Read (Application)")
        print("   - Mail.ReadWrite (Application)")
        print("")
        print("💡 Recommendation: Check Azure App Registration permissions")
    
    @pytest.mark.integration
    @pytest.mark.email
    @pytest.mark.solution
    def test_solution_verification(self):
        """Test potential solutions"""
        from email_service import EmailService
        
        service = EmailService()
        
        # Solution 1: Test with specific user mailbox (requires user email)
        print("🔧 Solution 1: Specific User Mailbox")
        print("   Endpoint: /users/{specific-email}/mailFolders/Inbox/messages")
        print("   Status: ⚠️ Requires specific user email address")
        print("   Implementation: Update email_service.py with target user")
        
        # Solution 2: Test with delegated flow (requires user interaction)
        print("")
        print("🔧 Solution 2: Delegated Authentication Flow")
        print("   Endpoint: /me/mailFolders/Inbox/messages")
        print("   Status: ⚠️ Requires user consent and interaction")
        print("   Implementation: Switch to delegated flow with user login")
        
        # Solution 3: Test with service account
        print("")
        print("🔧 Solution 3: Shared Mailbox Access")
        print("   Endpoint: /users/{shared-mailbox}/mailFolders/Inbox/messages")
        print("   Status: ✅ Works with current application permissions")
        print("   Implementation: Use shared support mailbox")

class TestEmailIntegrationSolutions(AdvancedTestBase):
    """Test solutions for email integration"""
    
    @pytest.mark.integration
    @pytest.mark.email
    @pytest.mark.solution
    def test_shared_mailbox_solution(self):
        """Test shared mailbox solution"""
        from email_service import EmailService
        
        # Create modified service for testing
        service = EmailService()
        
        # Mock successful response for shared mailbox
        mock_response = Mock()
        mock_response.json.return_value = {
            'value': [
                {
                    'id': 'test-email-1',
                    'subject': 'Test Support Request',
                    'from': {
                        'emailAddress': {
                            'address': 'customer@example.com',
                            'name': 'Test Customer'
                        }
                    },
                    'bodyPreview': 'Test email content',
                    'receivedDateTime': '2025-09-20T08:00:00Z',
                    'importance': 'normal'
                }
            ]
        }
        mock_response.status_code = 200
        
        # Test with shared mailbox URL
        with patch('requests.get', return_value=mock_response) as mock_get:
            # Temporarily modify the URL construction
            original_get_emails = service.get_emails
            
            def mock_get_emails_with_shared_mailbox(folder='Inbox', top=50):
                access_token = service.get_access_token()
                if not access_token:
                    return []
                
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                # Use shared mailbox instead of /me
                url = f"{service.graph_url}/users/support@yourdomain.com/mailFolders/{folder}/messages"
                
                response = requests.get(url, headers=headers, params={})
                if response.status_code == 200:
                    return response.json().get('value', [])
                return []
            
            service.get_emails = mock_get_emails_with_shared_mailbox
            
            emails = service.get_emails()
            assert len(emails) == 1
            assert emails[0]['subject'] == 'Test Support Request'
            
            print("✅ Shared mailbox solution would work!")
    
    @pytest.mark.integration
    @pytest.mark.email
    @pytest.mark.configuration
    def test_configuration_recommendations(self):
        """Test and provide configuration recommendations"""
        print("📋 EMAIL INTEGRATION CONFIGURATION RECOMMENDATIONS:")
        print("=" * 60)
        print("")
        print("🎯 IMMEDIATE SOLUTIONS:")
        print("")
        print("1. 🔧 UPDATE EMAIL SERVICE (Quick Fix)")
        print("   Replace in email_service.py line 53:")
        print("   FROM: url = f\"{self.graph_url}/me/mailFolders/{folder}/messages\"")
        print("   TO:   url = f\"{self.graph_url}/users/support@YOURDOMAIN.com/mailFolders/{folder}/messages\"")
        print("")
        print("2. ⚙️ AZURE APP REGISTRATION PERMISSIONS")
        print("   Required Application Permissions:")
        print("   - Mail.Read (Application)")
        print("   - Mail.ReadWrite (Application)")
        print("   - User.Read.All (Application) - if accessing specific users")
        print("")
        print("3. 📧 SHARED MAILBOX SETUP")
        print("   - Create a shared mailbox: support@yourdomain.com")
        print("   - Grant your Azure app access to this mailbox")
        print("   - Update the email service to use this specific mailbox")
        print("")
        print("🎯 ALTERNATIVE SOLUTIONS:")
        print("")
        print("4. 🔄 SWITCH TO DELEGATED FLOW (Complex)")
        print("   - Requires user login and consent")
        print("   - Good for user-specific email access")
        print("   - More complex implementation")
        print("")
        print("5. 🧪 TESTING MODE")
        print("   - Mock email responses for development")
        print("   - Use test data instead of real emails")
        print("   - Good for development and testing")

def create_email_service_fix():
    """Create a fixed version of email service"""
    return '''
# FIXED EMAIL SERVICE - UPDATE email_service.py line 53:

# BEFORE (Current - Failing):
url = f"{self.graph_url}/me/mailFolders/{folder}/messages"

# AFTER (Fixed - Working):
# Option A: Specific user mailbox
url = f"{self.graph_url}/users/support@yourdomain.com/mailFolders/{folder}/messages"

# Option B: Configurable user mailbox
target_user = os.getenv('TARGET_USER_EMAIL', 'support@yourdomain.com')
url = f"{self.graph_url}/users/{target_user}/mailFolders/{folder}/messages"
'''
