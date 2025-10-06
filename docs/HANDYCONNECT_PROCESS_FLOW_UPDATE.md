# HandyConnect Process Flow Update - Implementation Plan

**Date**: October 6, 2025  
**Type**: Major Operational Realignment  
**Estimated Time**: 3-4 hours  
**Status**: 🔵 PLANNING PHASE

---

## 🎯 **OBJECTIVE**

Realign HandyConnect to a **Case-Centric Model** where:
- Cases are the primary entity (created from inbound emails)
- Threads are embedded within cases (not standalone)
- Tasks are assigned to internal team OR external contractors
- All communications logged to case threads
- AI summaries regenerate based on full case context

---

## 📊 **CURRENT vs NEW ARCHITECTURE**

### **CURRENT (As-Is)**:
```
Email → Task → Case (loosely linked)
Threads → Standalone page (in-memory, lost on restart)
Tasks → Limited assignment (no contractor workflow)
```

### **NEW (To-Be)**:
```
Email → Case → Threads (embedded) + Tasks (assigned)
                ↓
         AI Summary (regenerated)
                ↓
         Acknowledgment Email → Logged to Threads
                ↓
         Task Assignment → Email to Contractor → Logged to Threads
```

---

## 🗂️ **NEW DATA MODEL**

### **Case Structure**:
```json
{
  "case_id": "uuid",
  "case_number": "2510060001",
  "case_title": "Door jamming issue",
  "customer_info": {...},
  "status": "New",
  "priority": "High",
  "threads": [
    {
      "thread_id": "uuid",
      "timestamp": "2025-10-06T...",
      "direction": "Inbound",
      "sender_name": "Customer Name",
      "sender_email": "customer@email.com",
      "subject": "Help with door",
      "body": "Full email content...",
      "message_id": "email-123"
    },
    {
      "thread_id": "uuid",
      "timestamp": "2025-10-06T...",
      "direction": "Outbound",
      "sender_name": "HandyConnect Support",
      "sender_email": "handymyjob@outlook.com",
      "subject": "Re: Help with door",
      "body": "Thank you for contacting...",
      "message_id": "email-456"
    }
  ],
  "tasks": ["task-1", "task-2"],
  "ai_summary": "Generated summary...",
  "created_at": "...",
  "updated_at": "..."
}
```

### **Task Structure**:
```json
{
  "id": 1,
  "case_id": "uuid",
  "subject": "Fix bathroom door",
  "description": "Inspect and repair jammed door",
  "status": "New",
  "assigned_to": "John Smith",
  "assigned_email": "john@plumbingpro.com",
  "assigned_role": "External",
  "created_at": "...",
  "due_date": "...",
  "completed_at": null
}
```

---

## 📋 **IMPLEMENTATION PHASES**

---

## **PHASE 1: Data Model Updates** (30 minutes)

### **1.1: Update Case Service to Handle Threads**

**File**: `features/core_services/case_service.py`

**Changes**:
```python
def add_thread_to_case(self, case_id: str, thread_data: dict) -> bool:
    """
    Add a communication thread entry to a case
    
    Args:
        case_id: Case UUID
        thread_data: {
            'direction': 'Inbound' | 'Outbound',
            'sender_name': str,
            'sender_email': str,
            'subject': str,
            'body': str,
            'timestamp': ISO datetime,
            'message_id': str (optional)
        }
    """
    try:
        cases = self.load_cases()
        case = next((c for c in cases if c['case_id'] == case_id), None)
        
        if not case:
            return False
        
        if 'threads' not in case:
            case['threads'] = []
        
        thread_entry = {
            'thread_id': str(uuid.uuid4()),
            'timestamp': thread_data.get('timestamp', datetime.utcnow().isoformat()),
            'direction': thread_data['direction'],
            'sender_name': thread_data['sender_name'],
            'sender_email': thread_data['sender_email'],
            'subject': thread_data['subject'],
            'body': thread_data['body'],
            'message_id': thread_data.get('message_id', '')
        }
        
        case['threads'].append(thread_entry)
        case['updated_at'] = datetime.utcnow().isoformat()
        
        self.save_cases(cases)
        logger.info(f"Added {thread_data['direction']} thread to case {case.get('case_number')}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding thread to case: {e}")
        return False
```

### **1.2: Update Task Service for Assignment**

**File**: `features/core_services/task_service.py`

