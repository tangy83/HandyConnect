# User-Critical Features: Validation & Implementation Plan

## 🎯 User Requirements

### **Feature 1: AI-Powered Email Summary at Case Level**
**User Story**: "As a case manager, I want to see an AI summary of the email thread at a glance so I can quickly understand the problem without reading the entire conversation."

**Requirements:**
- View case and see topline AI summary of the issue
- Summary should be at the case level (not buried in details)
- Must be generated using LLM
- Should update when new emails arrive
- Must be visible in both Cases list and Case detail view

---

### **Feature 2: Task Assignment to Third Parties**
**User Story**: "As a case manager, I want to assign tasks to third-party contractors (plumbers, electricians) and have them automatically notified via email."

**Requirements:**
- Assign a task to a specific person/contractor
- Task must be linked to a case
- Automated email notification sent to assignee
- Email includes case context and task details
- Track assignment status

---

## 📊 PHASE 1: FEATURE DISCOVERY & VALIDATION (30 minutes)

### Goal
Determine what's already built and what needs to be created.

---

### **1.1: Check AI Summary Feature**

#### What to Check:
1. ✅ Does `LLMService` have a summary generation method?
2. ✅ Is summary displayed in Cases list?
3. ✅ Is summary displayed in Case detail modal?
4. ✅ Does summary update with new emails?
5. ✅ Is summary visible "at a glance"?

#### Commands to Run:
```bash
# Check if AI summary method exists
grep -r "generate_case_summary\|generate_summary" features/core_services/llm_service.py

# Check if summary is displayed in UI
grep -r "ai-summary\|case-summary" templates/cases.html static/js/case-management.js

# Check if summary is in case list
grep -r "summary" static/js/case-management.js | grep -i "render"
```

#### Expected Findings:
- ✅ **FOUND**: `generate_case_summary()` method exists in `LLMService`
- ✅ **FOUND**: `case-ai-summary` element in case detail modal
- ✅ **FOUND**: `loadCaseSummary()` function in JavaScript
- ❌ **MISSING**: Summary NOT in Cases list (only in detail modal)
- ❌ **MISSING**: Summary not "at a glance" - requires clicking case

#### Status:
🟡 **PARTIALLY BUILT** - Summary exists but hidden, needs UI improvements

---

### **1.2: Check Task Assignment Feature**

#### What to Check:
1. ❌ Can tasks be assigned to specific people?
2. ❌ Does task assignment send email notification?
3. ❌ Can we assign to third-party contractors?
4. ❌ Is there an "Assigned To" field in tasks?
5. ❌ Is there a contractor/user management system?

#### Commands to Run:
```bash
# Check for assignment fields
grep -r "assigned_to\|assignee" features/core_services/task_service.py data/tasks.json

# Check for email notification on assignment
grep -r "assign.*email\|notify.*assign" features/

# Check for contractor management
grep -r "contractor\|third.party" features/
```

#### Expected Findings:
- ✅ **FOUND**: `assigned_to` field exists in task model
- ❌ **MISSING**: No email notification on assignment
- ❌ **MISSING**: No contractor management system
- ❌ **MISSING**: No UI to assign tasks
- ❌ **MISSING**: No email template for assignments

#### Status:
🔴 **NOT BUILT** - Basic field exists but feature incomplete

---

## 📋 PHASE 2: FEATURE 1 - AI SUMMARY ENHANCEMENTS (2 hours)

### Goal
Make AI summary visible "at a glance" without clicking into case details.

---

### **2.1: Add Summary to Cases List (30 min)**

#### Changes Required:

**File: `static/js/case-management.js`**
```javascript
// In renderCases function, add summary preview column
function renderCases(casesToRender) {
    // ... existing code ...
    
    // Add new column for AI summary preview
    <td class="col-summary">
        <div class="summary-preview">
            ${caseItem.ai_summary_preview || 'Loading summary...'}
        </div>
    </td>
}
```

**File: `templates/cases.html`**
```html
<!-- Add summary column header -->
<th class="col-summary">Issue Summary</th>

<!-- In table body -->
<td class="col-summary">
    <div class="summary-preview text-muted small">
        <i class="bi bi-robot me-1"></i>
        <span id="summary-${case.case_id}">Loading...</span>
    </div>
</td>
```

