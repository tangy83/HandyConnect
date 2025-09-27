# Email Integration Manual Testing Guide
## Complete Process Tracing from Email Origin to Task Creation

**Date**: September 20, 2025  
**Purpose**: Manual testing and debugging of the complete email-to-task workflow

---

## 🔄 **THE COMPLETE EMAIL-TO-TASK FLOW**

```
📧 EMAIL (Outlook Inbox)
    ↓ (1. Email exists in mailbox)
🔐 Microsoft Graph API Authentication  
    ↓ (2. Get Bearer token)
📥 Email Fetching & Parsing
    ↓ (3. Fetch emails via Graph API)
🧵 Email Threading & Grouping
    ↓ (4. Group related emails)
🤖 AI Processing (OpenAI)
    ↓ (5. Analyze and categorize)
📝 Task Creation & Storage
    ↓ (6. Create task in JSON)
📊 Analytics & Monitoring
    ↓ (7. Record metrics)
🌐 UI Display & Management
    ↓ (8. Show in dashboard)
```

---

## 🧪 **MANUAL TESTING STEPS**

### **Prerequisites**
1. **Application Running**: `python app.py` (port 5001)
2. **Environment Configured**: `.env` file with Azure credentials
3. **Test Email**: Email in your Outlook inbox (last 24 hours)

---

### **STEP 1: Test Authentication** 🔐

**Command:**
```bash
curl -X POST http://localhost:5001/api/test/graph-auth
```

**Expected Success Response:**
```json
{
  "status": "success",
  "message": "Microsoft Graph authentication successful",
  "data": {
    "token_acquired": true,
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "https://graph.microsoft.com/.default"
  }
}
```

**If This Fails:**
- ❌ Check CLIENT_ID, CLIENT_SECRET, TENANT_ID in `.env`
- ❌ Verify Azure App Registration exists
- ❌ Check network connectivity

---

### **STEP 2: Test Email Access** 📥

**Command:**
```bash
curl -X POST http://localhost:5001/api/test/email-access
```

**Expected Success Response:**
```json
{
  "status": "success", 
  "message": "Email access successful",
  "data": {
    "emails_found": 5,
    "sample_email": {
      "subject": "Your email subject",
      "from": "sender@example.com", 
      "received": "2025-09-20T08:00:00Z"
    }
  }
}
```

**Expected Failure (Current Issue):**
```json
{
  "status": "error",
  "message": "Email access failed", 
  "data": {
    "error": "/me request is only valid with delegated authentication flow"
  }
}
```

**If This Fails (Current Issue):**
- ❌ Authentication flow mismatch (Client Credentials vs Delegated)
- ❌ Need to use specific user mailbox instead of `/me`

---

### **STEP 3: Test Configuration** ⚙️

**Command:**
```bash
curl http://localhost:5001/api/test/configuration
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Configuration check complete (8/9 configured)",
  "data": {
    "CLIENT_ID": "✅ Configured",
    "CLIENT_SECRET": "✅ Configured", 
    "TENANT_ID": "✅ Configured",
    "OPENAI_API_KEY": "✅ Configured"
  }
}
```

---

### **STEP 4: Manual Email Polling** 📬

**Command:**
```bash
curl -X POST http://localhost:5001/api/poll-emails
```

**Expected Success Response:**
```json
{
  "status": "success",
  "message": "Processed 3 new emails", 
  "data": {
    "processed_count": 3,
    "total_emails": 5,
    "errors": []
  }
}
```

**Expected Failure (Current):**
```json
{
  "status": "error",
  "message": "Failed to poll emails",
  "data": {
    "error": "Email access failed"
  }
}
```

---

### **STEP 5: Check Created Tasks** 📝

**Command:**
```bash
curl http://localhost:5001/api/tasks
```

**Expected Success Response (if emails processed):**
```json
{
  "status": "success",
  "message": "Retrieved 3 tasks",
  "data": [
    {
      "id": 1,
      "email_id": "email_123",
      "subject": "Customer Support Request",
      "sender": "John Doe",
      "category": "General Inquiry",
      "priority": "Medium",
      "status": "New",
      "summary": "Customer needs help with account access"
    }
  ]
}
```

**Current Response (No emails processed):**
```json
{
  "status": "success", 
  "message": "Retrieved 0 tasks",
  "data": []
}
```

