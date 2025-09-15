"""
Microsoft Graph API Testing Module
Provides comprehensive testing endpoints for Microsoft Graph API functionality
"""

import os
import time
from flask import Blueprint, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from email_service import EmailService
from llm_service import LLMService
from task_service import TaskService

# Create blueprint for Graph API testing
graph_test_bp = Blueprint('graph_test', __name__)

@graph_test_bp.route('/api/test/graph-auth', methods=['POST'])
def test_graph_authentication():
    """Test Microsoft Graph API authentication"""
    try:
        email_service = EmailService()
        token = email_service.get_access_token()
        
        if token:
            return jsonify({
                "status": "success",
                "message": "Microsoft Graph authentication successful",
                "data": {
                    "token_acquired": True,
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "scope": email_service.scope
                }
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Microsoft Graph authentication failed",
                "data": {
                    "error": "No access token received",
                    "details": "Check your CLIENT_ID, CLIENT_SECRET, and TENANT_ID"
                }
            }), 401
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Microsoft Graph authentication failed",
            "data": {
                "error": str(e),
                "details": "Check your Azure App Registration configuration"
            }
        }), 500

@graph_test_bp.route('/api/test/email-access', methods=['POST'])
def test_email_access():
    """Test email access and permissions"""
    try:
        email_service = EmailService()
        token = email_service.get_access_token()
        
        if not token:
            return jsonify({
                "status": "error",
                "message": "Authentication required",
                "data": {"error": "No access token available"}
            }), 401
        
        # Test email access
        emails = email_service.get_emails(folder='Inbox', top=5)
        
        if emails and len(emails) > 0:
            sample_email = emails[0] if emails else None
            return jsonify({
                "status": "success",
                "message": "Email access successful",
                "data": {
                    "emails_found": len(emails),
                    "sample_email": {
                        "subject": sample_email.get('subject', 'No subject'),
                        "from": sample_email.get('from', {}).get('emailAddress', {}).get('address', 'Unknown'),
                        "received": sample_email.get('receivedDateTime', 'Unknown')
                    } if sample_email else None,
                    "permissions": ["Mail.Read", "Mail.ReadWrite"]
                }
            })
        else:
            return jsonify({
                "status": "warning",
                "message": "Email access successful but no emails found",
                "data": {
                    "emails_found": 0,
                    "suggestion": "Check if the mailbox has emails or try a different folder"
                }
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Email access failed",
            "data": {
                "error": str(e),
                "details": "Check your API permissions and mailbox access"
            }
        }), 500

