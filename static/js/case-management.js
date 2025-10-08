/**
 * Case Management JavaScript
 * Handles case management interface functionality
 */

// Global variables
let allCases = [];
let filteredCases = [];
let currentPage = 1;
let itemsPerPage = 20; // Default page size
let selectedCases = new Set();
let currentSort = { field: 'created_at', direction: 'desc' };
let currentCaseId = null; // Global variable to store current case ID
let currentTaskId = null; // Global variable to store current task ID
let caseTasks = []; // Store tasks for the current case
let currentCaseTaskSort = { field: 'created_at', direction: 'desc' }; // Sort state for case tasks

// Utility function: debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Utility function: throttle for high-frequency events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Initialize case management
document.addEventListener('DOMContentLoaded', function() {
    updateSortIcons(); // Set initial sort icon state
    loadCases();
    initializeEventListeners();
    initializeMessageInputOptimizations();
});

// Optimize message input for better keyboard responsiveness
function initializeMessageInputOptimizations() {
    // Add event listeners for message textarea when modal is shown
    document.getElementById('emailResponseModal').addEventListener('shown.bs.modal', function() {
        const messageTextarea = document.getElementById('response-message');
        if (messageTextarea) {
            // Remove any existing listeners to prevent duplicates
            messageTextarea.removeEventListener('input', handleMessageInput);
            messageTextarea.removeEventListener('keydown', handleMessageKeydown);
            
            // Add optimized input handlers
            messageTextarea.addEventListener('input', throttle(handleMessageInput, 16), { passive: true });
            messageTextarea.addEventListener('keydown', handleMessageKeydown, { passive: true });
            
            // Focus the textarea
            setTimeout(() => messageTextarea.focus(), 100);
        }
    });
}

// Handle message input with optimizations
function handleMessageInput(event) {
    // This function can be used for real-time validation or character counting
    // Currently kept minimal to avoid performance issues
}

// Handle message keydown events
function handleMessageKeydown(event) {
    // Handle special keys without interfering with normal typing
    if (event.key === 'Enter' && event.ctrlKey) {
        // Ctrl+Enter to send
        event.preventDefault();
        sendEmailResponse();
    }
}

// Event listeners
function initializeEventListeners() {
    // Create case form submission
    document.getElementById('create-case-form').addEventListener('submit', handleCreateCase);
    
    // Search input
    document.getElementById('search-input').addEventListener('input', debounce(searchCases, 150));
    
    // Filter changes
    ['status-filter', 'priority-filter', 'type-filter'].forEach(filterId => {
        document.getElementById(filterId).addEventListener('change', filterCases);
    });
}

// Load cases from API
async function loadCases() {
    try {
        console.log('Loading cases...');
        showLoader();
        
        const response = await fetch('/api/cases/');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Response error:', errorText);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('API Response:', result);
        
        if (result.status === 'success') {
            allCases = result.data.cases || [];
            filteredCases = [...allCases];
            
            console.log('Loaded cases:', allCases.length);
            
            if (allCases.length > 0) {
                // Apply current sort
                sortCases(currentSort.field);
            }
            
            renderCases();
            updateStatistics();
        } else {
            console.error('API Error:', result.message || 'Unknown error');
            showError('Failed to load cases: ' + (result.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error loading cases:', error);
        console.error('Error stack:', error.stack);
        showError('Failed to load cases: ' + error.message);
    } finally {
        hideLoader();
    }
}

// Sort cases
function sortCases(sortBy) {
    // Toggle sort direction if same field is clicked
    if (currentSort.field === sortBy) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.field = sortBy;
        currentSort.direction = 'desc'; // Default to descending for new fields
    }
    
    // Update icon states
    updateSortIcons();
    
    // Sort the filtered cases
    filteredCases.sort((a, b) => {
        let aValue, bValue;
        
        switch (sortBy) {
            case 'created_at':
                aValue = new Date(a.created_at || 0);
                bValue = new Date(b.created_at || 0);
                break;
            case 'priority':
                const priorityOrder = { 'Urgent': 4, 'High': 3, 'Medium': 2, 'Low': 1 };
                aValue = priorityOrder[a.priority] || 0;
                bValue = priorityOrder[b.priority] || 0;
                break;
            case 'status':
                aValue = (a.status || '').toLowerCase();
                bValue = (b.status || '').toLowerCase();
                break;
            default:
                return 0;
        }
        
        // Handle comparison based on sort direction
        if (currentSort.direction === 'desc') {
            return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
        } else {
            return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        }
    });
    
    // Update case count display
    document.getElementById('cases-count').textContent = filteredCases.length;
    
    // Reset to first page and render
    currentPage = 1;
    renderCases();
    updatePagination();
    
    // Show notification
    showNotification(`Cases sorted by ${sortBy} (${currentSort.direction})`, 'info');
}

// Update sort icon states
function updateSortIcons() {
    // Reset all icons
    document.getElementById('sort-newest-icon').className = 'bi bi-sort-down';
    document.getElementById('sort-priority-icon').className = 'bi bi-sort-up';
    document.getElementById('sort-status-icon').className = 'bi bi-sort-alpha-down';
    
    // Reset all button states
    const buttons = ['sort-newest-btn', 'sort-priority-btn', 'sort-status-btn'];
    buttons.forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline-secondary');
        }
    });
    
    // Update active sort icon and button
    const iconMap = {
        'created_at': 'sort-newest-icon',
        'priority': 'sort-priority-icon',
        'status': 'sort-status-icon'
    };
    
    const buttonMap = {
        'created_at': 'sort-newest-btn',
        'priority': 'sort-priority-btn',
        'status': 'sort-status-btn'
    };
    
    const activeIcon = document.getElementById(iconMap[currentSort.field]);
    const activeButton = document.getElementById(buttonMap[currentSort.field]);
    
    if (activeIcon) {
        const iconMap2 = {
            'created_at': { asc: 'bi-sort-up', desc: 'bi-sort-down' },
            'priority': { asc: 'bi-sort-down', desc: 'bi-sort-up' },
            'status': { asc: 'bi-sort-alpha-up', desc: 'bi-sort-alpha-down' }
        };
        activeIcon.className = `bi ${iconMap2[currentSort.field][currentSort.direction]}`;
    }
    
    if (activeButton) {
        activeButton.classList.remove('btn-outline-secondary');
        activeButton.classList.add('btn-primary');
    }
}

// ==================== CASE TASKS MANAGEMENT ====================