**File: `features/core_services/case_service.py`**
```python
def get_all_cases_with_summaries(self):
    """Get all cases with AI summaries pre-loaded"""
    cases = self.load_cases()
    
    for case in cases:
        # Generate short summary preview (first 100 chars)
        full_summary = self.generate_case_summary(case['case_id'])
        case['ai_summary_preview'] = full_summary[:100] + '...'
        case['ai_summary_full'] = full_summary
    
    return cases
```

#### Acceptance Criteria:
- ✅ Cases list shows AI summary preview (100 chars)
- ✅ Summary loads asynchronously to avoid slow page load
- ✅ Summary updates when case is updated
- ✅ Clicking case shows full summary in detail modal

---

### **2.2: Improve Summary Display in Detail Modal (30 min)**

#### Changes Required:

**File: `templates/cases.html`**
```html
<!-- Make AI summary more prominent -->
<div class="card bg-light mb-3">
    <div class="card-body">
        <div class="d-flex align-items-start">
            <div class="flex-shrink-0">
                <i class="bi bi-robot fs-2 text-primary"></i>
            </div>
            <div class="flex-grow-1 ms-3">
                <h5 class="card-title mb-2">
                    🤖 AI Summary
                    <span class="badge bg-success ms-2">Auto-Generated</span>
                </h5>
                <div id="case-ai-summary" class="lead">
                    Loading intelligent summary...
                </div>
                <div class="mt-3">
                    <strong>Key Points:</strong>
                    <ul id="case-key-points" class="mb-0">
                        <!-- Populated by JavaScript -->
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
```

**File: `features/core_services/llm_service.py`**
```python
def generate_case_summary(self, case_id: str, email_content: str = None) -> dict:
    """
    Generate comprehensive case summary with key points
    
    Returns:
        {
            'summary': 'Full summary text',
            'key_points': ['Point 1', 'Point 2', 'Point 3'],
            'urgency': 'high|medium|low',
            'sentiment': 'positive|neutral|negative'
        }
    """
    # ... existing code ...
    
    prompt = f"""
    Analyze this customer case and provide:
    
    1. A 2-3 sentence summary of the main issue
    2. 3-5 key actionable points
    3. Urgency level (critical/high/medium/low)
    4. Customer sentiment
    
    Case Details:
    {case_context}
    
    Format as JSON:
    {{
        "summary": "Brief overview",
        "key_points": ["Point 1", "Point 2", "Point 3"],
        "urgency": "medium",
        "sentiment": "frustrated"
    }}
    """
```

#### Acceptance Criteria:
- ✅ AI summary is prominent and easy to read
- ✅ Key points displayed as bullet list
- ✅ Urgency and sentiment badges visible
- ✅ Summary refreshes when new emails arrive

---

### **2.3: Real-Time Summary Updates (30 min)**

#### Changes Required:

**File: `app.py` (Email Polling Worker)**
```python
def email_polling_worker():
    while True:
        # ... existing email processing ...
        
        # After creating/updating case from email
        if case_id:
            # Regenerate AI summary
            case_service.regenerate_case_summary(case_id)
            logger.info(f"Updated AI summary for case {case_id}")
```

**File: `features/core_services/case_service.py`**
```python
def regenerate_case_summary(self, case_id: str):
    """Regenerate AI summary for a case (called when new emails arrive)"""
    case = self.get_case_by_id(case_id)
    if not case:
        return
    
    # Get latest email content
    tasks = self.task_service.get_tasks_by_case(case_id)
    email_content = '\n\n'.join([t.get('content', '') for t in tasks[-3:]])
    
    # Generate new summary
    summary_data = self.llm_service.generate_case_summary(case_id, email_content)
    
    # Update case
    case['ai_summary'] = summary_data
    case['ai_summary_preview'] = summary_data['summary'][:100] + '...'
    case['updated_at'] = datetime.utcnow().isoformat()
    
    self.save_cases([case])
    logger.info(f"Regenerated AI summary for case {case_id}")
```