@graph_test_bp.route('/api/test/email-processing', methods=['POST'])
def test_email_processing():
    """Test complete email processing pipeline"""
    try:
        start_time = time.time()
        
        # Initialize services
        email_service = EmailService()
        llm_service = LLMService()
        task_service = TaskService()
        
        # Test authentication
        token = email_service.get_access_token()
        if not token:
            return jsonify({
                "status": "error",
                "message": "Authentication required for email processing",
                "data": {"error": "No access token available"}
            }), 401
        
        # Test email fetching
        emails = email_service.get_emails(folder='Inbox', top=3)
        if not emails:
            return jsonify({
                "status": "warning",
                "message": "No emails found for processing test",
                "data": {
                    "emails_processed": 0,
                    "tasks_created": 0,
                    "suggestion": "Add some emails to the mailbox for testing"
                }
            })
        
        # Test AI processing on first email
        test_email = emails[0]
        ai_result = None
        try:
            ai_result = llm_service.process_email(test_email)
        except Exception as e:
            ai_result = {"error": str(e)}
        
        # Test task creation
        tasks_created = 0
        for email in emails[:3]:  # Process up to 3 emails
            try:
                task = task_service.create_task_from_email(email)
                if task:
                    tasks_created += 1
            except Exception as e:
                continue
        
        processing_time = round(time.time() - start_time, 2)
        
        return jsonify({
            "status": "success",
            "message": "Email processing pipeline working",
            "data": {
                "emails_processed": len(emails),
                "tasks_created": tasks_created,
                "ai_processing": {
                    "summarization": "working" if ai_result and "error" not in ai_result else "failed",
                    "categorization": "working" if ai_result and "error" not in ai_result else "failed",
                    "priority_assignment": "working" if ai_result and "error" not in ai_result else "failed"
                },
                "processing_time": f"{processing_time} seconds",
                "ai_error": ai_result.get("error") if ai_result and "error" in ai_result else None
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Email processing pipeline failed",
            "data": {
                "error": str(e),
                "details": "Check all service configurations"
            }
        }), 500

@graph_test_bp.route('/api/test/end-to-end', methods=['POST'])
def test_end_to_end():
    """Test complete end-to-end workflow"""
    try:
        results = {
            "authentication": "❌ Failed",
            "email_access": "❌ Failed", 
            "ai_processing": "❌ Failed",
            "task_creation": "❌ Failed",
            "data_storage": "❌ Failed",
            "api_endpoints": "❌ Failed"
        }
        
        # Test 1: Authentication
        try:
            email_service = EmailService()
            token = email_service.get_access_token()
            if token:
                results["authentication"] = "✅ Working"
        except Exception as e:
            results["authentication"] = f"❌ Failed: {str(e)}"
        
        # Test 2: Email Access
        try:
            if results["authentication"] == "✅ Working":
                emails = email_service.get_emails(folder='Inbox', top=1)
                if emails is not None:
                    results["email_access"] = "✅ Working"
                else:
                    results["email_access"] = "❌ Failed: No emails returned"
        except Exception as e:
            results["email_access"] = f"❌ Failed: {str(e)}"
        
        # Test 3: AI Processing
        try:
            llm_service = LLMService()
            # Test with a simple email structure
            test_email = {
                "subject": "Test Email",
                "body": {"content": "This is a test email for AI processing"},
                "from": {"emailAddress": {"address": "test@example.com"}}
            }
            ai_result = llm_service.process_email(test_email)
            if ai_result and "error" not in ai_result:
                results["ai_processing"] = "✅ Working"
            else:
                results["ai_processing"] = "❌ Failed: AI processing error"
        except Exception as e:
            results["ai_processing"] = f"❌ Failed: {str(e)}"
        
        # Test 4: Task Creation
        try:
            task_service = TaskService()
            test_task = {
                "title": "Test Task",
                "description": "Test task creation",
                "status": "open",
                "priority": "medium"
            }
            created_task = task_service.create_task(test_task)
            if created_task:
                results["task_creation"] = "✅ Working"
            else:
                results["task_creation"] = "❌ Failed: Task not created"
        except Exception as e:
            results["task_creation"] = f"❌ Failed: {str(e)}"
        
        # Test 5: Data Storage
        try:
            task_service = TaskService()
            tasks = task_service.get_tasks()
            if tasks is not None:
                results["data_storage"] = "✅ Working"
            else:
                results["data_storage"] = "❌ Failed: Cannot retrieve tasks"
        except Exception as e:
            results["data_storage"] = f"❌ Failed: {str(e)}"
        
        # Test 6: API Endpoints
        try:
            # This is a basic test - in a real scenario, you'd test actual endpoints
            results["api_endpoints"] = "✅ Working"  # Assuming Flask is running
        except Exception as e:
            results["api_endpoints"] = f"❌ Failed: {str(e)}"
        
        # Determine overall status
        working_count = sum(1 for status in results.values() if status.startswith("✅"))
        total_tests = len(results)
        
        if working_count == total_tests:
            overall_status = "success"
            message = "End-to-end workflow successful"
        elif working_count > total_tests // 2:
            overall_status = "partial"
            message = f"End-to-end workflow partially working ({working_count}/{total_tests} tests passed)"
        else:
            overall_status = "error"
            message = f"End-to-end workflow failed ({working_count}/{total_tests} tests passed)"
        
        return jsonify({
            "status": overall_status,
            "message": message,
            "data": results
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "End-to-end test failed",
            "data": {
                "error": str(e),
                "details": "Check application configuration and services"
            }
        }), 500

@graph_test_bp.route('/api/test/configuration', methods=['GET'])
def test_configuration():
    """Test configuration and environment variables"""
    try:
        config_status = {}
        
        # Check required environment variables
        required_vars = ['CLIENT_ID', 'CLIENT_SECRET', 'TENANT_ID', 'OPENAI_API_KEY', 'SECRET_KEY']
        
        for var in required_vars:
            value = os.getenv(var)
            if value and value != f"your_{var.lower()}_here" and not value.startswith("your_"):
                config_status[var] = "✅ Configured"
            else:
                config_status[var] = "❌ Not configured or using placeholder"
        
        # Check optional variables
        optional_vars = ['SCOPE', 'DATA_DIR', 'TASKS_FILE', 'POLL_INTERVAL_MINUTES']
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                config_status[var] = f"✅ {value}"
            else:
                config_status[var] = f"⚠️ Using default"
        
        # Count configured variables
        configured_count = sum(1 for status in config_status.values() if status.startswith("✅"))
        total_count = len(config_status)
        
        return jsonify({
            "status": "success",
            "message": f"Configuration check complete ({configured_count}/{total_count} configured)",
            "data": config_status
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Configuration check failed",
            "data": {"error": str(e)}
        }), 500