// Load tasks for the current case
async function loadCaseTasks(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}/tasks`);
        const result = await response.json();
        
        if (result.status === 'success') {
            caseTasks = result.data.tasks || [];
            renderCaseTasks();
        } else {
            console.error('Failed to load case tasks:', result.message);
            caseTasks = [];
            renderCaseTasks();
        }
    } catch (error) {
        console.error('Error loading case tasks:', error);
        caseTasks = [];
        renderCaseTasks();
    }
}

// Render tasks table in case detail
function renderCaseTasks() {
    const tbody = document.getElementById('case-tasks-tbody');
    const emptyDiv = document.getElementById('case-tasks-empty');
    
    if (!tbody) return;
    
    if (caseTasks.length === 0) {
        tbody.innerHTML = '';
        if (emptyDiv) {
            emptyDiv.style.display = 'block';
        }
        return;
    }
    
    if (emptyDiv) {
        emptyDiv.style.display = 'none';
    }
    
    tbody.innerHTML = caseTasks.map(task => {
        const isCompleted = task.status === 'Completed' || task.status === 'Resolved';
        const rowClass = isCompleted ? 'table-success' : '';
        const textClass = isCompleted ? 'text-decoration-line-through text-muted' : '';
        
        return `
        <tr data-task-id="${task.id}" onclick="viewTaskDetail('${task.id}')" style="cursor: pointer;" class="${rowClass}">
            <td onclick="event.stopPropagation();">
                <input type="checkbox" class="task-checkbox" value="${task.id}" 
                       onchange="toggleCaseTaskSelection('${task.id}')"
                       ${isCompleted ? 'checked' : ''}>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <div>
                        <div class="fw-medium ${textClass}">${task.subject || task.title || 'No Subject'}</div>
                        <small class="text-muted">from ${task.sender || 'Unknown'}</small>
                    </div>
                </div>
            </td>
            <td>
                <span class="badge bg-secondary">${task.category || 'General'}</span>
            </td>
            <td>
                <span class="badge ${getPriorityBadgeClass(task.priority)}">${task.priority || 'Medium'}</span>
            </td>
            <td onclick="event.stopPropagation();">
                <select class="form-select form-select-sm" onchange="updateTaskStatusInline('${task.id}', this.value)" 
                        style="width: auto; min-width: 120px;">
                    <option value="New" ${task.status === 'New' ? 'selected' : ''}>New</option>
                    <option value="In Progress" ${task.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                    <option value="Completed" ${task.status === 'Completed' ? 'selected' : ''}>Completed</option>
                    <option value="On Hold" ${task.status === 'On Hold' ? 'selected' : ''}>On Hold</option>
                    <option value="Resolved" ${task.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
                </select>
            </td>
            <td>
                <small class="text-muted">${formatDate(task.created_at)}</small>
            </td>
            <td>
                ${task.assigned_to ? `
                    <div>
                        <span class="badge ${task.assigned_role === 'External' ? 'bg-success' : 'bg-info'}">
                            ${task.assigned_to}
                        </span>
                        ${task.assigned_role ? `<br><small class="text-muted">${task.assigned_role}</small>` : ''}
                    </div>
                ` : '<span class="badge bg-secondary">Unassigned</span>'}
            </td>
            <td onclick="event.stopPropagation();">
                ${!task.assigned_to ? `
                    <button class="btn btn-sm btn-outline-primary" onclick="showTaskAssignmentModal('${task.id}', '${(task.subject || task.title || 'No Subject').replace(/'/g, "\\'")}')">
                        <i class="bi bi-person-plus"></i> Assign
                    </button>
                ` : `
                    <button class="btn btn-sm btn-outline-secondary" onclick="showTaskAssignmentModal('${task.id}', '${(task.subject || task.title || 'No Subject').replace(/'/g, "\\'")}')">
                        <i class="bi bi-pencil"></i> Reassign
                    </button>
                `}
            </td>
        </tr>
        `;
    }).join('');
}

// Get priority badge class
function getPriorityBadgeClass(priority) {
    const classes = {
        'Urgent': 'bg-danger',
        'High': 'bg-warning',
        'Medium': 'bg-info',
        'Low': 'bg-secondary'
    };
    return classes[priority] || 'bg-secondary';
}

// Sort case tasks
function sortCaseTasks(sortBy) {
    if (currentCaseTaskSort.field === sortBy) {
        currentCaseTaskSort.direction = currentCaseTaskSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentCaseTaskSort.field = sortBy;
        currentCaseTaskSort.direction = 'desc';
    }
    
    updateCaseTaskSortIcons();
    
    caseTasks.sort((a, b) => {
        let aValue, bValue;
        
        switch (sortBy) {
            case 'created_at':
                aValue = new Date(a.created_at || 0);
                bValue = new Date(b.created_at || 0);
                break;
            case 'priority':
                const priorityOrder = { 'Urgent': 4, 'High': 3, 'Medium': 2, 'Low': 1 };
                aValue = priorityOrder[a.priority] || 0;
                bValue = priorityOrder[b.priority] || 0;
                break;
            case 'status':
                aValue = (a.status || '').toLowerCase();
                bValue = (b.status || '').toLowerCase();
                break;
            default:
                return 0;
        }
        
        if (currentCaseTaskSort.direction === 'desc') {
            return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
        } else {
            return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        }
    });
    
    renderCaseTasks();
    showNotification(`Tasks sorted by ${sortBy} (${currentCaseTaskSort.direction})`, 'info');
}

// Update case task sort icons
function updateCaseTaskSortIcons() {
    document.getElementById('case-task-sort-newest-icon').className = 'bi bi-sort-down';
    document.getElementById('case-task-sort-priority-icon').className = 'bi bi-sort-up';
    document.getElementById('case-task-sort-status-icon').className = 'bi bi-sort-alpha-down';
    
    const iconMap = {
        'created_at': 'case-task-sort-newest-icon',
        'priority': 'case-task-sort-priority-icon',
        'status': 'case-task-sort-status-icon'
    };
    
    const activeIcon = document.getElementById(iconMap[currentCaseTaskSort.field]);
    if (activeIcon) {
        const iconMap2 = {
            'created_at': { asc: 'bi-sort-up', desc: 'bi-sort-down' },
            'priority': { asc: 'bi-sort-down', desc: 'bi-sort-up' },
            'status': { asc: 'bi-sort-alpha-up', desc: 'bi-sort-alpha-down' }
        };
        activeIcon.className = `bi ${iconMap2[currentCaseTaskSort.field][currentCaseTaskSort.direction]}`;
    }
}

// View task detail
async function viewTaskDetail(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const task = result.data;
            currentTaskId = taskId;
            populateTaskDetailModal(task);
            const modal = new bootstrap.Modal(document.getElementById('taskDetailModal'));
            modal.show();
        } else {
            showError('Failed to load task details: ' + result.message);
        }
    } catch (error) {
        console.error('Error loading task details:', error);
        showError('Failed to load task details. Please try again.');
    }
}

// Populate task detail modal
function populateTaskDetailModal(task) {
    document.getElementById('task-modal-title').textContent = task.subject || task.title || 'Task Details';
    document.getElementById('task-detail-subject').textContent = task.subject || task.title || 'No Subject';
    document.getElementById('task-detail-category').innerHTML = `<span class="badge bg-secondary">${task.category || 'General'}</span>`;
    document.getElementById('task-detail-priority').innerHTML = `<span class="badge ${getPriorityBadgeClass(task.priority)}">${task.priority || 'Medium'}</span>`;
    document.getElementById('task-detail-status').innerHTML = `<span class="badge bg-info">${task.status || 'New'}</span>`;
    document.getElementById('task-detail-created').textContent = formatDate(task.created_at);
    document.getElementById('task-detail-assigned').innerHTML = `<span class="badge bg-info">${task.assigned_to || 'Unassigned'}</span>`;
    document.getElementById('task-detail-description').textContent = task.content || task.description || 'No description available';
    
    // Show/hide complete task button based on status
    const completeBtn = document.getElementById('complete-task-btn');
    const saveBtn = document.getElementById('save-completion-btn');
    const completionSection = document.getElementById('task-completion-section');
    
    if (task.status === 'Completed' || task.status === 'Resolved') {
        completeBtn.style.display = 'none';
        saveBtn.style.display = 'none';
        completionSection.style.display = 'none';
    } else {
        completeBtn.style.display = 'inline-block';
        saveBtn.style.display = 'none';
        completionSection.style.display = 'none';
    }
    
    // Load task notes
    loadTaskNotes(currentTaskId);
}

// Show task completion form
function showTaskCompletionForm() {
    const completionSection = document.getElementById('task-completion-section');
    const completeBtn = document.getElementById('complete-task-btn');
    const saveBtn = document.getElementById('save-completion-btn');
    
    completionSection.style.display = 'block';
    completeBtn.style.display = 'none';
    saveBtn.style.display = 'inline-block';
    
    // Set current date/time as default
    const now = new Date();
    const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    document.getElementById('completion-date').value = localDateTime;
}

// Save task completion
async function saveTaskCompletion() {
    try {
        const form = document.getElementById('taskCompletionForm');
        const formData = new FormData(form);
        
        const completionData = {
            status: document.getElementById('completion-status').value,
            completion_date: document.getElementById('completion-date').value,
            completion_notes: document.getElementById('completion-notes').value,
            time_spent: document.getElementById('completion-time-spent').value,
            notify_customer: document.getElementById('notify-customer').checked
        };
        
        if (!completionData.status || !completionData.completion_notes) {
            showError('Please fill in all required fields.');
            return;
        }
        
        const response = await fetch(`/api/tasks/${currentTaskId}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(completionData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showNotification('Task completed successfully!', 'success');
            
            // Close modal and refresh tasks
            const modal = bootstrap.Modal.getInstance(document.getElementById('taskDetailModal'));
            modal.hide();
            
            // Refresh case tasks
            if (currentCaseId) {
                loadCaseTasks(currentCaseId);
            }
        } else {
            showError('Failed to complete task: ' + result.message);
        }
    } catch (error) {
        console.error('Error completing task:', error);
        showError('Failed to complete task. Please try again.');
    }
}