#### Acceptance Criteria:
- ✅ Summary updates when new email arrives
- ✅ Summary cached to avoid regenerating on every page load
- ✅ Summary regeneration happens in background
- ✅ UI shows "Updated X minutes ago" timestamp

---

### **2.4: Testing & Validation (30 min)**

#### Test Cases:
1. Open Cases page → See AI summary preview in list
2. Click case → See full AI summary prominently displayed
3. Send new email to case → Summary updates automatically
4. Summary includes key points, urgency, sentiment
5. Summary is readable and accurate

---

## 📋 PHASE 3: FEATURE 2 - TASK ASSIGNMENT SYSTEM (4 hours)

### Goal
Build complete task assignment workflow with email notifications.

---

### **3.1: Contractor/User Management (1 hour)**

#### Create Contractor Database

**File: `data/contractors.json`** (NEW)
```json
[
  {
    "id": "contractor-001",
    "name": "John's Plumbing Services",
    "email": "john@plumbingservices.com",
    "phone": "+1-555-0123",
    "specialty": "Plumbing",
    "active": true,
    "created_at": "2025-10-01T00:00:00"
  },
  {
    "id": "contractor-002",
    "name": "Electric Pro Solutions",
    "email": "info@electricpro.com",
    "phone": "+1-555-0456",
    "specialty": "Electrical",
    "active": true,
    "created_at": "2025-10-01T00:00:00"
  }
]
```

**File: `features/core_services/contractor_service.py`** (NEW)
```python
"""
Contractor Management Service
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ContractorService:
    def __init__(self):
        self.contractors_file = 'data/contractors.json'
        self.ensure_contractors_file()
    
    def ensure_contractors_file(self):
        """Ensure contractors file exists"""
        if not os.path.exists(self.contractors_file):
            os.makedirs(os.path.dirname(self.contractors_file), exist_ok=True)
            with open(self.contractors_file, 'w') as f:
                json.dump([], f)
    
    def load_contractors(self) -> List[Dict]:
        """Load all contractors"""
        try:
            with open(self.contractors_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading contractors: {e}")
            return []
    
    def get_active_contractors(self) -> List[Dict]:
        """Get all active contractors"""
        contractors = self.load_contractors()
        return [c for c in contractors if c.get('active', True)]
    
    def get_contractor_by_id(self, contractor_id: str) -> Optional[Dict]:
        """Get contractor by ID"""
        contractors = self.load_contractors()
        return next((c for c in contractors if c['id'] == contractor_id), None)
    
    def get_contractors_by_specialty(self, specialty: str) -> List[Dict]:
        """Get contractors filtered by specialty"""
        contractors = self.get_active_contractors()
        return [c for c in contractors if c.get('specialty', '').lower() == specialty.lower()]
    
    def add_contractor(self, name: str, email: str, specialty: str, phone: str = None) -> Dict:
        """Add a new contractor"""
        contractors = self.load_contractors()
        
        contractor_id = f"contractor-{len(contractors) + 1:03d}"
        
        new_contractor = {
            'id': contractor_id,
            'name': name,
            'email': email,
            'phone': phone,
            'specialty': specialty,
            'active': True,
            'created_at': datetime.utcnow().isoformat()
        }
        
        contractors.append(new_contractor)
        self.save_contractors(contractors)
        
        logger.info(f"Added contractor: {name} ({contractor_id})")
        return new_contractor
    
    def save_contractors(self, contractors: List[Dict]):
        """Save contractors to file"""
        try:
            with open(self.contractors_file, 'w') as f:
                json.dump(contractors, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving contractors: {e}")
```

#### Acceptance Criteria:
- ✅ Contractors can be added/viewed/updated
- ✅ Contractors have email, phone, specialty
- ✅ Can filter contractors by specialty
- ✅ Simple management UI (admin only)

---

### **3.2: Task Assignment UI (1 hour)**

#### Add Assignment to Case Detail Modal

