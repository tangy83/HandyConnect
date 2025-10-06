# Manual Email Response Feature - Fix Plan

## 🎯 Objective
Enable the "Send Response" button in Case Detail modal to send emails FROM `handymyjob@outlook.com` TO customers.

**This is DIFFERENT from auto-acknowledgment emails that send when a case is created.**

---

## 🔴 Current Issue

**Error**: "Failed to send email response: Failed to send email"

**Root Cause**: Missing authentication token file (`ms_graph_token.json`)

**Impact**: Portal users cannot manually respond to customers from the UI

---

## ✅ What's Already Working

1. ✅ UI: "Send Response" button and modal
2. ✅ API endpoint: `/api/cases/send-response`
3. ✅ Backend code: `send_email_response()` in `EmailService`
4. ✅ Environment variables: `CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID`, `SCOPES`
5. ✅ Mail.Send permission in `.env` file

---

## 🚀 PHASED FIX PLAN

---

## **PHASE 1: Authenticate Microsoft Graph API** ⏱️ 10 minutes
**Status**: 🔴 NOT STARTED  
**Priority**: 🔥 CRITICAL - Must complete before other phases

### Goal
Create the authentication token file so the app can send emails via Microsoft Graph API.

### Steps

#### Step 1.1: Stop Background App (1 min)
```bash
# Kill any background processes
lsof -ti:5001 | xargs kill -9 2>/dev/null
```

#### Step 1.2: Run App in Foreground (2 min)
```bash
# Activate virtual environment
cd /Users/tanujsaluja/HandyConnect
source venv/bin/activate

# Run app in foreground (NOT background)
python app.py
```

**Expected Output:**
```
To sign in, use a web browser to open the page:
https://microsoft.com/devicelogin

And enter the code: XXXXXXXX
```

#### Step 1.3: Complete Device Code Authentication (5 min)
1. Open browser: https://microsoft.com/devicelogin
2. Enter the code shown in terminal
3. Sign in with: `handymyjob@outlook.com`
4. Review permissions:
   - ✅ Read your mail
   - ✅ Send mail as you
   - ✅ Read user profile
5. Click "Accept"

**Expected Terminal Output:**
```
✅ Authentication successful!
✅ Token saved to ms_graph_token.json
🚀 Starting Flask app...
 * Running on http://127.0.0.1:5001
```

#### Step 1.4: Verify Token Created (1 min)
```bash
# In a NEW terminal tab/window
cd /Users/tanujsaluja/HandyConnect
ls -la ms_graph_token.json

# Should show:
# -rw-r--r--  1 tanujsaluja  staff  XXXX Oct  6 XX:XX ms_graph_token.json
```

#### Step 1.5: Run Diagnostic Test (1 min)
```bash
# Keep app running in first terminal
# In second terminal:
source venv/bin/activate
python test_email_send.py
```

**Expected Output:**
```
🔍 EMAIL SEND DIAGNOSTIC TOOL
============================================================
Environment Variables: ✅ PASS
Token File:           ✅ PASS
Email Service:        ✅ PASS
============================================================
🎉 ALL CHECKS PASSED!
```

### Acceptance Criteria
- ✅ Token file exists: `ms_graph_token.json`
- ✅ Token contains `Mail.Send` permission
- ✅ Token is not expired
- ✅ Diagnostic test passes all checks
- ✅ App running on http://localhost:5001

### Troubleshooting
**Problem**: No device code appears in terminal  
**Solution**: Check if port 5001 is already in use: `lsof -i:5001`

**Problem**: Browser shows "Invalid code"  
**Solution**: Code expires after 15 minutes - restart `python app.py` for new code

**Problem**: "Permission denied" error  
**Solution**: Use correct Microsoft account that owns `handymyjob@outlook.com`

---

## **PHASE 2: Test Manual Email Sending** ⏱️ 5 minutes
**Status**: 🟡 WAITING FOR PHASE 1  
**Priority**: 🔥 HIGH

### Goal
Verify that the "Send Response" button successfully sends emails to customers.

### Steps