// Load task notes
async function loadTaskNotes(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/notes`);
        const result = await response.json();
        
        const notesList = document.getElementById('task-notes-list');
        if (result.status === 'success' && result.data.notes) {
            notesList.innerHTML = result.data.notes.map(note => `
                <div class="border-bottom pb-2 mb-2">
                    <div class="d-flex justify-content-between">
                        <small class="text-muted">${formatDate(note.created_at)}</small>
                        <small class="text-muted">by ${note.created_by || 'System'}</small>
                    </div>
                    <div class="mt-1">${note.content}</div>
                </div>
            `).join('');
        } else {
            notesList.innerHTML = '<p class="text-muted">No notes available</p>';
        }
    } catch (error) {
        console.error('Error loading task notes:', error);
        document.getElementById('task-notes-list').innerHTML = '<p class="text-muted">Error loading notes</p>';
    }
}

// Update task status inline
async function updateTaskStatusInline(taskId, newStatus) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showNotification(`Task status updated to ${newStatus}`, 'success');
            // Refresh case tasks
            if (currentCaseId) {
                loadCaseTasks(currentCaseId);
            }
        } else {
            showError('Failed to update task status: ' + result.message);
        }
    } catch (error) {
        console.error('Error updating task status:', error);
        showError('Failed to update task status. Please try again.');
    }
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (error) {
        return dateString;
    }
}

// Format case number for display (YYMMDDNNNN format)
function formatCaseNumber(caseNumber) {
    // Input: "2510060005" (10 digits: YYMMDDNNNN)
    // Output: "2510060005" (plain display as requested)
    if (!caseNumber) return 'N/A';
    
    // Validate it's the correct 10-digit format
    if (/^\d{10}$/.test(caseNumber)) {
        return caseNumber;  // Display as-is (Option A: Plain)
    }
    
    // Fallback for any other format
    return caseNumber;
}

// ==================== CASE TASK COMPLETION ====================

// Toggle task completion status
async function toggleCaseTaskSelection(taskId) {
    try {
        const task = caseTasks.find(t => t.id == taskId);
        if (!task) {
            console.error('Task not found:', taskId);
            return;
        }

        // Determine new status based on current status
        const newStatus = task.status === 'Completed' || task.status === 'Resolved' ? 'New' : 'Completed';
        
        // Update task status via API
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        });

        const result = await response.json();

        if (result.status === 'success') {
            // Update local task data
            task.status = newStatus;
            task.updated_at = new Date().toISOString();
            
            // Refresh the tasks display
            renderCaseTasks();
            
            // Show notification
            const action = newStatus === 'Completed' ? 'completed' : 'reopened';
            showNotification(`Task ${action} successfully!`, 'success');
            
            // Update case statistics if needed
            updateStatistics();
        } else {
            showError('Failed to update task status: ' + result.message);
        }
    } catch (error) {
        console.error('Error toggling task completion:', error);
        showError('Failed to update task status. Please try again.');
    }
}

// ==================== PAGE SIZE MANAGEMENT ====================

// Change page size
function changePageSize() {
    const pageSizeSelect = document.getElementById('page-size-select');
    if (pageSizeSelect) {
        itemsPerPage = parseInt(pageSizeSelect.value);
        currentPage = 1; // Reset to first page when changing page size
        renderCases();
        updatePagination();
        showNotification(`Showing ${itemsPerPage} records per page`, 'info');
    }
}

// Render cases table
function renderCases() {
    try {
        console.log('Rendering cases...', filteredCases.length, 'filtered cases');
        const tbody = document.getElementById('cases-tbody');
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const pageCases = filteredCases.slice(startIndex, endIndex);
        
        console.log('Page cases to render:', pageCases.length, pageCases);
        
        if (pageCases.length === 0) {
            console.log('No page cases, showing empty message');
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-4">
                        <i class="bi bi-inbox fs-1 text-muted"></i>
                        <p class="text-muted mt-2">No cases found</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        // Update case count display
        const casesCountElement = document.getElementById('cases-count');
        if (casesCountElement) {
            casesCountElement.textContent = filteredCases.length;
        } else {
            console.error('cases-count element not found');
        }
    
        tbody.innerHTML = pageCases.map(caseItem => `
        <tr data-case-id="${caseItem.case_id}" onclick="viewCaseDetail('${caseItem.case_id}')" style="cursor: pointer;">
            <td onclick="event.stopPropagation();">
                <input type="checkbox" class="case-checkbox" value="${caseItem.case_id}" 
                       onchange="toggleCaseSelection('${caseItem.case_id}')">
            </td>
            <td>
                <strong>${caseItem.case_number}</strong>
            </td>
            <td>
                <div class="text-truncate" style="max-width: 200px;" title="${caseItem.case_title}">
                    ${caseItem.case_title}
                </div>
            </td>
            <td>
                <div>
                    <div class="fw-medium">${caseItem.customer_info?.name || 'Unknown'}</div>
                    <small class="text-muted">${caseItem.customer_info?.email || 'No email'}</small>
                </div>
            </td>
            <td onclick="event.stopPropagation();">
                <select class="form-select form-select-sm" onchange="updateCaseStatusInline('${caseItem.case_id}', this.value)" style="width: auto; min-width: 120px;">
                    <option value="New" ${caseItem.status === 'New' ? 'selected' : ''}>🔵 New</option>
                    <option value="In Progress" ${caseItem.status === 'In Progress' ? 'selected' : ''}>🟡 In Progress</option>
                    <option value="Awaiting Customer" ${caseItem.status === 'Awaiting Customer' ? 'selected' : ''}>⏳ Awaiting Customer</option>
                    <option value="Awaiting Vendor" ${caseItem.status === 'Awaiting Vendor' ? 'selected' : ''}>⏳ Awaiting Vendor</option>
                    <option value="Resolved" ${caseItem.status === 'Resolved' ? 'selected' : ''}>✅ Resolved</option>
                    <option value="Closed" ${caseItem.status === 'Closed' ? 'selected' : ''}>✅ Closed</option>
                </select>
            </td>
            <td>
                <span class="badge ${getPriorityBadgeClass(caseItem.priority)}">
                    ${caseItem.priority}
                </span>
            </td>
            <td>
                <span class="badge ${getSLAStatusBadgeClass(caseItem.sla_status)}">
                    ${caseItem.sla_status}
                </span>
            </td>
            <td>
                <span class="badge bg-info">
                    ${(caseItem.tasks ? caseItem.tasks.length : 0) + (caseItem.threads ? caseItem.threads.length : 0)}
                </span>
            </td>
            <td>
                <span class="badge ${getSentimentBadgeClass(caseItem.sentiment)}">
                    ${caseItem.sentiment || 'Neutral'}
                </span>
            </td>
        </tr>
        `).join('');
        
        updatePagination();
        updateBulkActionsVisibility();
        
    } catch (error) {
        console.error('Error in renderCases:', error);
        showError('Failed to render cases: ' + error.message);
    }
}

// Load AI summaries asynchronously for cases
async function loadCaseSummariesAsync(cases) {
    for (const caseItem of cases) {
        try {
            const summaryElement = document.getElementById(`summary-${caseItem.case_id}`);
            if (!summaryElement) continue;
            
            // Check if summary already exists in cache
            if (caseItem.ai_summary_preview) {
                summaryElement.innerHTML = `
                    <span class="ai-icon"><i class="bi bi-robot"></i></span>
                    <span>${caseItem.ai_summary_preview}</span>
                `;
                continue;
            }
            
            // Fetch summary from API
            const response = await fetch(`/api/cases/${caseItem.case_id}/summary`);
            const result = await response.json();
            
            if (result.status === 'success' && result.data.summary) {
                let summary = result.data.summary;
                
                // Create preview (first 150 chars)
                const preview = summary.length > 150 ? summary.substring(0, 150) + '...' : summary;
                
                // Update element
                summaryElement.innerHTML = `
                    <span class="ai-icon"><i class="bi bi-robot"></i></span>
                    <span title="${summary}">${preview}</span>
                `;
                
                // Cache it
                caseItem.ai_summary_preview = preview;
                caseItem.ai_summary_full = summary;
            } else {
                summaryElement.innerHTML = `
                    <span class="ai-icon text-muted"><i class="bi bi-robot"></i></span>
                    <span class="text-muted small">Summary unavailable</span>
                `;
            }
        } catch (error) {
            console.error(`Error loading summary for case ${caseItem.case_id}:`, error);
            const summaryElement = document.getElementById(`summary-${caseItem.case_id}`);
            if (summaryElement) {
                summaryElement.innerHTML = `
                    <span class="ai-icon text-muted"><i class="bi bi-robot"></i></span>
                    <span class="text-muted small">Error loading summary</span>
                `;
            }
        }
    }
}

// Update statistics
function updateStatistics() {
    try {
        if (!allCases || allCases.length === 0) {
            document.getElementById('open-cases').textContent = '0';
            document.getElementById('resolved-cases').textContent = '0';
            document.getElementById('sla-compliant').textContent = '0%';
            return;
        }
        
        const stats = {
            open: allCases.filter(c => !['Resolved', 'Closed'].includes(c.status)).length,
            resolved: allCases.filter(c => ['Resolved', 'Closed'].includes(c.status)).length,
            slaCompliant: allCases.filter(c => c.sla_status === 'On Time').length
        };
        
        document.getElementById('open-cases').textContent = stats.open;
        document.getElementById('resolved-cases').textContent = stats.resolved;
        document.getElementById('sla-compliant').textContent = 
            allCases.length > 0 ? Math.round((stats.slaCompliant / allCases.length) * 100) + '%' : '0%';
        
        console.log('Updated statistics:', stats);
    } catch (error) {
        console.error('Error in updateStatistics:', error);
        showError('Failed to update statistics: ' + error.message);
    }
}

// Filter cases
function filterCases() {
    const statusFilter = document.getElementById('status-filter').value;
    const priorityFilter = document.getElementById('priority-filter').value;
    const typeFilter = document.getElementById('type-filter').value;
    
    filteredCases = allCases.filter(caseItem => {
        const statusMatch = !statusFilter || caseItem.status === statusFilter;
        const priorityMatch = !priorityFilter || caseItem.priority === priorityFilter;
        const typeMatch = !typeFilter || caseItem.case_type === typeFilter;
        
        return statusMatch && priorityMatch && typeMatch;
    });
    
    currentPage = 1;
    renderCases();
}

// Search cases
function searchCases() {
    const searchQuery = document.getElementById('search-input').value.toLowerCase().trim();
    
    if (!searchQuery) {
        filteredCases = [...allCases];
    } else {
        filteredCases = allCases.filter(caseItem => {
            const titleMatch = caseItem.case_title.toLowerCase().includes(searchQuery);
            const numberMatch = caseItem.case_number.toLowerCase().includes(searchQuery);
            const customerNameMatch = caseItem.customer_info?.name?.toLowerCase().includes(searchQuery);
            const customerEmailMatch = caseItem.customer_info?.email?.toLowerCase().includes(searchQuery);
            
            return titleMatch || numberMatch || customerNameMatch || customerEmailMatch;
        });
    }
    
    // Update search results count
    updateSearchResultsCount();
    
    currentPage = 1;
    renderCases();
}

// Update search results count display
function updateSearchResultsCount() {
    const searchResultsElement = document.getElementById('search-results-count');
    if (searchResultsElement) {
        const searchQuery = document.getElementById('search-input').value.toLowerCase().trim();
        const count = filteredCases.length;
        
        if (searchQuery) {
            searchResultsElement.textContent = `${count} result${count !== 1 ? 's' : ''}`;
        } else {
            searchResultsElement.textContent = '';
        }
    }
}

// Clear search
function clearSearch() {
    document.getElementById('search-input').value = '';
    searchCases();
}

// Update pagination
function updatePagination() {
    const totalPages = Math.ceil(filteredCases.length / itemsPerPage);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Previous button
    paginationHTML += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">Previous</a>
        </li>
    `;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage || i === 1 || i === totalPages || 
            (i >= currentPage - 2 && i <= currentPage + 2)) {
            paginationHTML += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
                </li>
            `;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    // Next button
    paginationHTML += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">Next</a>
        </li>
    `;
    
    pagination.innerHTML = paginationHTML;
}