**File: `templates/cases.html`**
```html
<!-- In Tasks Tab -->
<div class="card mt-3">
    <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="card-title mb-0">Linked Tasks</h6>
            <button class="btn btn-sm btn-primary" onclick="showAssignTaskModal()">
                <i class="bi bi-person-plus"></i> Assign Task
            </button>
        </div>
        
        <!-- Task list with assignment status -->
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Task</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Assigned To</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="case-tasks-tbody">
                <!-- Populated by JavaScript -->
            </tbody>
        </table>
    </div>
</div>

<!-- Assign Task Modal -->
<div class="modal fade" id="assignTaskModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="bi bi-person-plus"></i> Assign Task to Contractor
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="assignTaskForm">
                    <div class="mb-3">
                        <label for="assign-task-title" class="form-label">Task Title</label>
                        <input type="text" class="form-control" id="assign-task-title" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="assign-task-description" class="form-label">Description</label>
                        <textarea class="form-control" id="assign-task-description" rows="3" required></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="assign-task-specialty" class="form-label">Required Specialty</label>
                        <select class="form-select" id="assign-task-specialty" onchange="filterContractorsBySpecialty()">
                            <option value="">-- Select Specialty --</option>
                            <option value="Plumbing">Plumbing</option>
                            <option value="Electrical">Electrical</option>
                            <option value="HVAC">HVAC</option>
                            <option value="Carpentry">Carpentry</option>
                            <option value="General Maintenance">General Maintenance</option>
                        </select>
                    </div>
                    
                    <div class="mb-3">
                        <label for="assign-contractor" class="form-label">Assign To</label>
                        <select class="form-select" id="assign-contractor" required>
                            <option value="">-- Select Contractor --</option>
                            <!-- Populated by JavaScript -->
                        </select>
                    </div>
                    
                    <div class="mb-3">
                        <label for="assign-task-priority" class="form-label">Priority</label>
                        <select class="form-select" id="assign-task-priority">
                            <option value="Low">Low</option>
                            <option value="Medium" selected>Medium</option>
                            <option value="High">High</option>
                            <option value="Urgent">Urgent</option>
                        </select>
                    </div>
                    
                    <div class="mb-3 form-check">
                        <input type="checkbox" class="form-check-input" id="assign-send-email" checked>
                        <label class="form-check-label" for="assign-send-email">
                            Send email notification to contractor
                        </label>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="submitTaskAssignment()">
                    <i class="bi bi-check-circle"></i> Assign Task
                </button>
            </div>
        </div>
    </div>
</div>
```

#### Acceptance Criteria:
- ✅ Can create and assign task in one step
- ✅ Contractors filtered by specialty
- ✅ Can choose to send email notification
- ✅ Task linked to current case

---

### **3.3: Email Notification Service for Assignments (1 hour)**

**File: `features/core_services/assignment_notification_service.py`** (NEW)
```python
"""
Assignment Notification Service
Sends email notifications when tasks are assigned to contractors
"""

import logging
from typing import Dict, Optional
from .email_service import EmailService
from .case_service import CaseService
from .contractor_service import ContractorService

logger = logging.getLogger(__name__)

class AssignmentNotificationService:
    def __init__(self):
        self.email_service = EmailService()
        self.case_service = CaseService()
        self.contractor_service = ContractorService()
    
    def send_assignment_notification(self, task: Dict, case_id: str, contractor_id: str) -> bool:
        """
        Send email notification to contractor about new task assignment
        
        Args:
            task: Task dictionary with id, title, description, priority
            case_id: ID of the case this task belongs to
            contractor_id: ID of the contractor being assigned
        
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Get contractor details
            contractor = self.contractor_service.get_contractor_by_id(contractor_id)
            if not contractor:
                logger.error(f"Contractor not found: {contractor_id}")
                return False
            
            # Get case details
            case = self.case_service.get_case_by_id(case_id)
            if not case:
                logger.error(f"Case not found: {case_id}")
                return False
            
            # Build email content
            subject = f"New Task Assignment - Case #{case.get('case_number')} - {task.get('title')}"
            
            body = self._build_assignment_email(task, case, contractor)
            
            # Send email via Microsoft Graph API
            email_sent = self.email_service.send_email_response(
                case_id=case_id,
                response_text=body,
                recipient_email=contractor['email'],
                subject=subject,
                include_case_details=False  # We're including custom details
            )
            
            if email_sent:
                logger.info(f"✉️ Assignment notification sent to {contractor['name']} ({contractor['email']})")
                return True
            else:
                logger.error(f"Failed to send assignment notification to {contractor['email']}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending assignment notification: {e}")
            return False
    
    def _build_assignment_email(self, task: Dict, case: Dict, contractor: Dict) -> str:
        """Build assignment email body"""
        customer_info = case.get('customer_info', {})
        
        priority_emoji = {
            'Urgent': '🔴',
            'High': '🟠',
            'Medium': '🟡',
            'Low': '🟢'
        }.get(task.get('priority', 'Medium'), '🟡')
        
        email_body = f"""
Dear {contractor['name']},

You have been assigned a new task by HandyConnect Property Management.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 TASK ASSIGNMENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{priority_emoji} Priority: {task.get('priority', 'Medium')}
📝 Task: {task.get('title', 'Task Assignment')}

Description:
{task.get('description', 'No description provided')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏠 PROPERTY DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Case Number: {case.get('case_number', 'N/A')}
Property Number: {customer_info.get('property_number', 'N/A')}
Block Number: {customer_info.get('block_number', 'N/A')}
Property Address: {customer_info.get('property_address', 'N/A')}

Customer: {customer_info.get('name', 'N/A')}
Contact: {customer_info.get('email', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Review the task details above
2. Contact the customer if needed: {customer_info.get('email', 'N/A')}
3. Schedule the work at your earliest convenience
4. Reply to this email with your estimated completion time
5. Update us when the task is completed

If you have any questions or need additional information, please reply to this email or contact our support team.

Thank you for your prompt attention to this matter.

Best regards,
HandyConnect Property Management Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated notification from HandyConnect Case Management System.
Case ID: {case_id} | Task ID: {task.get('id', 'N/A')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return email_body
```

