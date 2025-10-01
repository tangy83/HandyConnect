# Microsoft Graph API Testing Guide
## Complete Testing and Verification Process

---

## 🎯 **Overview**

This guide provides step-by-step instructions to ensure Microsoft Graph API is fully functional in HandyConnect. We'll test authentication, permissions, email access, and end-to-end functionality.

---

## 📋 **Prerequisites Checklist**

Before testing, ensure you have:

- [ ] **Azure Active Directory tenant** (personal or organizational)
- [ ] **Azure App Registration** created
- [ ] **Client ID, Client Secret, and Tenant ID** obtained
- [ ] **API permissions** granted
- [ ] **Valid .env configuration**
- [ ] **HandyConnect application running**

---

## 🔧 **Step 1: Azure App Registration Setup**

### 1.1 Create App Registration

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to**: Azure Active Directory → App registrations
3. **Click**: "New registration"
4. **Configure**:
   - **Name**: `HandyConnect`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: Leave blank (not needed for this app)
5. **Click**: "Register"

### 1.2 Get Required Credentials

After registration, note down:

- **Application (client) ID** → Use as `CLIENT_ID`
- **Directory (tenant) ID** → Use as `TENANT_ID`

### 1.3 Create Client Secret

1. **Go to**: Certificates & secrets
2. **Click**: "New client secret"
3. **Add description**: `HandyConnect Secret`
4. **Expires**: Choose appropriate duration (24 months recommended)
5. **Click**: "Add"
6. **Copy the secret value** → Use as `CLIENT_SECRET` (⚠️ **Save immediately - you can't see it again!**)

### 1.4 Configure API Permissions

1. **Go to**: API permissions
2. **Click**: "Add a permission"
3. **Select**: Microsoft Graph
4. **Choose**: Application permissions
5. **Add these permissions**:
   - `Mail.Read` - Read mail in all mailboxes
   - `Mail.ReadWrite` - Read and write mail in all mailboxes
   - `User.Read.All` - Read all users' full profiles
6. **Click**: "Add permissions"
7. **Click**: "Grant admin consent" (⚠️ **Required for application permissions**)

---

## 🔧 **Step 2: Environment Configuration**

### 2.1 Update .env File

Replace placeholder values in your `.env` file:

```env
# Microsoft Graph API Configuration
CLIENT_ID=your_actual_azure_client_id_here
CLIENT_SECRET=your_actual_azure_client_secret_here
TENANT_ID=your_actual_azure_tenant_id_here
SCOPE=https://graph.microsoft.com/.default

# OpenAI Configuration
OPENAI_API_KEY=your_actual_openai_api_key_here

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_actual_secret_key_here

# Data Storage Configuration
DATA_DIR=data
TASKS_FILE=data/tasks.json

# Email Polling Configuration
POLL_INTERVAL_MINUTES=5
SUPPORT_EMAIL_FOLDER=Inbox
```

### 2.2 Restart Application

```bash
# Stop and restart Docker container
docker-compose down
docker-compose up -d

# Check if container is running
docker ps
```

---

## 🧪 **Step 3: Testing Microsoft Graph API**

### 3.1 Test Authentication

```bash
# Test 1: Check if authentication is working
curl -X POST http://localhost:5001/api/test/graph-auth | jq .

# Expected Success Response:
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

# Expected Error Response:
{
  "status": "error",
  "message": "Microsoft Graph authentication failed",
  "data": {
    "error": "Invalid client credentials",
    "details": "AADSTS7000215: Invalid client secret is provided"
  }
}
```

### 3.2 Test Email Access

```bash
# Test 2: Check if we can access emails
curl -X POST http://localhost:5001/api/test/email-access | jq .

# Expected Success Response:
{
  "status": "success",
  "message": "Email access successful",
  "data": {
    "emails_found": 15,
    "sample_email": {
      "subject": "Customer Support Request",
      "from": "customer@example.com",
      "received": "2025-09-15T10:30:00Z"
    },
    "permissions": ["Mail.Read", "Mail.ReadWrite"]
  }
}

# Expected Error Response:
{
  "status": "error",
  "message": "Email access failed",
  "data": {
    "error": "Insufficient privileges",
    "details": "The application does not have the required permissions"
  }
}
```

### 3.3 Test Email Processing

```bash
# Test 3: Test complete email processing pipeline
curl -X POST http://localhost:5001/api/test/email-processing | jq .

# Expected Success Response:
{
  "status": "success",
  "message": "Email processing pipeline working",
  "data": {
    "emails_processed": 3,
    "tasks_created": 3,
    "ai_processing": {
      "summarization": "working",
      "categorization": "working",
      "priority_assignment": "working"
    },
    "processing_time": "2.3 seconds"
  }
}
```

### 3.4 Test End-to-End Workflow

```bash
# Test 4: Test complete workflow
curl -X POST http://localhost:5001/api/test/end-to-end | jq .

# Expected Success Response:
{
  "status": "success",
  "message": "End-to-end workflow successful",
  "data": {
    "authentication": "✅ Working",
    "email_access": "✅ Working",
    "ai_processing": "✅ Working",
    "task_creation": "✅ Working",
    "data_storage": "✅ Working",
    "api_endpoints": "✅ Working"
  }
}
```

---

## 🔍 **Step 4: Manual Verification**

### 4.1 Check Application Logs

```bash
# Check for authentication errors
docker logs handyconnect-handyconnect-1 | grep -i "error\|auth\|token"

# Check for successful email processing
docker logs handyconnect-handyconnect-1 | grep -i "email\|processed\|task"
```

### 4.2 Verify Data Creation

```bash
# Check if tasks are being created
curl -s http://localhost:5001/api/tasks | jq .

# Check if threads are being created
curl -s http://localhost:5001/api/threads | jq .
```

### 4.3 Test Email Polling

```bash
# Manually trigger email polling
curl -X POST http://localhost:5001/api/poll-emails | jq .

# Check the response for processed emails
```

---

## 🚨 **Common Issues and Solutions**

### Issue 1: Authentication Failed

**Error**: `AADSTS7000215: Invalid client secret is provided`

**Solution**:
1. Verify `CLIENT_SECRET` is correct in `.env`
2. Check if secret has expired
3. Create a new client secret if needed

### Issue 2: Insufficient Privileges

**Error**: `Insufficient privileges to complete the operation`

**Solution**:
1. Check API permissions in Azure Portal
2. Ensure admin consent is granted
3. Verify permissions include `Mail.Read` and `Mail.ReadWrite`

### Issue 3: Tenant Not Found

**Error**: `Unable to get authority configuration`

**Solution**:
1. Verify `TENANT_ID` is correct
2. Check if tenant ID is in GUID format
3. Ensure tenant exists and is accessible

### Issue 4: No Emails Found

**Issue**: Authentication works but no emails are returned

**Solution**:
1. Check if the mailbox has emails
2. Verify `SUPPORT_EMAIL_FOLDER` setting
3. Check if emails are in the correct folder
4. Test with a different folder (e.g., "SentItems")

---

## ✅ **Success Criteria**

Microsoft Graph API is functional when:

- [ ] **Authentication test passes** (no token errors)
- [ ] **Email access test passes** (can read emails)
- [ ] **Email processing test passes** (AI processing works)
- [ ] **End-to-end test passes** (complete workflow works)
- [ ] **No errors in application logs**
- [ ] **Tasks are being created from emails**
- [ ] **Email polling works automatically**

---

## 🔄 **Ongoing Monitoring**

### Daily Checks

```bash
# Quick health check
curl -s http://localhost:5001/api/health | jq .

# Check recent email processing
curl -X POST http://localhost:5001/api/poll-emails | jq .
```

### Weekly Checks

```bash
# Full system test
curl -X POST http://localhost:5001/api/test/end-to-end | jq .

# Check logs for any issues
docker logs handyconnect-handyconnect-1 --since 7d | grep -i error
```

---

## 📞 **Troubleshooting Support**

If you encounter issues:

1. **Check the logs**: `docker logs handyconnect-handyconnect-1 --tail 50`
2. **Verify credentials**: Ensure all values in `.env` are correct
3. **Test permissions**: Use the testing endpoints above
4. **Check Azure Portal**: Verify app registration and permissions
5. **Review this guide**: Follow each step carefully

---

## 🎯 **Next Steps**

Once Microsoft Graph API is functional:

1. **Monitor email processing** regularly
2. **Set up alerts** for authentication failures
3. **Configure email filtering** if needed
4. **Test with different email types** to ensure robust processing
5. **Move to frontend development** (Phase 6-8)

---

*This guide ensures your Microsoft Graph API integration is fully functional and ready for production use.*