// Change page
function changePage(page) {
    const totalPages = Math.ceil(filteredCases.length / itemsPerPage);
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        renderCases();
    }
}

// Show create case modal
function showCreateCaseModal() {
    const modal = new bootstrap.Modal(document.getElementById('createCaseModal'));
    modal.show();
}

// Handle create case form submission
async function handleCreateCase(event) {
    event.preventDefault();
    
    const formData = {
        case_title: document.getElementById('case-title').value,
        case_type: document.getElementById('case-type').value,
        priority: document.getElementById('case-priority').value,
        assigned_to: document.getElementById('case-assigned-to').value,
        customer_info: {
            name: document.getElementById('customer-name').value,
            email: document.getElementById('customer-email').value
        },
        description: document.getElementById('case-description').value
    };
    
    try {
        const response = await fetch('/api/cases/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showSuccess('Case created successfully!');
            bootstrap.Modal.getInstance(document.getElementById('createCaseModal')).hide();
            document.getElementById('create-case-form').reset();
            loadCases();
        } else {
            showError('Failed to create case: ' + result.message);
        }
    } catch (error) {
        console.error('Error creating case:', error);
        showError('Failed to create case. Please try again.');
    }
}

// View case detail
async function viewCaseDetail(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const caseData = result.data.case;
            const tasks = result.data.related_tasks;
            currentCaseId = caseId; // Set current case ID
            
            // Update modal title and case number
            document.getElementById('case-modal-number').textContent = formatCaseNumber(caseData.case_number);
            
            // Populate case info
            try {
                populateCaseInfo(caseData);
            } catch (err) {
                console.error('Error populating case info:', err);
            }
            
            // Set up tab event listeners first
            setupCaseDetailTabs(caseData.case_id);
            
            // Show modal immediately so user sees loading states
            const modal = new bootstrap.Modal(document.getElementById('caseDetailModal'));
            modal.show();
            
            // Load async data (these will populate as they complete)
            loadCaseSummary(caseId).catch(err => console.error('Summary load error:', err));
            loadCaseTimeline(caseData.case_id).catch(err => console.error('Timeline load error:', err));
            loadCaseCommunication(caseData.case_id).catch(err => console.error('Communication load error:', err));
            loadCaseTasks(caseData.case_id).catch(err => console.error('Tasks load error:', err));
            
            // Initialize the first tab after modal is shown
            setTimeout(() => {
                const firstTab = document.querySelector('#caseDetailTabs .nav-link.active');
                if (firstTab) {
                    const tabTrigger = new bootstrap.Tab(firstTab);
                    tabTrigger.show();
                }
            }, 200);
        } else {
            showError('Failed to load case details: ' + result.message);
        }
    } catch (error) {
        console.error('Error loading case details:', error);
        showError('Failed to load case details. Please try again.');
    }
}

// Update case status
async function updateCaseStatus(caseId, status) {
    try {
        const response = await fetch(`/api/cases/${caseId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: status,
                actor: 'user'
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            loadCases();
        } else {
            showError('Failed to update case status: ' + result.message);
        }
    } catch (error) {
        console.error('Error updating case status:', error);
        showError('Failed to update case status. Please try again.');
    }
}

// Update case status inline (from dropdown)
async function updateCaseStatusInline(caseId, status) {
    try {
        const response = await fetch(`/api/cases/${caseId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: status,
                actor: 'user'
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Update the case in the current list without full reload
            const caseIndex = allCases.findIndex(c => c.case_id === caseId);
            if (caseIndex !== -1) {
                allCases[caseIndex].status = status;
                renderCases();
            }
        } else {
            showError('Failed to update case status: ' + result.message);
            loadCases(); // Reload to restore original state
        }
    } catch (error) {
        console.error('Error updating case status:', error);
        showError('Failed to update case status. Please try again.');
        loadCases(); // Reload to restore original state
    }
}

// Toggle case selection
function toggleCaseSelection(caseId) {
    if (selectedCases.has(caseId)) {
        selectedCases.delete(caseId);
    } else {
        selectedCases.add(caseId);
    }
    
    updateBulkActionsVisibility();
    updateSelectAllCheckbox();
}

// Toggle select all
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('select-all');
    const caseCheckboxes = document.querySelectorAll('.case-checkbox');
    
    if (selectAllCheckbox.checked) {
        caseCheckboxes.forEach(checkbox => {
            checkbox.checked = true;
            selectedCases.add(checkbox.value);
        });
    } else {
        caseCheckboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        selectedCases.clear();
    }
    
    updateBulkActionsVisibility();
}

// Update select all checkbox state
function updateSelectAllCheckbox() {
    const selectAllCheckbox = document.getElementById('select-all');
    const caseCheckboxes = document.querySelectorAll('.case-checkbox');
    const checkedCount = document.querySelectorAll('.case-checkbox:checked').length;
    
    if (checkedCount === 0) {
        selectAllCheckbox.indeterminate = false;
        selectAllCheckbox.checked = false;
    } else if (checkedCount === caseCheckboxes.length) {
        selectAllCheckbox.indeterminate = false;
        selectAllCheckbox.checked = true;
    } else {
        selectAllCheckbox.indeterminate = true;
        selectAllCheckbox.checked = false;
    }
}

// Update bulk actions visibility
function updateBulkActionsVisibility() {
    const bulkActionsBtn = document.querySelector('.bulk-actions-btn');
    if (bulkActionsBtn) {
        bulkActionsBtn.style.display = selectedCases.size > 0 ? 'block' : 'none';
    }
}

// Apply bulk actions
async function applyBulkActions() {
    if (selectedCases.size === 0) {
        showError('No cases selected');
        return;
    }
    
    const status = document.getElementById('bulk-status').value;
    const assignee = document.getElementById('bulk-assignee').value;
    
    if (!status && !assignee) {
        showError('Please select at least one action');
        return;
    }
    
    try {
        const caseIds = Array.from(selectedCases);
        
        // Update status if selected
        if (status) {
            const response = await fetch('/api/cases/bulk/status', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    case_ids: caseIds,
                    status: status,
                    actor: 'user'
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                showSuccess(`Updated status for ${result.data.updated_count} cases`);
            }
        }
        
        // Assign if selected
        if (assignee) {
            const response = await fetch('/api/cases/bulk/assign', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    case_ids: caseIds,
                    assignee: assignee,
                    actor: 'user'
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                showSuccess(`Assigned ${result.data.updated_count} cases to ${assignee}`);
            }
        }
        
        // Clear selections and reload
        selectedCases.clear();
        bootstrap.Modal.getInstance(document.getElementById('bulkActionsModal')).hide();
        loadCases();
        
    } catch (error) {
        console.error('Error applying bulk actions:', error);
        showError('Failed to apply bulk actions. Please try again.');
    }
}