#### Acceptance Criteria:
- ✅ Email sent FROM `handymyjob@outlook.com`
- ✅ Email sent TO contractor's email
- ✅ Email includes task details, case context, property info
- ✅ Email is professional and clear
- ✅ Email logged in case timeline

---

### **3.4: API Endpoints & JavaScript (1 hour)**

**File: `features/case_management/task_assignment_api.py`** (NEW)
```python
"""
Task Assignment API Blueprint
"""

from flask import Blueprint, request, jsonify
import logging
from ..core_services.task_service import TaskService
from ..core_services.contractor_service import ContractorService
from ..core_services.assignment_notification_service import AssignmentNotificationService

logger = logging.getLogger(__name__)

assignment_bp = Blueprint('assignment_api', __name__, url_prefix='/api/assignments')

task_service = TaskService()
contractor_service = ContractorService()
notification_service = AssignmentNotificationService()

@assignment_bp.route('/contractors', methods=['GET'])
def get_contractors():
    """Get all active contractors"""
    try:
        specialty = request.args.get('specialty')
        
        if specialty:
            contractors = contractor_service.get_contractors_by_specialty(specialty)
        else:
            contractors = contractor_service.get_active_contractors()
        
        return jsonify({
            'status': 'success',
            'data': contractors
        })
    except Exception as e:
        logger.error(f"Error getting contractors: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@assignment_bp.route('/assign-task', methods=['POST'])
def assign_task():
    """Assign a task to a contractor"""
    try:
        data = request.get_json()
        
        required_fields = ['case_id', 'contractor_id', 'title', 'description', 'priority']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400
        
        # Create task
        task = task_service.create_task(
            subject=data['title'],
            content=data['description'],
            case_id=data['case_id'],
            priority=data['priority'],
            assigned_to=data['contractor_id'],
            status='Assigned'
        )
        
        # Send email notification if requested
        email_sent = False
        if data.get('send_email', True):
            email_sent = notification_service.send_assignment_notification(
                task=task,
                case_id=data['case_id'],
                contractor_id=data['contractor_id']
            )
        
        return jsonify({
            'status': 'success',
            'data': {
                'task': task,
                'email_sent': email_sent
            },
            'message': 'Task assigned successfully'
        })
        
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
```