#### Step 2.1: Open Cases Page (1 min)
1. Open browser: http://localhost:5001
2. Click "Cases" in top menu
3. Click on any case (e.g., Case #2510050001)

#### Step 2.2: Navigate to Threads Tab (1 min)
1. In case detail modal, click "Threads" tab
2. Verify you see the original customer email
3. Click "Send Response" button (top right)

#### Step 2.3: Compose Test Email (2 min)
**Send Response Modal should appear with:**
- **To**: (auto-filled with customer email)
- **Subject**: Re: [original subject]
- **Message**: (empty - type your response)

**Type a test message:**
```
Dear [Customer Name],

Thank you for contacting HandyConnect. We have received your request 
regarding [issue description].

Our team is currently reviewing your case and will provide an update 
within 24 hours.

Best regards,
HandyConnect Support Team
```

✅ Check "Include case details in email signature"

#### Step 2.4: Send Email (1 min)
1. Click "Send Response" button
2. **Expected**: Modal closes, no error
3. **Expected**: Email sent successfully

**If error appears:**
- Screenshot the error
- Check logs: `tail -50 logs/app.log`
- Move to Phase 3 (Error Handling)

#### Step 2.5: Verify Email Sent (1 min)
**Check Timeline Tab:**
1. Click "Timeline" tab in case modal
2. Look for new event: "Response sent to customer"
3. Verify timestamp is current

**Check Customer Inbox:**
1. Log into customer email account
2. Check inbox for email FROM `handymyjob@outlook.com`
3. Verify subject, body, and case details signature

### Acceptance Criteria
- ✅ "Send Response" button works without errors
- ✅ Modal closes after sending
- ✅ Email appears in customer inbox within 1 minute
- ✅ Timeline shows "Response sent" event
- ✅ Email format is professional and readable
- ✅ Case details signature included (if checkbox was checked)

### Troubleshooting
**Problem**: Error "Failed to send email"  
**Solution**: Check app logs for specific error:
```bash
tail -100 logs/app.log | grep -A 10 "send_email_response"
```

**Problem**: Email not in customer inbox  
**Solution**: 
1. Check spam/junk folder
2. Verify email address is correct
3. Check Microsoft 365 admin center for delivery status

**Problem**: Timeline not updating  
**Solution**: Refresh case detail modal by closing and reopening

---

## **PHASE 3: Improve Error Handling** ⏱️ 2 hours
**Status**: 🟡 WAITING FOR PHASE 2  
**Priority**: 🟡 MEDIUM

### Goal
Provide clear, user-friendly error messages when email sending fails.

### Tasks

#### Task 3.1: Add Detailed Error Logging (30 min)
**File**: `features/core_services/email_service.py`

Update `send_email_response()` to log specific errors:

```python
def send_email_response(self, case_id: str, response_text: str, 
                      recipient_email: str, subject: str = None, 
                      include_case_details: bool = True) -> dict:
    """
    Send email response for a case using Microsoft Graph API
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'error_code': str (optional)
        }
    """
    try:
        # Get access token
        access_token = self.get_access_token()
        if not access_token:
            logger.error("❌ Failed to get access token for sending email")
            return {
                'success': False,
                'message': 'Authentication failed. Please contact administrator.',
                'error_code': 'AUTH_FAILED'
            }
        
        # Validate recipient email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, recipient_email):
            logger.error(f"❌ Invalid recipient email: {recipient_email}")
            return {
                'success': False,
                'message': f'Invalid email address: {recipient_email}',
                'error_code': 'INVALID_EMAIL'
            }
        
        # Get case context
        case_context = self._get_case_context(case_id)
        if not case_context:
            logger.error(f"❌ Case context not found for case {case_id}")
            return {
                'success': False,
                'message': f'Case not found: {case_id}',
                'error_code': 'CASE_NOT_FOUND'
            }
        
        # Build email content
        email_subject = subject or f"Re: {case_context.get('case_title', 'Case Update')}"
        email_body = response_text
        
        if include_case_details:
            case_details = f"""

----
Case Information:
• Case Number: {case_context.get('case_number', 'N/A')}
• Status: {case_context.get('status', 'N/A')}
• Priority: {case_context.get('priority', 'N/A')}

This email was sent from HandyConnect Case Management System.
Please reference the case number above in your reply.
"""
            email_body += case_details
        
        # Prepare Graph API request
        email_message = {
            "message": {
                "subject": email_subject,
                "body": {
                    "contentType": "Text",
                    "content": email_body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipient_email
                        }
                    }
                ]
            },
            "saveToSentItems": "true"
        }
        
        # Send via Microsoft Graph API
        send_url = f"{self.graph_url}/me/sendMail"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(send_url, headers=headers, json=email_message, timeout=30)
        
        if response.status_code == 202:
            logger.info(f"✅ Email sent successfully to {recipient_email}")
            return {
                'success': True,
                'message': 'Email sent successfully'
            }
        else:
            error_detail = response.text
            logger.error(f"❌ Graph API error: {response.status_code} - {error_detail}")
            return {
                'success': False,
                'message': f'Email service error: {response.status_code}',
                'error_code': 'GRAPH_API_ERROR',
                'details': error_detail
            }
            
    except requests.exceptions.Timeout:
        logger.error("❌ Email send timeout")
        return {
            'success': False,
            'message': 'Request timeout. Please try again.',
            'error_code': 'TIMEOUT'
        }
    except requests.exceptions.ConnectionError:
        logger.error("❌ Network connection error")
        return {
            'success': False,
            'message': 'Network error. Please check your connection.',
            'error_code': 'NETWORK_ERROR'
        }
    except Exception as e:
        logger.error(f"❌ Unexpected error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}',
            'error_code': 'UNKNOWN_ERROR'
        }
```

#### Task 3.2: Update API Endpoint (15 min)
**File**: `features/case_management/case_api.py`

Update `/api/cases/send-response` to return detailed errors:

```python
@case_bp.route('/send-response', methods=['POST'])
def send_email_response():
    """Send email response to customer via Microsoft Graph API"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['to', 'subject', 'message', 'case_id']):
            return error_response("Missing required fields: to, subject, message, case_id", 400)
        
        # Get case information
        case = case_service.get_case_by_id(data['case_id'])
        if not case:
            return error_response("Case not found", 404)
        
        # Import email service
        from ..core_services.email_service import EmailService
        email_service = EmailService()
        
        # Check if case details should be included
        include_case_details = data.get('includeCaseDetails', True)
        
        # Send email (returns dict with success, message, error_code)
        result = email_service.send_email_response(
            case_id=data['case_id'],
            response_text=data['message'],
            recipient_email=data['to'],
            subject=data['subject'],
            include_case_details=include_case_details
        )
        
        if result['success']:
            logger.info(f"✉️ Email sent successfully to {data['to']}: {data['subject']}")
            
            # Add timeline event
            timeline_event = {
                'event_id': str(uuid.uuid4()),
                'event_type': 'email_response_sent',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': 'portal_user',
                'description': f"Response sent: {data['subject']}",
                'metadata': {
                    'recipient': data['to'],
                    'subject': data['subject'],
                    'preview': data['message'][:100]
                }
            }
            
            # Update case timeline
            cases = case_service.load_cases()
            for i, c in enumerate(cases):
                if c['case_id'] == data['case_id']:
                    if 'timeline' not in c:
                        c['timeline'] = []
                    c['timeline'].append(timeline_event)
                    c['updated_at'] = datetime.utcnow().isoformat()
                    case_service.save_cases(cases)
                    break
            
            return success_response(
                data={"email_sent": True},
                message="Email response sent successfully"
            )
        else:
            # Return specific error message
            logger.error(f"❌ Failed to send email: {result['message']}")
            return error_response(result['message'], 500)
        
    except Exception as e:
        logger.error(f"❌ Error in send_email_response endpoint: {e}")
        import traceback
        traceback.print_exc()
        return error_response("Failed to send email response", 500)
```

#### Task 3.3: Improve Frontend Error Display (45 min)
**File**: `static/js/case-management.js`

Update `sendEmailResponse()` to show specific errors:

```javascript
async function sendEmailResponse() {
    if (!currentCaseId) {
        showError('No case selected');
        return;
    }
    
    try {
        const to = document.getElementById('response-to').value;
        const subject = document.getElementById('response-subject').value;
        let message = document.getElementById('response-message').value;
        const includeDetails = document.getElementById('include-case-details').checked;
        
        // Validate inputs
        if (!to || !subject || !message) {
            showError('Please fill in all required fields');
            return;
        }
        
        // Validate email format
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailPattern.test(to)) {
            showError('Please enter a valid email address');
            return;
        }
        
        // Find current case
        const currentCase = allCases.find(c => c.case_id === currentCaseId);
        if (!currentCase) {
            showError('Case not found');
            return;
        }
        
        // Show loading state
        const sendButton = document.querySelector('#emailResponseModal .btn-primary');
        const originalButtonText = sendButton.innerHTML;
        sendButton.disabled = true;
        sendButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Sending...';
        
        // Prepare email data
        const emailData = {
            to: to,
            subject: subject,
            message: message,
            case_id: currentCaseId,
            includeCaseDetails: includeDetails
        };
        
        // Send request
        const response = await fetch('/api/cases/send-response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(emailData)
        });
        
        const result = await response.json();
        
        // Reset button
        sendButton.disabled = false;
        sendButton.innerHTML = originalButtonText;
        
        if (result.status === 'success') {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('emailResponseModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('emailResponseForm').reset();
            
            // Show subtle success notification
            console.log('✅ Email sent successfully to', to);
            
            // Refresh threads and timeline
            loadCaseThreads(currentCaseId);
            loadCaseTimeline(currentCaseId);
        } else {
            // Show specific error message
            showError(result.message || 'Failed to send email response');
        }
    } catch (error) {
        console.error('Error sending email response:', error);
        showError('Network error. Please check your connection and try again.');
    }
}
```

#### Task 3.4: Add Email Validation (30 min)
**File**: `templates/cases.html`

Add client-side validation to email form:

```html
<!-- In emailResponseModal -->
<div class="mb-3">
    <label for="response-to" class="form-label">To</label>
    <input 
        type="email" 
        class="form-control" 
        id="response-to" 
        required 
        pattern="[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        title="Please enter a valid email address"
    >
    <div class="invalid-feedback">
        Please enter a valid email address
    </div>
</div>
```

### Acceptance Criteria
- ✅ Clear error messages for each failure type
- ✅ Loading spinner shows during send operation
- ✅ Email validation prevents invalid addresses
- ✅ Network errors show user-friendly message
- ✅ Auth errors direct user to contact admin
- ✅ All errors logged with context

---

## **PHASE 4: Timeline Integration** ⏱️ 1 hour
**Status**: 🟡 WAITING FOR PHASE 3  
**Priority**: 🟡 MEDIUM

### Goal
Ensure sent emails appear correctly in Timeline and Threads tabs.

### Tasks

#### Task 4.1: Enhance Timeline Display (30 min)
Update timeline rendering to show sent emails with icon and formatting.

**File**: `static/js/case-management.js`

```javascript
function renderTimelineEvent(event) {
    const iconMap = {
        'case_created': 'bi-plus-circle text-success',
        'status_changed': 'bi-arrow-repeat text-info',
        'email_response_sent': 'bi-envelope-check text-primary',
        'task_completed': 'bi-check-circle text-success',
        'note_added': 'bi-sticky text-warning'
    };
    
    const icon = iconMap[event.event_type] || 'bi-circle text-secondary';
    const preview = event.metadata?.preview || '';
    
    return `
        <div class="timeline-event mb-3 pb-3 border-bottom">
            <div class="d-flex">
                <div class="me-3">
                    <i class="bi ${icon} fs-4"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between">
                        <h6 class="mb-1">${event.description}</h6>
                        <small class="text-muted">${formatDate(event.timestamp)}</small>
                    </div>
                    <small class="text-muted">By ${event.actor}</small>
                    ${preview ? `<p class="mt-2 mb-0 text-muted small">${preview}...</p>` : ''}
                </div>
            </div>
        </div>
    `;
}
```

#### Task 4.2: Update Threads View (30 min)
Show sent responses differently from received emails.

**File**: `static/js/case-management.js`

```javascript
async function loadCaseThreads(caseId) {
    try {
        // Fetch tasks (received emails)
        const tasksResponse = await fetch(`/api/tasks`);
        const tasksResult = await tasksResponse.json();
        
        // Fetch timeline (sent emails)
        const timelineResponse = await fetch(`/api/cases/${caseId}/timeline`);
        const timelineResult = await timelineResponse.json();
        
        const container = document.getElementById('case-threads-list');
        
        if (tasksResult.status === 'success' && timelineResult.status === 'success') {
            const caseTasks = tasksResult.data.filter(task => task.case_id === caseId);
            const sentEmails = timelineResult.data.timeline.filter(e => e.event_type === 'email_response_sent');
            
            // Combine and sort by timestamp
            const allThreads = [
                ...caseTasks.map(t => ({ ...t, type: 'received', timestamp: t.created_at })),
                ...sentEmails.map(e => ({ ...e, type: 'sent', timestamp: e.timestamp }))
            ].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            
            if (allThreads.length > 0) {
                container.innerHTML = allThreads.map((item, index) => {
                    if (item.type === 'received') {
                        // Received email (from customer)
                        return `
                            <div class="border-start border-primary border-3 ps-3 mb-4">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <div>
                                        <h6 class="mb-1">
                                            <i class="bi bi-envelope text-primary"></i>
                                            ${item.subject || 'Email Communication'}
                                        </h6>
                                        <small class="text-muted">
                                            <i class="bi bi-person"></i> From: ${item.sender || 'Unknown'} 
                                            <span class="text-muted">&lt;${item.sender_email || ''}&gt;</span>
                                        </small>
                                    </div>
                                    <small class="text-muted">${formatDate(item.timestamp)}</small>
                                </div>
                                <div class="bg-light p-3 rounded">
                                    <p class="mb-0" style="white-space: pre-wrap;">${item.content || 'No content available'}</p>
                                </div>
                            </div>
                        `;
                    } else {
                        // Sent response (from portal)
                        return `
                            <div class="border-start border-success border-3 ps-3 mb-4 ms-5">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <div>
                                        <h6 class="mb-1">
                                            <i class="bi bi-envelope-check text-success"></i>
                                            ${item.metadata?.subject || 'Response Sent'}
                                        </h6>
                                        <small class="text-muted">
                                            <i class="bi bi-person-badge"></i> To: ${item.metadata?.recipient || 'Customer'}
                                        </small>
                                    </div>
                                    <small class="text-muted">${formatDate(item.timestamp)}</small>
                                </div>
                                <div class="bg-success bg-opacity-10 p-3 rounded">
                                    <p class="mb-0" style="white-space: pre-wrap;">${item.metadata?.preview || item.description}...</p>
                                </div>
                            </div>
                        `;
                    }
                }).join('');
            } else {
                container.innerHTML = `
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle"></i>
                        No communications found for this case yet.
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error loading threads:', error);
    }
}
```

### Acceptance Criteria
- ✅ Sent emails appear in Timeline tab with ✉️ icon
- ✅ Sent emails appear in Threads tab, aligned right
- ✅ Received emails aligned left, sent emails aligned right
- ✅ Visual distinction (color, icon) between sent/received
- ✅ Timeline refreshes automatically after sending

---

## **PHASE 5: Production Deployment** ⏱️ 30 minutes
**Status**: 🟡 WAITING FOR PHASE 4  
**Priority**: 🟢 LOW

### Goal
Deploy to production and monitor email sending.

### Tasks

#### Task 5.1: Pre-Deployment Checklist
- ✅ All previous phases complete
- ✅ Token file exists and valid
- ✅ Tested on 5+ cases
- ✅ Error handling working
- ✅ Timeline integration working
- ✅ Documentation updated

#### Task 5.2: Deployment
1. Backup current database: `cp data/cases.json data/cases_backup_$(date +%Y%m%d).json`
2. Restart app: `lsof -ti:5001 | xargs kill -9 && python app.py &`
3. Verify health: `curl http://localhost:5001/api/health`