// Refresh cases
function refreshCases() {
    loadCases();
}

// Utility functions
function getStatusBadgeClass(status) {
    switch (status) {
        case 'New': return 'bg-secondary';
        case 'In Progress': return 'bg-primary';
        case 'Awaiting Customer': return 'bg-warning';
        case 'Awaiting Vendor': return 'bg-info';
        case 'Resolved': return 'bg-success';
        case 'Closed': return 'bg-dark';
        default: return 'bg-secondary';
    }
}

function getPriorityBadgeClass(priority) {
    switch (priority) {
        case 'Low': return 'bg-secondary';
        case 'Medium': return 'bg-info';
        case 'High': return 'bg-warning';
        case 'Urgent': return 'bg-danger';
        case 'Critical': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

function getSLAStatusBadgeClass(slaStatus) {
    switch (slaStatus) {
        case 'On Time': return 'bg-success';
        case 'At Risk': return 'bg-warning';
        case 'Breached': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

// Get sentiment badge class
function getSentimentBadgeClass(sentiment) {
    switch (sentiment) {
        case 'Positive': return 'bg-success';
        case 'Neutral': return 'bg-secondary';
        case 'Negative': return 'bg-danger';
        case 'Frustrated': return 'bg-danger';
        case 'Satisfied': return 'bg-success';
        case 'Concerned': return 'bg-warning';
        default: return 'bg-secondary';
    }
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return dateString;
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showLoader() {
    // Show loading spinner
    const tbody = document.getElementById('cases-tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="9" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="text-muted mt-2">Loading cases...</p>
            </td>
        </tr>
    `;
}

function hideLoader() {
    // Loader will be replaced by renderCases()
}

function showSuccess(message) {
    // You can implement a toast notification system here
    console.log('Success:', message);
    // Silent success - no alert
}

function showError(message) {
    // You can implement a toast notification system here
    alert('Error: ' + message);
}

function showNotification(message, type = 'info') {
    // Console log for debugging, silent for user
    console.log(`${type.toUpperCase()}:`, message);
    // You can implement a toast notification system here
    // For now, we'll keep it silent to avoid cluttering the UI
}

// Enhanced case detail functions

// Load AI-generated case summary
async function loadCaseSummary(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}/summary`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const summaryData = result.data;
            let summary = summaryData.summary;
            
            // Format the summary for HTML display
            // Replace **text** with <strong>text</strong>
            summary = summary.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            // Replace line breaks with <br>
            summary = summary.replace(/\n/g, '<br>');
            
            // Update main summary
            const summaryElement = document.getElementById('case-ai-summary');
            summaryElement.innerHTML = summary;
            
            // Show when summary was generated
            const generatedAt = summaryData.generated_at || new Date().toISOString();
            const timeAgo = getTimeAgo(generatedAt);
            summaryElement.innerHTML += `<div class="mt-2"><small class="text-muted"><i class="bi bi-clock me-1"></i>Updated ${timeAgo}</small></div>`;
            
            // Add urgency and sentiment badges
            const badgesContainer = document.getElementById('case-summary-badges');
            const badges = [];
            
            // Detect urgency from summary
            const urgency = detectUrgency(summary);
            if (urgency) {
                badges.push(`<span class="badge ${getUrgencyBadgeClass(urgency)}">${urgency}</span>`);
            }
            
            // Detect sentiment from summary
            const sentiment = detectSentiment(summary);
            if (sentiment) {
                badges.push(`<span class="badge ${getSentimentBadgeClass(sentiment)}">${sentiment}</span>`);
            }
            
            badgesContainer.innerHTML = badges.join(' ');
            
        } else {
            document.getElementById('case-ai-summary').innerHTML = 
                '<span class="text-muted">Summary generation temporarily unavailable.</span>';
        }
    } catch (error) {
        console.error('Error loading case summary:', error);
        document.getElementById('case-ai-summary').innerHTML = 
            '<span class="text-muted">Error loading summary. Please try again.</span>';
    }
}

// Extract key points from summary text
function extractKeyPoints(summary) {
    const keyPoints = [];
    
    // Look for numbered lists (1. 2. 3. etc.)
    const numberedPoints = summary.match(/\d+\.\s*([^<\n]+)/g);
    if (numberedPoints) {
        return numberedPoints.map(point => point.replace(/^\d+\.\s*/, '').trim());
    }
    
    // Look for bullet points
    const bulletPoints = summary.match(/[•\-\*]\s*([^<\n]+)/g);
    if (bulletPoints) {
        return bulletPoints.map(point => point.replace(/^[•\-\*]\s*/, '').trim());
    }
    
    // Look for sentences that indicate action items
    const actionWords = ['must', 'should', 'need', 'require', 'fix', 'repair', 'replace', 'install'];
    const sentences = summary.split(/[.!]/);
    for (const sentence of sentences) {
        const lowerSentence = sentence.toLowerCase();
        if (actionWords.some(word => lowerSentence.includes(word))) {
            const cleanSentence = sentence.replace(/<[^>]*>/g, '').trim();
            if (cleanSentence.length > 10) {
                keyPoints.push(cleanSentence);
            }
        }
    }
    
    return keyPoints.slice(0, 5); // Max 5 key points
}

// Detect urgency level from summary text
function detectUrgency(summary) {
    const lowerSummary = summary.toLowerCase();
    
    if (lowerSummary.match(/urgent|emergency|immediate|critical|asap|dangerous|safety/)) {
        return 'Urgent';
    }
    if (lowerSummary.match(/high priority|important|soon|promptly/)) {
        return 'High Priority';
    }
    if (lowerSummary.match(/routine|normal|standard|regular/)) {
        return 'Normal';
    }
    
    return null;
}

// Detect sentiment from summary text
function detectSentiment(summary) {
    const lowerSummary = summary.toLowerCase();
    
    if (lowerSummary.match(/angry|furious|appalled|disgusted|outraged/)) {
        return 'Angry';
    }
    if (lowerSummary.match(/frustrated|disappointed|upset|concerned|worried/)) {
        return 'Frustrated';
    }
    if (lowerSummary.match(/satisfied|happy|pleased|grateful|thank/)) {
        return 'Satisfied';
    }
    if (lowerSummary.match(/calm|neutral|polite|courteous/)) {
        return 'Neutral';
    }
    
    return null;
}

// Get urgency badge class
function getUrgencyBadgeClass(urgency) {
    const classes = {
        'Urgent': 'bg-danger',
        'High Priority': 'bg-warning text-dark',
        'Normal': 'bg-info'
    };
    return classes[urgency] || 'bg-secondary';
}

// Get sentiment badge class (reused from existing function)
function getSentimentBadgeClass(sentiment) {
    const classes = {
        'Angry': 'bg-danger',
        'Frustrated': 'bg-warning text-dark',
        'Satisfied': 'bg-success',
        'Neutral': 'bg-secondary',
        'Positive': 'bg-success',
        'Negative': 'bg-danger'
    };
    return classes[sentiment] || 'bg-secondary';
}

// Get time ago string (e.g., "2 minutes ago", "1 hour ago")
function getTimeAgo(timestamp) {
    try {
        const now = new Date();
        const then = new Date(timestamp);
        const seconds = Math.floor((now - then) / 1000);
        
        if (seconds < 60) {
            return 'just now';
        }
        
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) {
            return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
        }
        
        const hours = Math.floor(minutes / 60);
        if (hours < 24) {
            return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
        }
        
        const days = Math.floor(hours / 24);
        if (days < 30) {
            return `${days} ${days === 1 ? 'day' : 'days'} ago`;
        }
        
        return formatDate(timestamp);
    } catch (e) {
        return 'recently';
    }
}

// Populate case information in the modal
function populateCaseInfo(caseData) {
    // Status dropdown
    const statusSelect = document.getElementById('case-status-select');
    if (statusSelect) {
        statusSelect.value = caseData.status || 'New';
    }
    
    // Priority dropdown
    const prioritySelect = document.getElementById('case-priority-select');
    if (prioritySelect) {
        prioritySelect.value = caseData.priority || 'Medium';
    }
    
    // Type dropdown
    const typeSelect = document.getElementById('case-type-select');
    if (typeSelect) {
        typeSelect.value = caseData.case_type || 'General';
    }
    
    // Created date
    document.getElementById('case-detail-created').textContent = formatDate(caseData.created_at || new Date().toISOString());
    
    // Customer info
    const customerInfo = caseData.customer_info || {};
    document.getElementById('case-detail-customer-name').textContent = customerInfo.name || 'Unknown Customer';
    document.getElementById('case-detail-customer-email').textContent = customerInfo.email || 'No email provided';
    document.getElementById('case-detail-property-number').textContent = customerInfo.property_number || 'Not specified';
    document.getElementById('case-detail-block-number').textContent = customerInfo.block_number || 'Not specified';
    
    // Description
    const description = caseData.case_description || 
                       (caseData.case_metadata && caseData.case_metadata.description) || 
                       'No description available.';
    document.getElementById('case-detail-description').textContent = description;
}

// Populate related tasks with clickable links
function populateRelatedTasks(tasks) {
    const container = document.getElementById('case-related-tasks');
    
    if (!tasks || tasks.length === 0) {
        container.innerHTML = '<p class="text-muted">No related tasks found.</p>';
        return;
    }
    
    container.innerHTML = tasks.map(task => `
        <div class="d-flex justify-content-between align-items-center p-2 border rounded mb-2 related-task-item">
            <div class="d-flex align-items-center">
                <input type="checkbox" class="form-check-input me-2" ${(task.status === 'Completed' || task.status === 'Resolved') ? 'checked' : ''}>
                <div>
                    <a href="#" class="related-task-link text-decoration-none" data-task-id="${task.id || task.task_id || 'unknown'}">
                        <strong>Task #${task.id || task.task_id || 'Unknown'}</strong>
                    </a>
                    <br>
                    <small class="text-muted">${task.subject || task.title || 'No subject'}</small>
                </div>
            </div>
            <span class="badge ${getStatusBadgeClass(task.status || 'New')}">${task.status || 'New'}</span>
        </div>
    `).join('');
    
    // Add click handlers for task links
    container.querySelectorAll('.related-task-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const taskId = e.target.closest('.related-task-link').dataset.taskId;
            viewTaskDetail(taskId);
        });
    });
}