**File: `static/js/case-management.js`**
```javascript
// Load contractors and populate dropdown
async function loadContractors(specialty = null) {
    try {
        let url = '/api/assignments/contractors';
        if (specialty) {
            url += `?specialty=${encodeURIComponent(specialty)}`;
        }
        
        const response = await fetch(url);
        const result = await response.json();
        
        if (result.status === 'success') {
            const select = document.getElementById('assign-contractor');
            select.innerHTML = '<option value="">-- Select Contractor --</option>';
            
            result.data.forEach(contractor => {
                const option = document.createElement('option');
                option.value = contractor.id;
                option.textContent = `${contractor.name} (${contractor.specialty})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading contractors:', error);
    }
}

function filterContractorsBySpecialty() {
    const specialty = document.getElementById('assign-task-specialty').value;
    loadContractors(specialty || null);
}

function showAssignTaskModal() {
    // Load all contractors
    loadContractors();
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('assignTaskModal'));
    modal.show();
}

async function submitTaskAssignment() {
    try {
        const formData = {
            case_id: currentCaseId,
            contractor_id: document.getElementById('assign-contractor').value,
            title: document.getElementById('assign-task-title').value,
            description: document.getElementById('assign-task-description').value,
            priority: document.getElementById('assign-task-priority').value,
            send_email: document.getElementById('assign-send-email').checked
        };
        
        // Validate
        if (!formData.contractor_id) {
            showError('Please select a contractor');
            return;
        }
        
        // Show loading
        const button = event.target;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Assigning...';
        
        const response = await fetch('/api/assignments/assign-task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            console.log('✅ Task assigned successfully');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('assignTaskModal'));
            modal.hide();
            
            // Reset form
            document.getElementById('assignTaskForm').reset();
            
            // Refresh tasks list
            loadCaseTasks(currentCaseId);
            
            // Show success message
            if (result.data.email_sent) {
                console.log('✅ Email notification sent to contractor');
            }
        } else {
            showError('Failed to assign task: ' + result.message);
        }
        
        // Reset button
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-check-circle"></i> Assign Task';
        
    } catch (error) {
        console.error('Error assigning task:', error);
        showError('Failed to assign task. Please try again.');
    }
}
```

#### Acceptance Criteria:
- ✅ Can load contractors via API
- ✅ Can filter by specialty
- ✅ Can assign task and send email
- ✅ Task appears in case tasks list
- ✅ Contractor receives email

---

## 📋 PHASE 4: INTEGRATION & TESTING (1 hour)

### Goal
Ensure both features work seamlessly together.

---

### **4.1: Register New Blueprints (10 min)**

**File: `app.py`**
```python
# Import new blueprint
from features.case_management.task_assignment_api import assignment_bp

# Register blueprint
app.register_blueprint(assignment_bp)
```

---

### **4.2: Create Sample Contractors (10 min)**

**File: `scripts/seed_contractors.py`** (NEW)
```python
#!/usr/bin/env python3
"""Seed sample contractors for testing"""

import json

contractors = [
    {
        "id": "contractor-001",
        "name": "John's Plumbing Services",
        "email": "john.plumber@example.com",
        "phone": "+1-555-0123",
        "specialty": "Plumbing",
        "active": True,
        "created_at": "2025-10-01T00:00:00"
    },
    {
        "id": "contractor-002",
        "name": "Electric Pro Solutions",
        "email": "info@electricpro.example.com",
        "phone": "+1-555-0456",
        "specialty": "Electrical",
        "active": True,
        "created_at": "2025-10-01T00:00:00"
    },
    {
        "id": "contractor-003",
        "name": "Cool Air HVAC",
        "email": "service@coolair.example.com",
        "phone": "+1-555-0789",
        "specialty": "HVAC",
        "active": True,
        "created_at": "2025-10-01T00:00:00"
    }
]

with open('data/contractors.json', 'w') as f:
    json.dump(contractors, f, indent=2)