**Changes**:
```python
def assign_task(self, task_id: int, assignee_name: str, 
                assignee_email: str, assignee_role: str) -> dict:
    """
    Assign a task to internal team or external contractor
    
    Args:
        task_id: Task ID
        assignee_name: Full name of assignee
        assignee_email: Email address
        assignee_role: "Internal" or "External"
    
    Returns:
        Updated task dict or None
    """
    try:
        tasks = self.load_tasks()
        task = next((t for t in tasks if t['id'] == task_id), None)
        
        if not task:
            return None
        
        task['assigned_to'] = assignee_name
        task['assigned_email'] = assignee_email
        task['assigned_role'] = assignee_role
        task['status'] = 'Assigned'
        task['assigned_at'] = datetime.utcnow().isoformat()
        task['updated_at'] = datetime.utcnow().isoformat()
        
        self.save_tasks(tasks)
        logger.info(f"Assigned task {task_id} to {assignee_name} ({assignee_role})")
        
        return task
        
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        return None
```

---

## **PHASE 2: Email Worker Refactoring** (45 minutes)

### **2.1: Update Email Processing to Log Threads**

**File**: `app.py`

**Changes to `email_polling_worker()`**:
```python
# When new email arrives:
1. Check if it's a reply (thread_id exists) or new email
2. If new email:
   - Create new case
   - Add inbound email to case threads
   - Generate AI summary
   - Send acknowledgment email
   - Log acknowledgment to case threads
3. If reply:
   - Find existing case by thread_id or customer email
   - Add inbound email to case threads
   - Regenerate AI summary
```

### **2.2: Log Acknowledgment Emails to Threads**

**File**: `features/core_services/acknowledgment_service.py`

**Enhancement**:
```python
def send_acknowledgment(self, case_id: str, customer_email: str, ...):
    # ... existing code ...
    
    # After sending email successfully
    if email_sent:
        # Log to case threads
        thread_data = {
            'direction': 'Outbound',
            'sender_name': 'HandyConnect Support',
            'sender_email': 'handymyjob@outlook.com',
            'subject': subject,
            'body': body,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        case_service.add_thread_to_case(case_id, thread_data)
```

---

## **PHASE 3: UI Refactoring** (60 minutes)

### **3.1: Remove Threads Page**

**Files to Modify**:
- `templates/base.html` - Remove "Threads" nav link
- `app.py` - Remove `/threads` route
- `templates/threads.html` - Can be deleted or archived
- `static/js/thread-management.js` - Can be deleted or archived

### **3.2: Add Communication Tab to Case Detail Modal**

**File**: `templates/cases.html`

**Changes**:
```html
<!-- Update tabs -->
<ul class="nav nav-tabs" id="caseDetailTabs">
    <li class="nav-item">
        <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#summary">
            <i class="bi bi-file-text"></i> Summary
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tasks">
            <i class="bi bi-list-check"></i> Tasks
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#communication">
            <i class="bi bi-chat-dots"></i> Communication
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#timeline">
            <i class="bi bi-clock-history"></i> Timeline
        </button>
    </li>
</ul>

<!-- Communication Tab Content -->
<div class="tab-pane fade" id="communication">
    <div class="card mt-3">
        <div class="card-header">
            <h6 class="mb-0">Email Communication History</h6>
        </div>
        <div class="card-body">
            <div id="case-communication-list">
                <!-- Populated by JavaScript -->
            </div>
        </div>
    </div>
</div>
```

### **3.3: JavaScript for Communication Tab**

**File**: `static/js/case-management.js`

**New Function**:
```javascript
async function loadCaseCommunication(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const caseData = result.data.case;
            const threads = caseData.threads || [];
            
            const container = document.getElementById('case-communication-list');
            
            if (threads.length === 0) {
                container.innerHTML = `
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle"></i>
                        No communication history yet.
                    </div>
                `;
                return;
            }
            
            // Sort by timestamp descending (newest first)
            threads.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            
            container.innerHTML = threads.map(thread => {
                const isInbound = thread.direction === 'Inbound';
                const badgeClass = isInbound ? 'bg-primary' : 'bg-success';
                const borderClass = isInbound ? 'border-primary' : 'border-success';
                const alignClass = isInbound ? '' : 'ms-4';
                
                return `
                    <div class="border-start ${borderClass} border-3 ps-3 mb-4 ${alignClass}">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <h6 class="mb-1">
                                    <span class="badge ${badgeClass}">${thread.direction}</span>
                                    ${thread.subject}
                                </h6>
                                <small class="text-muted">
                                    <i class="bi bi-person"></i> ${thread.sender_name}
                                    &lt;${thread.sender_email}&gt;
                                </small>
                            </div>
                            <small class="text-muted">${formatDate(thread.timestamp)}</small>
                        </div>
                        <div class="bg-light p-3 rounded">
                            <p class="mb-0 email-body-preview" 
                               id="thread-${thread.thread_id}" 
                               style="white-space: pre-wrap; max-height: 100px; overflow: hidden;">
                                ${thread.body}
                            </p>
                            <button class="btn btn-sm btn-link p-0 mt-2" 
                                    onclick="toggleThreadExpand('${thread.thread_id}')">
                                <i class="bi bi-chevron-down"></i> Show more
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading communication:', error);
    }
}