// View task detail (placeholder for now)
function viewTaskDetail(taskId) {
    // For now, redirect to tasks page with highlight
    window.location.href = `/tasks?highlight=${taskId}`;
}

// Load case timeline events
async function loadCaseTimeline(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}/timeline`);
        const result = await response.json();
        
        const container = document.getElementById('case-timeline-events');
        
        if (result.status === 'success' && result.data.timeline && result.data.timeline.length > 0) {
            container.innerHTML = result.data.timeline.map(event => `
                <div class="d-flex align-items-start mb-3">
                    <div class="flex-shrink-0">
                        <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                            <i class="bi bi-clock text-white"></i>
                        </div>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <h6 class="mb-1">${event.event_type.replace('_', ' ').toUpperCase()}</h6>
                        <p class="mb-1 text-muted">${event.description}</p>
                        <small class="text-muted">${formatDate(event.timestamp)}</small>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="text-muted">No timeline events found.</p>';
        }
    } catch (error) {
        console.error('Error loading timeline:', error);
        document.getElementById('case-timeline-events').innerHTML = 
            '<p class="text-danger">Timeline loading failed. Please try refreshing the page.</p>';
    }
}

// Load case tasks (both existing and generated)
async function loadCaseTasks(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}/tasks`);
        const result = await response.json();
        
        const container = document.getElementById('case-tasks-checklist');
        
        if (result.status === 'success' && result.data.tasks.length > 0) {
            container.innerHTML = result.data.tasks.map(task => `
                <div class="d-flex align-items-start mb-3 p-3 border rounded">
                    <div class="form-check me-3">
                        <input class="form-check-input" type="checkbox" ${task.status === 'Completed' || task.status === 'Resolved' ? 'checked' : ''} 
                               onchange="toggleTaskStatus('${task.id}', this.checked)">
                    </div>
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="mb-1">${task.title}</h6>
                            <div class="d-flex gap-1">
                                <span class="badge ${getPriorityBadgeClass(task.priority)}">${task.priority}</span>
                                ${task.estimated_time ? `<span class="badge bg-secondary">${task.estimated_time}</span>` : ''}
                                ${task.type === 'generated' ? '<span class="badge bg-info">AI Generated</span>' : ''}
                            </div>
                        </div>
                        <p class="text-muted mb-2">${task.description}</p>
                        <small class="text-muted">
                            Status: ${task.status} 
                            ${task.created_at ? `• Created: ${formatDate(task.created_at)}` : ''}
                        </small>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="text-muted">No tasks found for this case.</p>';
        }
    } catch (error) {
        console.error('Error loading case tasks:', error);
        document.getElementById('case-tasks-checklist').innerHTML = 
            '<p class="text-muted">Failed to load tasks.</p>';
    }
}

// Toggle task status
async function toggleTaskStatus(taskId, completed) {
    try {
        const status = completed ? 'Completed' : 'Pending';
        
        // For now, just update the UI. In a real implementation, you'd call an API
        console.log(`Task ${taskId} status changed to ${status}`);
        
        // Show success message
        showSuccess(`Task marked as ${status}`);
    } catch (error) {
        console.error('Error updating task status:', error);
        showError('Failed to update task status');
    }
}