print("✅ Sample contractors created!")
```

---

### **4.3: End-to-End Testing (40 min)**

#### Test Scenario 1: AI Summary Visibility
1. Open Cases page
2. ✅ Verify AI summary preview visible in list
3. Click case
4. ✅ Verify full AI summary displayed prominently
5. ✅ Verify key points, urgency, sentiment shown
6. Send new email to case
7. ✅ Verify summary updates

#### Test Scenario 2: Task Assignment Workflow
1. Open a case
2. Click "Assign Task" button
3. ✅ Modal opens with contractor dropdown
4. Select specialty → ✅ Contractors filtered
5. Fill in task details
6. Check "Send email notification"
7. Click "Assign Task"
8. ✅ Task appears in case tasks list
9. ✅ Task shows "Assigned to: [Contractor Name]"
10. ✅ Check contractor's email inbox
11. ✅ Verify assignment email received with all details

#### Test Scenario 3: Integration
1. Case with urgent issue
2. ✅ AI summary shows "Urgent" badge
3. Assign task to plumber
4. ✅ Email includes urgency level
5. ✅ Task linked to case
6. ✅ Timeline shows assignment event

---

## 📊 PHASE 5: DOCUMENTATION & ROLLOUT (30 minutes)

### Goal
Document features for users and prepare for production.

---

### **5.1: User Documentation**

**File: `docs/USER_GUIDE_FEATURES.md`** (NEW)
```markdown
# HandyConnect User Guide: Key Features

## Feature 1: AI-Powered Case Summaries

### What It Does
Automatically generates intelligent summaries of customer issues using AI, so you can understand problems at a glance.

### How to Use It
1. **In Cases List**: See brief summary preview for each case
2. **In Case Details**: View full AI-generated summary with:
   - Main issue description
   - Key actionable points
   - Urgency level
   - Customer sentiment

### Benefits
- Save time reading long email threads
- Quickly prioritize cases
- Understand context instantly
- Auto-updates when new emails arrive

---

## Feature 2: Task Assignment to Contractors

### What It Does
Assign tasks to third-party contractors (plumbers, electricians, etc.) and automatically notify them via email.

### How to Use It
1. Open a case
2. Click **"Assign Task"** button
3. Select contractor specialty (Plumbing, Electrical, HVAC, etc.)
4. Choose contractor from filtered list
5. Fill in task details
6. Check "Send email notification"
7. Click **"Assign Task"**

### What Happens Next
- ✅ Task created and linked to case
- ✅ Email sent to contractor with:
  - Task details
  - Property information
  - Customer contact info
  - Priority level
- ✅ Task status tracked in case
- ✅ Timeline updated with assignment

### Benefits
- Automate contractor notifications
- Ensure contractors have all context
- Track assignments per case
- Maintain communication history
```

---

### **5.2: Quick Reference Card**

Create a 1-page PDF with:
- Screenshots of AI summary
- Step-by-step assignment workflow
- Troubleshooting tips

---

## ✅ ACCEPTANCE CRITERIA SUMMARY

### Feature 1: AI Summary
- [x] Summary visible in Cases list (preview)
- [x] Full summary in Case detail modal
- [x] Includes key points, urgency, sentiment
- [x] Updates when new emails arrive
- [x] Cached to avoid slow page loads
- [x] Readable and accurate

### Feature 2: Task Assignment
- [x] Contractor management system
- [x] Assignment UI in Case detail
- [x] Filter contractors by specialty
- [x] Create and assign task in one step
- [x] Automated email notification
- [x] Email includes all relevant context
- [x] Task tracked in case
- [x] Timeline updated

---

## 📅 TIMELINE SUMMARY

| Phase | Duration | Depends On |
|-------|----------|------------|
| Phase 1: Discovery | 30 min | None |
| Phase 2: AI Summary | 2 hours | Phase 1 |
| Phase 3: Task Assignment | 4 hours | Phase 1 |
| Phase 4: Integration & Testing | 1 hour | Phases 2 & 3 |
| Phase 5: Documentation | 30 min | Phase 4 |
| **TOTAL** | **8 hours** | |

---

## 🎯 IMMEDIATE NEXT STEPS

1. **Run Phase 1 Discovery** (30 min)
   - Validate what exists
   - Document gaps
   - Confirm requirements

2. **Choose Implementation Order**
   - **Option A**: Build both features in parallel (faster)
   - **Option B**: Build Feature 1 first, then Feature 2 (safer)
   - **Option C**: Build Feature 2 first (higher user priority)

3. **Get User Feedback**
   - Show mockups/wireframes
   - Validate workflow
   - Adjust requirements

---

**Ready to start Phase 1 Discovery? Let me know and I'll begin validating existing features!** 🚀