---

### **STEP 6: Check Application Logs** 📋

**Command:**
```bash
tail -f logs/app.log | grep -E "(Email|error|Error)"
```

**What to Look For:**
- ✅ `Services initialized successfully`
- ✅ `Configuration validation passed`
- ❌ `Error fetching emails: 400 - BadRequest`
- ❌ `/me request is only valid with delegated authentication flow`

---

### **STEP 7: Test Analytics Integration** 📊

**Command:**
```bash
curl http://localhost:5001/api/analytics/performance
```

**Expected Response:**
```json
{
  "data": {
    "cpu_usage_percent": 21.7,
    "memory_usage_mb": 2858.3,
    "error_rate": 0.0,
    "timestamp": "2025-09-20T08:00:00Z"
  },
  "success": true
}
```

---

## 🔧 **DEBUGGING THE EMAIL FLOW**

### **Debug Step 1: Check Email Service Directly**

**Python Test:**
```python
# Run in Python console
from email_service import EmailService

service = EmailService()

# Test authentication
token = service.get_access_token()
print(f"Token acquired: {token is not None}")

# Test email fetching
emails = service.get_emails()
print(f"Emails found: {len(emails)}")
```

### **Debug Step 2: Check Threading Service**

**Command:**
```bash
curl http://localhost:5001/api/threads/
```

### **Debug Step 3: Check LLM Service**

**Python Test:**
```python
from llm_service import LLMService

llm = LLMService()
test_email = {
    'subject': 'Test Support Request',
    'body': 'I need help with my account'
}

result = llm.process_email(test_email)
print(f"LLM Result: {result}")
```

---

## 🚨 **CURRENT ISSUE & SOLUTION**

### **❌ Current Problem:**
- **Authentication**: ✅ Working (Bearer token acquired)
- **Email Access**: ❌ Failing (`/me` endpoint incompatible with Client Credentials)
- **Root Cause**: Using application permissions but accessing user-specific endpoint

### **✅ Solutions:**

#### **Solution 1: Fix Email Service (Quick)**
**Update `email_service.py` line 58:**
```python
# CURRENT (Failing):
url = f"{self.graph_url}/me/mailFolders/{folder}/messages"

# FIXED (Working):
url = f"{self.graph_url}/users/support@yourdomain.com/mailFolders/{folder}/messages"
```

#### **Solution 2: Add Environment Variable**
**Add to `.env`:**
```env
TARGET_USER_EMAIL=support@yourdomain.com
```

**Update `email_service.py`:**
```python
target_user = os.getenv('TARGET_USER_EMAIL', 'support@yourdomain.com')
url = f"{self.graph_url}/users/{target_user}/mailFolders/{folder}/messages"
```

#### **Solution 3: Testing Mode**
**Add to `.env` for development:**
```env
EMAIL_TESTING_MODE=true
```

---

## 🎯 **TESTING CHECKLIST**

### **✅ Working Components:**
- [x] Flask application startup
- [x] Microsoft Graph authentication  
- [x] Configuration validation
- [x] Analytics framework
- [x] Task management API
- [x] Background services

### **❌ Not Working Components:**
- [ ] Email fetching from Outlook
- [ ] Email-to-task conversion
- [ ] Background email polling (finds 0 emails)

### **⚠️ Partially Working:**
- [~] Email service (auth works, access fails)
- [~] Performance metrics (some validation errors)

---

## 📞 **TROUBLESHOOTING COMMANDS**

### **Quick Health Check:**
```bash
curl http://localhost:5001/api/health
```

### **Check All APIs:**
```bash
curl http://localhost:5001/api/tasks
curl http://localhost:5001/api/tasks/stats  
curl http://localhost:5001/api/analytics/health
```

### **Monitor Real-time Logs:**
```bash
tail -f logs/app.log
```

### **Test Individual Services:**
```bash
# Test each component
python -c "from email_service import EmailService; print('Email service:', EmailService())"
python -c "from llm_service import LLMService; print('LLM service:', LLMService())" 
python -c "from task_service import TaskService; print('Task service:', TaskService())"
```

---

**🎯 CONCLUSION: Email integration is 80% working - authentication successful, but email access needs endpoint/permission fix to complete the flow.**