// Load timeline summary
async function loadTimelineSummary(caseId) {
    try {
        const response = await fetch(`/api/cases/${caseId}/timeline-summary`);
        const result = await response.json();
        
        if (result.status === 'success') {
            // Update the AI summary with timeline information
            const summaryElement = document.getElementById('case-ai-summary');
            if (summaryElement) {
                summaryElement.innerHTML = `
                    <div class="mb-2">${summaryElement.textContent}</div>
                    <div class="border-top pt-2">
                        <strong>Timeline Summary:</strong><br>
                        ${result.data.timeline_summary}
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error loading timeline summary:', error);
    }
}

// Load case threads/communications (from tasks since threads are in-memory only)
async function loadCaseCommunication(caseId) {
    try {
        // Load case data which now includes threads
        const response = await fetch(`/api/cases/${caseId}`);
        const result = await response.json();
        
        const container = document.getElementById('case-communication-list');
        
        if (result.status === 'success') {
            const caseData = result.data.case;
            const threads = caseData.threads || [];
            
            if (threads.length > 0) {
                // Sort by timestamp (newest first for email thread view)
                threads.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
                
                container.innerHTML = threads.map((thread, index) => {
                    const isInbound = thread.direction === 'Inbound';
                    const badgeClass = isInbound ? 'bg-primary' : 'bg-success';
                    const borderClass = isInbound ? 'border-primary' : 'border-success';
                    const alignClass = isInbound ? '' : 'ms-4';
                    const icon = isInbound ? 'envelope' : 'reply';
                    
                    return `
                        <div class="border-start ${borderClass} border-3 ps-3 pb-4 mb-3 ${alignClass} communication-item">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <div class="flex-grow-1">
                                    <h6 class="mb-1">
                                        <span class="badge ${badgeClass} me-2">
                                            <i class="bi bi-${icon}"></i> ${thread.direction}
                                        </span>
                                        ${thread.subject}
                                    </h6>
                                    <small class="text-muted">
                                        <i class="bi bi-person"></i> ${thread.sender_name}
                                        <span class="text-muted">&lt;${thread.sender_email}&gt;</span>
                                    </small>
                                </div>
                                <small class="text-muted text-end">
                                    <i class="bi bi-clock"></i> ${formatDate(thread.timestamp)}
                                </small>
                            </div>
                            <div class="email-body bg-light p-3 rounded position-relative">
                                <div class="email-preview" id="thread-preview-${thread.thread_id}" 
                                     style="white-space: pre-wrap; max-height: 100px; overflow: hidden; position: relative;">
                                    ${thread.body}
                                </div>
                                <div class="email-full" id="thread-full-${thread.thread_id}" 
                                     style="white-space: pre-wrap; display: none;">
                                    ${thread.body}
                                </div>
                                <button class="btn btn-sm btn-link p-0 mt-2 text-decoration-none" 
                                        onclick="toggleThreadExpand('${thread.thread_id}')">
                                    <i class="bi bi-chevron-down" id="thread-icon-${thread.thread_id}"></i> 
                                    <span id="thread-text-${thread.thread_id}">Show more</span>
                                </button>
                            </div>
                        </div>
                    `;
                }).join('');
            } else {
                container.innerHTML = `
                    <div class="alert alert-info text-center">
                        <i class="bi bi-info-circle" style="font-size: 2rem;"></i>
                        <p class="mb-0 mt-2">No email communications found for this case yet.</p>
                    </div>
                `;
            }
        } else {
            container.innerHTML = '<p class="text-danger text-center">Failed to load communications.</p>';
        }
    } catch (error) {
        console.error('Error loading communication:', error);
        const container = document.getElementById('case-communication-list');
        if (container) {
            container.innerHTML = '<p class="text-muted">Error loading communication history.</p>';
        }
    }
}

// Toggle thread expansion
function toggleThreadExpand(threadId) {
    const preview = document.getElementById(`thread-preview-${threadId}`);
    const full = document.getElementById(`thread-full-${threadId}`);
    const icon = document.getElementById(`thread-icon-${threadId}`);
    const text = document.getElementById(`thread-text-${threadId}`);
    
    if (preview && full && icon && text) {
        if (preview.style.display === 'none') {
            // Show preview, hide full
            preview.style.display = 'block';
            full.style.display = 'none';
            icon.className = 'bi bi-chevron-down';
            text.textContent = 'Show more';
        } else {
            // Show full, hide preview
            preview.style.display = 'none';
            full.style.display = 'block';
            icon.className = 'bi bi-chevron-up';
            text.textContent = 'Show less';
        }
    }
}

// Add new task to case (placeholder)
function addNewTask() {
    // TODO: Implement task creation modal
    alert('Task creation functionality coming soon!');
}

// Show email response modal
function showEmailResponseModal() {
    if (!currentCaseId) {
        showError('No case selected');
        return;
    }
    
    // Find current case data
    const currentCase = allCases.find(c => c.case_id === currentCaseId);
    if (!currentCase) {
        showError('Case not found');
        return;
    }
    
    const customerInfo = currentCase.customer_info || {};
    
    // Populate email form
    document.getElementById('response-to').value = customerInfo.email || '';
    document.getElementById('response-subject').value = `Re: ${currentCase.case_title || 'Case Update'}`;
    
    // Pre-fill message with case context
    const includeDetails = document.getElementById('include-case-details').checked;
    let message = '';
    
    if (includeDetails) {
        message = `Dear ${customerInfo.name || 'Valued Customer'},

Thank you for contacting HandyConnect regarding your case ${currentCase.case_number}.

`;
    }
    
    document.getElementById('response-message').value = message;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('emailResponseModal'));
    modal.show();
}

// Send email response
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
        
        if (!to || !subject || !message) {
            showError('Please fill in all required fields');
            return;
        }
        
        // Find current case data
        const currentCase = allCases.find(c => c.case_id === currentCaseId);
        if (!currentCase) {
            showError('Case not found');
            return;
        }
        
        // Add case details to signature if requested
        if (includeDetails) {
            const customerInfo = currentCase.customer_info || {};
            message += `

---
Case Details:
Case Number: ${currentCase.case_number}
Property: ${customerInfo.property_number || 'N/A'}, Block: ${customerInfo.block_number || 'N/A'}
Status: ${currentCase.status}
Priority: ${currentCase.priority}

Best regards,
HandyConnect Support Team`;
        }
        
        const emailData = {
            to: to,
            subject: subject,
            message: message,
            case_id: currentCaseId
        };
        
        const response = await fetch('/api/cases/send-response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(emailData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('emailResponseModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('emailResponseForm').reset();
            
            showSuccess('Email response sent successfully');
            
            // Refresh threads to show the new communication
            loadCaseThreads(currentCaseId);
        } else {
            showError('Failed to send email response: ' + result.message);
        }
    } catch (error) {
        console.error('Error sending email response:', error);
        showError('Failed to send email response. Please try again.');
    }
}

// Edit customer information

function editCustomerInfo() {
    // Get current case ID from the modal
    const caseNumberElement = document.getElementById('case-modal-number');
    if (!caseNumberElement) return;
    
    // Find current case data
    const caseNumber = caseNumberElement.textContent;
    const currentCase = allCases.find(c => c.case_number === caseNumber);
    
    if (!currentCase) {
        showError('Case not found');
        return;
    }
    
    currentCaseId = currentCase.case_id;
    const customerInfo = currentCase.customer_info || {};
    
    // Populate edit form
    document.getElementById('edit-customer-name').value = customerInfo.name || '';
    document.getElementById('edit-customer-email').value = customerInfo.email || '';
    document.getElementById('edit-property-number').value = customerInfo.property_number || '';
    document.getElementById('edit-block-number').value = customerInfo.block_number || '';
    document.getElementById('edit-property-address').value = customerInfo.property_address || '';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('editCustomerModal'));
    modal.show();
}

// Update case status
async function updateCaseStatus() {
    const statusSelect = document.getElementById('case-status-select');
    const newStatus = statusSelect.value;
    
    if (!currentCaseId || !newStatus) {
        return;
    }
    
    try {
        const response = await fetch(`/api/cases/${currentCaseId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                status: newStatus,
                updated_at: new Date().toISOString()
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Update the case in the allCases array
            const caseIndex = allCases.findIndex(c => c.case_id === currentCaseId);
            if (caseIndex !== -1) {
                allCases[caseIndex].status = newStatus;
                allCases[caseIndex].updated_at = new Date().toISOString();
            }
            
            // Update the cases table if visible
            renderCases();
        } else {
            showError('Failed to update case status: ' + result.message);
            // Revert the dropdown to the previous value
            statusSelect.value = allCases.find(c => c.case_id === currentCaseId)?.status || 'New';
        }
    } catch (error) {
        console.error('Error updating case status:', error);
        showError('Failed to update case status. Please try again.');
        // Revert the dropdown to the previous value
        const caseIndex = allCases.findIndex(c => c.case_id === currentCaseId);
        statusSelect.value = allCases[caseIndex]?.status || 'New';
    }
}

// Save customer information
async function saveCustomerInfo() {
    if (!currentCaseId) {
        showError('No case selected');
        return;
    }
    
    try {
        const formData = {
            customer_info: {
                name: document.getElementById('edit-customer-name').value,
                email: document.getElementById('edit-customer-email').value,
                property_number: document.getElementById('edit-property-number').value,
                block_number: document.getElementById('edit-block-number').value,
                property_address: document.getElementById('edit-property-address').value
            }
        };
        
        const response = await fetch(`/api/cases/${currentCaseId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            console.log('✅ Customer information updated successfully');
            
            // Close modal first
            const modal = bootstrap.Modal.getInstance(document.getElementById('editCustomerModal'));
            if (modal) {
                modal.hide();
            }
            
            // Update the case in the current list
            const caseIndex = allCases.findIndex(c => c.case_id === currentCaseId);
            if (caseIndex !== -1) {
                allCases[caseIndex].customer_info = formData.customer_info;
                // Refresh the case detail view
                try {
                    populateCaseInfo(allCases[caseIndex]);
                } catch (e) {
                    console.warn('Could not refresh case info display:', e);
                    // Still consider it a success since save worked
                }
            }
        } else {
            showError('Failed to update customer information: ' + (result.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error updating customer info:', error);
        // Only show error if response was not ok
        if (error.message && !error.message.includes('JSON')) {
            showError('Failed to update customer information. Please try again.');
        } else {
            // Might be a JSON parsing error after successful save
            console.log('Update may have succeeded despite error');
        }
    }
}

// Set up case detail tab event listeners
function setupCaseDetailTabs(caseId) {
    // Add event listeners for tab switching
    const tabs = document.querySelectorAll('#caseDetailTabs button[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (event) {
            const targetTab = event.target.getAttribute('data-bs-target');
            
            // Load data when specific tabs are shown
            if (targetTab === '#tasks') {
                loadCaseTasks(caseId);
            } else if (targetTab === '#threads') {
                loadCaseThreads(caseId);
            } else if (targetTab === '#timeline') {
                loadCaseTimeline(caseId);
            }
        });
    });
}

// Update case priority
async function updateCasePriority() {
    const prioritySelect = document.getElementById('case-priority-select');
    const newPriority = prioritySelect.value;
    
    if (!currentCaseId || !newPriority) {
        return;
    }
    
    try {
        const response = await fetch(`/api/cases/${currentCaseId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                priority: newPriority,
                updated_at: new Date().toISOString()
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Update the case in the current list
            const caseIndex = allCases.findIndex(c => c.case_id === currentCaseId);
            if (caseIndex !== -1) {
                allCases[caseIndex].priority = newPriority;
                renderCases();
            }
        } else {
            showError('Failed to update case priority: ' + result.message);
        }
    } catch (error) {
        console.error('Error updating case priority:', error);
        showError('Failed to update case priority: ' + error.message);
    }
}

// Update case type
async function updateCaseType() {
    const typeSelect = document.getElementById('case-type-select');
    const newType = typeSelect.value;
    
    if (!currentCaseId || !newType) {
        return;
    }
    
    try {
        const response = await fetch(`/api/cases/${currentCaseId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                case_type: newType,
                updated_at: new Date().toISOString()
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Update the case in the current list
            const caseIndex = allCases.findIndex(c => c.case_id === currentCaseId);
            if (caseIndex !== -1) {
                allCases[caseIndex].case_type = newType;
                renderCases();
            }
        } else {
            showError('Failed to update case type: ' + result.message);
        }
    } catch (error) {
        console.error('Error updating case type:', error);
        showError('Failed to update case type: ' + error.message);
    }
}

// Edit case description
function editCaseDescription() {
    document.getElementById('case-detail-description-display').style.display = 'none';
    document.getElementById('case-detail-description-edit').style.display = 'block';
    
    // Populate the textarea with current description
    const currentDescription = document.getElementById('case-detail-description').textContent;
    document.getElementById('case-description-edit').value = currentDescription === 'No description available.' ? '' : currentDescription;
}

// Cancel editing description
function cancelEditDescription() {
    document.getElementById('case-detail-description-display').style.display = 'block';
    document.getElementById('case-detail-description-edit').style.display = 'none';
}

// Save case description
async function saveCaseDescription() {
    const description = document.getElementById('case-description-edit').value;
    
    if (!currentCaseId) {
        return;
    }
    
    try {
        const response = await fetch(`/api/cases/${currentCaseId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                description: description,
                updated_at: new Date().toISOString()
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Update the display
            document.getElementById('case-detail-description').textContent = description || 'No description available.';
            document.getElementById('case-detail-description-display').style.display = 'block';
            document.getElementById('case-detail-description-edit').style.display = 'none';
            
            // Update the case in the current list
            const caseIndex = allCases.findIndex(c => c.case_id === currentCaseId);
            if (caseIndex !== -1) {
                allCases[caseIndex].description = description;
                renderCases();
            }
        } else {
            showError('Failed to update case description: ' + result.message);
        }
    } catch (error) {
        console.error('Error updating case description:', error);
        showError('Failed to update case description: ' + error.message);
    }
}

// Task Assignment Functions
let currentAssignmentTaskId = null;

// Show task assignment modal
function showTaskAssignmentModal(taskId, taskSubject) {
    currentAssignmentTaskId = taskId;
    
    // Populate task subject
    document.getElementById('assign-task-subject').textContent = taskSubject;
    
    // Clear form fields
    document.getElementById('assign-name').value = '';
    document.getElementById('assign-email').value = '';
    document.getElementById('assign-role').value = '';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('taskAssignmentModal'));
    modal.show();
}

// Submit task assignment
async function submitTaskAssignment() {
    if (!currentCaseId || !currentAssignmentTaskId) {
        showError('Missing case or task information');
        return;
    }
    
    // Get form values
    const assigneeName = document.getElementById('assign-name').value.trim();
    const assigneeEmail = document.getElementById('assign-email').value.trim();
    const assigneeRole = document.getElementById('assign-role').value;
    
    // Validate
    if (!assigneeName || !assigneeEmail || !assigneeRole) {
        showError('Please fill in all required fields');
        return;
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(assigneeEmail)) {
        showError('Please enter a valid email address');
        return;
    }
    
    try {
        // Show loading state
        const submitBtn = event.target;
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Assigning...';
        
        // Make API call
        const response = await fetch(`/api/cases/${currentCaseId}/tasks/${currentAssignmentTaskId}/assign`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                assignee_name: assigneeName,
                assignee_email: assigneeEmail,
                assignee_role: assigneeRole
            })
        });
        
        const result = await response.json();
        
        // Restore button
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        
        if (result.status === 'success') {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('taskAssignmentModal'));
            modal.hide();
            
            // Show success message
            showSuccess(`Task assigned to ${assigneeName} successfully! Notification email sent.`);
            
            // Reload tasks to show updated assignment
            await loadCaseTasks(currentCaseId);
            
            // Reload communication to show assignment email
            await loadCaseCommunication(currentCaseId);
            
        } else {
            showError('Failed to assign task: ' + result.message);
        }
        
    } catch (error) {
        console.error('Error assigning task:', error);
        showError('Failed to assign task: ' + error.message);
    }
}