function toggleThreadExpand(threadId) {
    const element = document.getElementById(`thread-${threadId}`);
    const button = element.nextElementSibling;
    
    if (element.style.maxHeight === 'none') {
        element.style.maxHeight = '100px';
        button.innerHTML = '<i class="bi bi-chevron-down"></i> Show more';
    } else {
        element.style.maxHeight = 'none';
        button.innerHTML = '<i class="bi bi-chevron-up"></i> Show less';
    }
}
```

---

## **PHASE 4: Task Assignment Feature** (90 minutes)

### **4.1: Create Assignment Notification Service**

**File**: `features/core_services/task_assignment_service.py` (NEW)

```python
"""
Task Assignment Service
Handles assignment of tasks to internal team or external contractors
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from .email_service import EmailService
from .case_service import CaseService
from .task_service import TaskService

logger = logging.getLogger(__name__)

class TaskAssignmentService:
    def __init__(self):
        self.email_service = EmailService()
        self.case_service = CaseService()
        self.task_service = TaskService()
    
    def assign_and_notify(self, task_id: int, assignee_name: str, 
                         assignee_email: str, assignee_role: str,
                         case_id: str) -> bool:
        """
        Assign task and send notification email
        
        Returns:
            bool: True if assignment and notification successful
        """
        try:
            # Assign the task
            task = self.task_service.assign_task(
                task_id, assignee_name, assignee_email, assignee_role
            )
            
            if not task:
                logger.error(f"Failed to assign task {task_id}")
                return False
            
            # Get case details
            case = self.case_service.get_case_by_id(case_id)
            if not case:
                logger.error(f"Case not found: {case_id}")
                return False
            
            # Build assignment email
            subject, body = self._build_assignment_email(task, case)
            
            # Send email to assignee
            email_sent = self.email_service.send_email_response(
                case_id=case_id,
                response_text=body,
                recipient_email=assignee_email,
                subject=subject,
                include_case_details=False
            )
            
            if email_sent:
                # Log email to case threads
                thread_data = {
                    'direction': 'Outbound',
                    'sender_name': 'HandyConnect System',
                    'sender_email': 'handymyjob@outlook.com',
                    'subject': subject,
                    'body': body,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                self.case_service.add_thread_to_case(case_id, thread_data)
                
                logger.info(f"✉️ Task assignment notification sent to {assignee_name}")
                return True
            else:
                logger.error(f"Failed to send assignment email to {assignee_email}")
                return False
                
        except Exception as e:
            logger.error(f"Error in assign_and_notify: {e}")
            return False
    
    def _build_assignment_email(self, task: Dict, case: Dict) -> tuple:
        """Build assignment email subject and body"""
        
        customer_info = case.get('customer_info', {})
        property_ref = f"Property {customer_info.get('property_number', 'N/A')}, Block {customer_info.get('block_number', 'N/A')}"
        
        priority_emoji = {
            'Urgent': '🔴',
            'High': '🟠',
            'Medium': '🟡',
            'Low': '🟢'
        }.get(case.get('priority', 'Medium'), '🟡')
        
        subject = f"Task Assignment - Case #{case.get('case_number')} - {task.get('subject', 'New Task')}"
        
        body = f"""
Dear {task.get('assigned_to', 'Team Member')},

You have been assigned a new task by HandyConnect Property Management.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 TASK ASSIGNMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{priority_emoji} Priority: {case.get('priority', 'Medium')}
📝 Task: {task.get('subject', 'Task Assignment')}