#### Task 5.3: Post-Deployment Testing
1. Send 3 test emails to different customers
2. Verify all arrive successfully
3. Check timeline events persist
4. Monitor logs for errors

#### Task 5.4: Monitoring (First 24 hours)
- Monitor `logs/app.log` for email send errors
- Track success rate (should be >95%)
- Watch for token expiration issues
- Gather user feedback

### Acceptance Criteria
- ✅ Zero production errors in first hour
- ✅ Email delivery rate >95%
- ✅ Timeline events persist correctly
- ✅ Users can send emails without assistance

---

## 📊 SUCCESS METRICS

| Metric | Target | Current |
|--------|--------|---------|
| Email Delivery Rate | >95% | TBD |
| Average Send Time | <3 seconds | TBD |
| Error Rate | <5% | TBD |
| User Satisfaction | >80% | TBD |

---

## 🔧 QUICK TROUBLESHOOTING

### Error: "Failed to send email"
1. Check token exists: `ls ms_graph_token.json`
2. Run diagnostic: `python test_email_send.py`
3. Check logs: `tail -50 logs/app.log | grep send_email`

### Error: "Authentication failed"
1. Delete token: `rm ms_graph_token.json`
2. Restart app: `python app.py`
3. Re-authenticate via device code

### Email not received by customer
1. Check spam folder
2. Verify email address correct
3. Check Microsoft 365 admin center

---

## 📅 ESTIMATED TIMELINE

| Phase | Duration | Can Start |
|-------|----------|-----------|
| Phase 1: Authentication | 10 min | ✅ NOW |
| Phase 2: Test Sending | 5 min | After Phase 1 |
| Phase 3: Error Handling | 2 hours | After Phase 2 |
| Phase 4: Timeline | 1 hour | After Phase 3 |
| Phase 5: Production | 30 min | After Phase 4 |
| **TOTAL** | **4 hours** | |

---

## 🎯 IMMEDIATE NEXT STEP

**START PHASE 1 NOW** - Authentication (10 minutes)

Run these commands:

```bash
# 1. Kill background app
lsof -ti:5001 | xargs kill -9

# 2. Run app in foreground
cd /Users/tanujsaluja/HandyConnect
source venv/bin/activate
python app.py

# 3. Follow device code instructions in terminal
# 4. Open browser and authenticate
# 5. Wait for "Token saved" message
```

Once Phase 1 is complete, the "Send Response" button will work! 🎉

---

**Ready to start? Let me know and I'll guide you through Phase 1 step-by-step!**