// Email Response Functions
function showEmailResponseModal() {
    if (!currentCaseId) {
        showError('No case selected');
        return;
    }
    
    // Get case details
    const caseData = allCases.find(c => c.case_id === currentCaseId);
    if (!caseData) {
        showError('Case not found');
        return;
    }
    
    // Populate form
    document.getElementById('response-to').value = caseData.customer_info.email;
    document.getElementById('response-subject').value = `Re: ${caseData.case_title}`;
    document.getElementById('response-message').value = '';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('emailResponseModal'));
    modal.show();
}

async function sendEmailResponse() {
    const to = document.getElementById('response-to').value;
    const subject = document.getElementById('response-subject').value;
    const message = document.getElementById('response-message').value;
    const includeDetails = document.getElementById('include-case-details').checked;
    
    if (!to || !subject || !message) {
        showError('Please fill in all required fields');
        return;
    }
    
    try {
        const submitBtn = document.querySelector('#emailResponseModal .btn-primary');
        const originalText = submitBtn.innerHTML;
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Sending...';
        
        const response = await fetch(`/api/cases/${currentCaseId}/send-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                to: to,
                subject: subject,
                message: message,
                include_case_details: includeDetails
            })
        });
        
        const result = await response.json();
        
        // Restore button
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        
        if (result.status === 'success') {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('emailResponseModal'));
            modal.hide();
            
            // Show success message
            showSuccess('Email sent successfully!');
            
            // Reload communication to show sent email
            await loadCaseCommunication(currentCaseId);
            
        } else {
            showError('Failed to send email: ' + result.message);
        }
        
    } catch (error) {
        console.error('Error sending email:', error);
        showError('Failed to send email: ' + error.message);
    }
}

// Task Management Functions
function addNewTask() {
    if (!currentCaseId) {
        showError('No case selected');
        return;
    }
    
    // Show task creation modal
    showTaskCreationModal();
}

function showTaskCreationModal() {
    // Create modal HTML if it doesn't exist
    let modal = document.getElementById('taskCreationModal');
    if (!modal) {
        modal = createTaskCreationModal();
        document.body.appendChild(modal);
    }
    
    // Reset form
    document.getElementById('task-subject').value = '';
    document.getElementById('task-description').value = '';
    document.getElementById('task-priority').value = 'Medium';
    document.getElementById('task-assignee-name').value = '';
    document.getElementById('task-assignee-email').value = '';
    document.getElementById('task-assignee-role').value = 'Internal';
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

function createTaskCreationModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'taskCreationModal';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-labelledby', 'taskCreationModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="taskCreationModalLabel">
                        <i class="bi bi-plus-circle"></i> Add New Task
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="taskCreationForm">
                        <div class="mb-3">
                            <label for="task-subject" class="form-label">Task Subject *</label>
                            <input type="text" class="form-control" id="task-subject" required placeholder="Enter task subject">
                        </div>
                        <div class="mb-3">
                            <label for="task-description" class="form-label">Description</label>
                            <textarea class="form-control" id="task-description" rows="3" placeholder="Enter task description"></textarea>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="task-priority" class="form-label">Priority</label>
                                    <select class="form-select" id="task-priority">
                                        <option value="Low">Low</option>
                                        <option value="Medium" selected>Medium</option>
                                        <option value="High">High</option>
                                        <option value="Urgent">Urgent</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="task-assignee-role" class="form-label">Assignee Type</label>
                                    <select class="form-select" id="task-assignee-role" onchange="toggleAssigneeFields()">
                                        <option value="Internal">Internal Team</option>
                                        <option value="External">External Contractor</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="row" id="assignee-fields">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="task-assignee-name" class="form-label">Assignee Name</label>
                                    <input type="text" class="form-control" id="task-assignee-name" placeholder="Enter assignee name">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="task-assignee-email" class="form-label">Assignee Email</label>
                                    <input type="email" class="form-control" id="task-assignee-email" placeholder="Enter assignee email">
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="submitTaskCreation()">
                        <i class="bi bi-plus"></i> Create Task
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return modal;
}

function toggleAssigneeFields() {
    const role = document.getElementById('task-assignee-role').value;
    const fields = document.getElementById('assignee-fields');
    
    if (role === 'Internal') {
        fields.style.display = 'none';
    } else {
        fields.style.display = 'block';
    }
}

async function submitTaskCreation() {
    const subject = document.getElementById('task-subject').value;
    const description = document.getElementById('task-description').value;
    const priority = document.getElementById('task-priority').value;
    const assigneeName = document.getElementById('task-assignee-name').value;
    const assigneeEmail = document.getElementById('task-assignee-email').value;
    const assigneeRole = document.getElementById('task-assignee-role').value;
    
    if (!subject) {
        showError('Please enter a task subject');
        return;
    }
    
    try {
        const submitBtn = document.querySelector('#taskCreationModal .btn-primary');
        const originalText = submitBtn.innerHTML;
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Creating...';
        
        const taskData = {
            subject: subject,
            description: description,
            priority: priority,
            assigned_to: assigneeName || null,
            assigned_email: assigneeEmail || null,
            assigned_role: assigneeRole
        };
        
        const response = await fetch(`/api/cases/${currentCaseId}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData)
        });
        
        const result = await response.json();
        
        // Restore button
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        
        if (result.status === 'success') {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('taskCreationModal'));
            modal.hide();
            
            // Show success message
            showSuccess('Task created successfully!');
            
            // Reload tasks
            await loadCaseTasks(currentCaseId);
            
            // If external assignee, show assignment notification
            if (assigneeRole === 'External' && assigneeEmail) {
                showSuccess(`Task assigned to ${assigneeName} (${assigneeEmail}). Notification email sent.`);
            }
            
        } else {
            showError('Failed to create task: ' + result.message);
        }
        
    } catch (error) {
        console.error('Error creating task:', error);
        showError('Failed to create task: ' + error.message);
    }
}