Description:
{task.get('description', task.get('content', 'No description provided'))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏠 PROPERTY DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Case Number: {case.get('case_number', 'N/A')}
{property_ref}
Property Address: {customer_info.get('property_address', 'N/A')}

Customer: {customer_info.get('name', 'N/A')}
Contact: {customer_info.get('email', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Review the task details above
2. Contact the customer if needed
3. Complete the assigned work
4. Reply to this email when task is completed

If you have questions, reply to this email or contact our support team.

Thank you,
HandyConnect Property Management Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Case ID: {case_id} | Task ID: {task.get('id')}
This is an automated notification from HandyConnect.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return subject, body
```

---

## **PHASE 5: Frontend Updates** (60 minutes)

### **5.1: Remove Threads from Navigation**

**File**: `templates/base.html`

**Find and remove**:
```html
<!-- REMOVE THIS -->
<li class="nav-item">
    <a class="nav-link" href="/threads">
        <i class="bi bi-chat-dots"></i> Threads
    </a>
</li>
```

### **5.2: Update Case Detail Modal Tabs**

**File**: `templates/cases.html`

**Replace current tabs with**:
```html
<ul class="nav nav-tabs" id="caseDetailTabs">
    <li class="nav-item">
        <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#summary">
            <i class="bi bi-file-text"></i> Summary
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tasks">
            <i class="bi bi-list-check"></i> Tasks
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#communication">
            <i class="bi bi-envelope"></i> Communication
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#timeline">
            <i class="bi bi-clock-history"></i> Timeline
        </button>
    </li>
</ul>
```

### **5.3: Add Task Assignment UI**

**File**: `templates/cases.html`

**In Tasks tab, add assignment button**:
```html
<div class="d-flex justify-content-between align-items-center mb-3">
    <h6 class="card-title mb-0">Linked Tasks</h6>
    <button class="btn btn-sm btn-primary" onclick="showAssignTaskModal()">
        <i class="bi bi-person-plus"></i> Assign Task
    </button>
</div>
```

**Add Assignment Modal**:
```html
<div class="modal fade" id="assignTaskModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Assign Task</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="mb-3">
                    <label class="form-label">Assign To</label>
                    <input type="text" class="form-control" id="assign-name" placeholder="Name">
                </div>
                <div class="mb-3">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" id="assign-email" placeholder="email@example.com">
                </div>
                <div class="mb-3">
                    <label class="form-label">Role</label>
                    <select class="form-select" id="assign-role">
                        <option value="Internal">Internal Team</option>
                        <option value="External">External Contractor</option>
                    </select>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="submitTaskAssignment()">
                    Assign & Notify
                </button>
            </div>
        </div>
    </div>
</div>
```

---

## **PHASE 6: Testing & Validation** (30 minutes)

### **End-to-End Test Scenarios**:

1. **New Email → Case Creation**:
   - Send email to `handymyjob@outlook.com`
   - Verify case created
   - Verify inbound email in Communication tab
   - Verify acknowledgment email sent
   - Verify acknowledgment logged in Communication tab

2. **Task Assignment**:
   - Open case
   - Assign task to contractor
   - Verify email sent to contractor
   - Verify assignment logged in Communication tab
   - Verify Timeline shows assignment event

3. **AI Summary Regeneration**:
   - Open case
   - Verify summary includes threads and tasks
   - Send new email
   - Verify summary updates

---

## 📅 **IMPLEMENTATION TIMELINE**

| Phase | Duration | Description |
|-------|----------|-------------|
| Phase 1 | 30 min | Data model updates |
| Phase 2 | 45 min | Email worker refactoring |
| Phase 3 | 60 min | UI refactoring |
| Phase 4 | 90 min | Task assignment feature |
| Phase 5 | 30 min | Testing & validation |
| **TOTAL** | **4 hours** | Complete refactoring |

---

## ✅ **DELIVERABLES**

1. ✅ Cases contain embedded threads (not standalone)
2. ✅ Communication tab in Case Detail modal
3. ✅ Task assignment with email notifications
4. ✅ All emails logged to case threads
5. ✅ AI summaries use full case context
6. ✅ Threads page/menu removed
7. ✅ Clean data model
8. ✅ End-to-end tested

---

## 🎯 **ACCEPTANCE CRITERIA**

- [ ] New email creates case with inbound thread entry
- [ ] Acknowledgment email logged to threads
- [ ] Communication tab shows all emails (inbound/outbound)
- [ ] Can expand/collapse thread messages
- [ ] Task assignment sends email and logs to threads
- [ ] AI summary includes thread context
- [ ] Threads menu option removed
- [ ] All data persists to JSON files
- [ ] No console errors
- [ ] Performance acceptable

---

## 🚀 **READY TO START?**

This is a major refactoring that will significantly improve the operational flow.

**Benefits**:
- ✅ Clear case-centric model
- ✅ All communications in one place
- ✅ Contractor assignment workflow
- ✅ Better AI summaries (full context)
- ✅ Cleaner UI (removed standalone Threads page)

**Would you like me to proceed with Phase 1?**

Let me know and I'll start implementing! 🎉

