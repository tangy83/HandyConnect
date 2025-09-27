// HandyConnect Frontend JavaScript - Enhanced Version
// Advanced functionality for the task management interface

// Global variables for pagination and state management
let currentPage = 1;
let itemsPerPage = 10;
let totalTasks = 0;
let filteredTasks = [];
let selectedTasks = new Set();
let currentTaskId = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('HandyConnect frontend loaded');
    
    // Initialize all frontend functionality
    initializeTaskManagement();
    initializeFilters();
    initializeRealTimeUpdates();
    initializeModals();
    initializePagination();
    initializeBulkOperations();
});

// ==================== TASK MANAGEMENT ====================

function initializeTaskManagement() {
    console.log('Task management initialized');
    
    // Add event listeners for status changes
    document.querySelectorAll('.status-select').forEach(select => {
        select.addEventListener('change', function() {
            updateTaskStatus(this.dataset.taskId, this.value);
        });
    });
    
    // Add event listeners for action buttons
    document.querySelectorAll('[onclick*="viewTask"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const taskId = this.getAttribute('onclick').match(/\d+/)[0];
            viewTask(taskId);
        });
    });
    
    document.querySelectorAll('[onclick*="deleteTask"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const taskId = this.getAttribute('onclick').match(/\d+/)[0];
            deleteTask(taskId);
        });
    });
}

// ==================== FILTERS AND SEARCH ====================

function initializeFilters() {
    // Filter event listeners
    const filters = ['status-filter', 'priority-filter', 'category-filter', 'search-input'];
    filters.forEach(filterId => {
        const element = document.getElementById(filterId);
        if (element) {
            element.addEventListener('change', filterTasks);
            element.addEventListener('input', filterTasks);
        }
    });
}

function filterTasks() {
    const statusFilter = document.getElementById('status-filter')?.value || '';
    const priorityFilter = document.getElementById('priority-filter')?.value || '';
    const categoryFilter = document.getElementById('category-filter')?.value || '';
    const searchFilter = document.getElementById('search-input')?.value.toLowerCase() || '';
    
    const rows = document.querySelectorAll('#tasks-table-body tr');
    
    rows.forEach(row => {
        const status = row.dataset.status || '';
        const priority = row.dataset.priority || '';
        const category = row.dataset.category || '';
        const text = row.textContent.toLowerCase();
        
        const statusMatch = !statusFilter || status === statusFilter;
        const priorityMatch = !priorityFilter || priority === priorityFilter;
        const categoryMatch = !categoryFilter || category === categoryFilter;
        const searchMatch = !searchFilter || text.includes(searchFilter);
        
        if (statusMatch && priorityMatch && categoryMatch && searchMatch) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
    
    updateTaskCounts();
}

function updateTaskCounts() {
    const visibleRows = document.querySelectorAll('#tasks-table-body tr[style=""]');
    const totalVisible = visibleRows.length;
    
    // Update visible task count
    const totalElement = document.getElementById('total-tasks');
    if (totalElement) {
        totalElement.textContent = totalVisible;
    }
}

// ==================== TASK OPERATIONS ====================

async function updateTaskStatus(taskId, newStatus) {
    try {
        showLoadingIndicator();
        
        const result = await updateTask(taskId, { status: newStatus });
        
        if (result && result.status === 'success') {
            // Update the row with animation
            const row = document.querySelector(`tr[data-task-id="${taskId}"]`);
            if (row) {
                row.classList.add('task-updated');
                row.dataset.status = newStatus;
                
                // Update status badge
                const statusSelect = row.querySelector('.status-select');
                if (statusSelect) {
                    statusSelect.value = newStatus;
                }
                
                // Remove animation class after animation completes
                setTimeout(() => {
                    row.classList.remove('task-updated');
                }, 1000);
            }
            
            showNotification('Task status updated successfully', 'success');
            updateTaskCounts();
        } else {
            showNotification('Failed to update task status', 'error');
        }
    } catch (error) {
        console.error('Error updating task status:', error);
        showNotification('Error updating task status', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

async function viewTask(taskId) {
    try {
        currentTaskId = taskId;
        
        // Show modal first
        const modal = new bootstrap.Modal(document.getElementById('taskModal'));
        modal.show();
        
        // Show loading state in the task-info section only
        const taskInfo = document.getElementById('task-info');
        if (taskInfo) {
            taskInfo.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
        }
        
        const response = await fetch(`/api/tasks/${taskId}`);
        const result = await response.json();
        
        if (result && result.status === 'success') {
            // Wait a bit for the modal to be fully rendered
            setTimeout(() => {
                displayTaskDetails(result.data);
            }, 100);
        } else {
            showNotification('Failed to load task details', 'error');
            if (taskInfo) {
                taskInfo.innerHTML = '<div class="alert alert-danger">Failed to load task details</div>';
            }
        }
    } catch (error) {
        console.error('Error loading task:', error);
        showNotification('Error loading task details', 'error');
        const taskInfo = document.getElementById('task-info');
        if (taskInfo) {
            taskInfo.innerHTML = '<div class="alert alert-danger">Error loading task details</div>';
        }
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        showLoadingIndicator();
        
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (result && result.status === 'success') {
            // Remove the row from the table
            const row = document.querySelector(`tr[data-task-id="${taskId}"]`);
            if (row) {
                row.remove();
            }
            
            showNotification('Task deleted successfully', 'success');
            updateTaskCounts();
        } else {
            showNotification('Failed to delete task', 'error');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showNotification('Error deleting task', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

// ==================== EMAIL POLLING ====================

async function pollEmails() {
    try {
        showLoadingIndicator();
        showNotification('Polling for new emails...', 'info');
        
        const response = await fetch('/api/poll-emails', {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result && result.status === 'success') {
            const processedCount = result.data.processed_count || 0;
            if (processedCount > 0) {
                showNotification(`Processed ${processedCount} new emails`, 'success');
                // Reload the page to show new tasks
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                showNotification('No new emails found', 'info');
            }
        } else {
            showNotification('Failed to poll emails', 'error');
        }
    } catch (error) {
        console.error('Error polling emails:', error);
        showNotification('Error polling emails', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

// ==================== MODAL FUNCTIONALITY ====================

function initializeModals() {
    // Initialize Bootstrap modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        new bootstrap.Modal(modal);
    });
}

function displayTaskModal(task) {
    const modalBody = document.getElementById('taskModalBody');
    if (!modalBody) return;
    
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-8">
                <h6 class="text-muted">Subject</h6>
                <p class="mb-3">${task.subject || 'N/A'}</p>
                
                <h6 class="text-muted">Summary</h6>
                <p class="mb-3">${task.summary || 'No summary available'}</p>
                
                <h6 class="text-muted">Content</h6>
                <div class="task-detail-content">
                    ${task.content || 'No content available'}
                </div>
            </div>
            <div class="col-md-4">
                <h6 class="text-muted">Details</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>ID:</strong></td>
                        <td>${task.id}</td>
                    </tr>
                    <tr>
                        <td><strong>Sender:</strong></td>
                        <td>${task.sender || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Email:</strong></td>
                        <td>${task.sender_email || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Category:</strong></td>
                        <td><span class="badge bg-secondary">${task.category || 'N/A'}</span></td>
                    </tr>
                    <tr>
                        <td><strong>Priority:</strong></td>
                        <td><span class="badge ${getPriorityBadgeClass(task.priority)}">${task.priority || 'N/A'}</span></td>
                    </tr>
                    <tr>
                        <td><strong>Status:</strong></td>
                        <td><span class="badge ${getStatusBadgeClass(task.status)}">${task.status || 'N/A'}</span></td>
                    </tr>
                    <tr>
                        <td><strong>Created:</strong></td>
                        <td>${formatDate(task.created_at)}</td>
                    </tr>
                    <tr>
                        <td><strong>Updated:</strong></td>
                        <td>${formatDate(task.updated_at)}</td>
                    </tr>
                </table>
                
                <h6 class="text-muted mt-3">Notes</h6>
                <div class="task-notes">
                    ${task.notes || 'No notes available'}
                </div>
                
                <div class="mt-3">
                    <button class="btn btn-primary btn-sm" onclick="editTask(${task.id})">
                        <i class="bi bi-pencil"></i> Edit Task
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('taskModal'));
    modal.show();
}

// ==================== UTILITY FUNCTIONS ====================

function getPriorityBadgeClass(priority) {
    switch (priority) {
        case 'Urgent': return 'bg-danger';
        case 'High': return 'bg-warning';
        case 'Medium': return 'bg-info';
        case 'Low': return 'bg-secondary';
        default: return 'bg-secondary';
    }
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'New': return 'bg-warning';
        case 'In Progress': return 'bg-info';
        case 'Completed': return 'bg-success';
        case 'On Hold': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// ==================== NOTIFICATIONS ====================

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show notification`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// ==================== LOADING INDICATORS ====================

function showLoadingIndicator() {
    // Create or show loading indicator
    let indicator = document.getElementById('loading-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'loading-indicator';
        indicator.className = 'spinner-border text-primary polling-indicator';
        indicator.innerHTML = '<span class="visually-hidden">Loading...</span>';
        document.body.appendChild(indicator);
    }
    indicator.style.display = 'block';
}

function hideLoadingIndicator() {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

// ==================== REAL-TIME UPDATES ====================

function initializeRealTimeUpdates() {
    // Set up periodic updates for task statistics
    setInterval(updateTaskStatistics, 30000); // Update every 30 seconds
}

async function updateTaskStatistics() {
    try {
        const response = await fetch('/api/tasks/stats');
        const result = await response.json();
        
        if (result && result.status === 'success') {
            const stats = result.data;
            
            // Update statistics cards
            updateStatCard('total-tasks', stats.total || 0);
            updateStatCard('new-tasks', stats.new || 0);
            updateStatCard('in-progress-tasks', stats.in_progress || 0);
            updateStatCard('completed-tasks', stats.completed || 0);
        }
    } catch (error) {
        console.error('Error updating statistics:', error);
    }
}

function updateStatCard(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

// ==================== API HELPER FUNCTIONS ====================

async function fetchTasks() {
    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching tasks:', error);
        return null;
    }
}

async function updateTask(taskId, updates) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updates)
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error updating task:', error);
        return null;
    }
}

// ==================== TASK EDITING ====================

function editTask(taskId) {
    // This would open an edit modal or form
    // For now, we'll just show a placeholder
    showNotification('Edit functionality coming soon!', 'info');
}

// ==================== SYSTEM FUNCTIONS ====================

async function showSystemStatus() {
    try {
        showLoadingIndicator();
        
        const response = await fetch('/api/health');
        const result = await response.json();
        
        if (result && result.status === 'success') {
            const status = result.data;
            const statusHtml = `
                <div class="modal fade" id="systemStatusModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">System Status</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Application Status</h6>
                                        <p><strong>Status:</strong> <span class="badge bg-success">${status.status}</span></p>
                                        <p><strong>Version:</strong> ${status.version || '1.0.0'}</p>
                                        <p><strong>Uptime:</strong> ${status.uptime || 'N/A'}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Services</h6>
                                        <p><strong>Email Service:</strong> <span class="badge ${status.email_service ? 'bg-success' : 'bg-danger'}">${status.email_service ? 'Active' : 'Inactive'}</span></p>
                                        <p><strong>LLM Service:</strong> <span class="badge ${status.llm_service ? 'bg-success' : 'bg-danger'}">${status.llm_service ? 'Active' : 'Inactive'}</span></p>
                                        <p><strong>Task Service:</strong> <span class="badge ${status.task_service ? 'bg-success' : 'bg-danger'}">${status.task_service ? 'Active' : 'Inactive'}</span></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            const existingModal = document.getElementById('systemStatusModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to body
            document.body.insertAdjacentHTML('beforeend', statusHtml);
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('systemStatusModal'));
            modal.show();
        } else {
            showNotification('Failed to load system status', 'error');
        }
    } catch (error) {
        console.error('Error loading system status:', error);
        showNotification('Error loading system status', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

async function showConfiguration() {
    try {
        showLoadingIndicator();
        
        const response = await fetch('/api/test/configuration');
        const result = await response.json();
        
        if (result && result.status === 'success') {
            const config = result.data;
            const configHtml = `
                <div class="modal fade" id="configModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">System Configuration</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Microsoft Graph API</h6>
                                        <p><strong>Client ID:</strong> ${config.client_id ? 'Configured' : 'Not Set'}</p>
                                        <p><strong>Tenant ID:</strong> ${config.tenant_id ? 'Configured' : 'Not Set'}</p>
                                        <p><strong>Scope:</strong> ${config.scope || 'N/A'}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>OpenAI Configuration</h6>
                                        <p><strong>API Key:</strong> ${config.openai_api_key ? 'Configured' : 'Not Set'}</p>
                                        <p><strong>Model:</strong> ${config.openai_model || 'N/A'}</p>
                                    </div>
                                </div>
                                <div class="row mt-3">
                                    <div class="col-md-6">
                                        <h6>Flask Configuration</h6>
                                        <p><strong>Environment:</strong> ${config.flask_env || 'N/A'}</p>
                                        <p><strong>Secret Key:</strong> ${config.secret_key ? 'Configured' : 'Not Set'}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Data Storage</h6>
                                        <p><strong>Data Directory:</strong> ${config.data_dir || 'N/A'}</p>
                                        <p><strong>Tasks File:</strong> ${config.tasks_file || 'N/A'}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            const existingModal = document.getElementById('configModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to body
            document.body.insertAdjacentHTML('beforeend', configHtml);
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('configModal'));
            modal.show();
        } else {
            showNotification('Failed to load configuration', 'error');
        }
    } catch (error) {
        console.error('Error loading configuration:', error);
        showNotification('Error loading configuration', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

async function exportTasks() {
    try {
        showLoadingIndicator();
        
        const response = await fetch('/api/tasks');
        const result = await response.json();
        
        if (result && result.status === 'success') {
            const tasks = result.data;
            const csvContent = convertTasksToCSV(tasks);
            
            // Create and download CSV file
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `handyconnect-tasks-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification('Tasks exported successfully', 'success');
        } else {
            showNotification('Failed to export tasks', 'error');
        }
    } catch (error) {
        console.error('Error exporting tasks:', error);
        showNotification('Error exporting tasks', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

function convertTasksToCSV(tasks) {
    const headers = ['ID', 'Subject', 'Sender', 'Email', 'Category', 'Priority', 'Status', 'Created', 'Updated'];
    const csvRows = [headers.join(',')];
    
    tasks.forEach(task => {
        const row = [
            task.id || '',
            `"${(task.subject || '').replace(/"/g, '""')}"`,
            `"${(task.sender || '').replace(/"/g, '""')}"`,
            `"${(task.sender_email || '').replace(/"/g, '""')}"`,
            `"${(task.category || '').replace(/"/g, '""')}"`,
            `"${(task.priority || '').replace(/"/g, '""')}"`,
            `"${(task.status || '').replace(/"/g, '""')}"`,
            `"${(task.created_at || '').replace(/"/g, '""')}"`,
            `"${(task.updated_at || '').replace(/"/g, '""')}"`
        ];
        csvRows.push(row.join(','));
    });
    
    return csvRows.join('\n');
}

// ==================== BULK OPERATIONS ====================

function toggleAllTasks() {
    const selectAll = document.getElementById('select-all-tasks') || document.getElementById('select-all-tasks-header');
    const checkboxes = document.querySelectorAll('.task-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
    });
    
    updateSelectedCount();
}

function updateSelectedCount() {
    const selectedCheckboxes = document.querySelectorAll('.task-checkbox:checked');
    const count = selectedCheckboxes.length;
    const countElement = document.getElementById('selected-count');
    
    if (countElement) {
        countElement.textContent = `${count} task${count !== 1 ? 's' : ''} selected`;
    }
    
    // Update select all checkbox state
    const selectAll = document.getElementById('select-all-tasks') || document.getElementById('select-all-tasks-header');
    if (selectAll) {
        const totalCheckboxes = document.querySelectorAll('.task-checkbox');
        selectAll.checked = count === totalCheckboxes.length && totalCheckboxes.length > 0;
        selectAll.indeterminate = count > 0 && count < totalCheckboxes.length;
    }
}

async function bulkUpdateStatus() {
    const selectedTasks = getSelectedTasks();
    
    if (selectedTasks.length === 0) {
        showNotification('Please select tasks to update', 'warning');
        return;
    }
    
    const newStatus = prompt('Enter new status (New, In Progress, Completed, On Hold):');
    if (!newStatus) return;
    
    const validStatuses = ['New', 'In Progress', 'Completed', 'On Hold'];
    if (!validStatuses.includes(newStatus)) {
        showNotification('Invalid status. Please use: New, In Progress, Completed, or On Hold', 'error');
        return;
    }
    
    try {
        showLoadingIndicator();
        
        const updatePromises = selectedTasks.map(taskId => 
            updateTask(taskId, { status: newStatus })
        );
        
        const results = await Promise.all(updatePromises);
        const successCount = results.filter(result => result && result.status === 'success').length;
        
        if (successCount === selectedTasks.length) {
            showNotification(`Successfully updated ${successCount} tasks`, 'success');
            // Reload the page to show updated tasks
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showNotification(`Updated ${successCount} of ${selectedTasks.length} tasks`, 'warning');
        }
    } catch (error) {
        console.error('Error in bulk update:', error);
        showNotification('Error updating tasks', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

async function exportSelectedTasks() {
    const selectedTasks = getSelectedTasks();
    
    if (selectedTasks.length === 0) {
        showNotification('Please select tasks to export', 'warning');
        return;
    }
    
    try {
        showLoadingIndicator();
        
        const response = await fetch('/api/tasks');
        const result = await response.json();
        
        if (result && result.status === 'success') {
            const allTasks = result.data;
            const selectedTaskData = allTasks.filter(task => selectedTasks.includes(task.id.toString()));
            
            const csvContent = convertTasksToCSV(selectedTaskData);
            
            // Create and download CSV file
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `handyconnect-selected-tasks-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification(`Exported ${selectedTasks.length} tasks successfully`, 'success');
        } else {
            showNotification('Failed to export tasks', 'error');
        }
    } catch (error) {
        console.error('Error exporting tasks:', error);
        showNotification('Error exporting tasks', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

async function deleteSelectedTasks() {
    const selectedTasks = getSelectedTasks();
    
    if (selectedTasks.length === 0) {
        showNotification('Please select tasks to delete', 'warning');
        return;
    }
    
    if (!confirm(`Are you sure you want to delete ${selectedTasks.length} tasks? This action cannot be undone.`)) {
        return;
    }
    
    try {
        showLoadingIndicator();
        
        const deletePromises = selectedTasks.map(taskId => 
            fetch(`/api/tasks/${taskId}`, { method: 'DELETE' })
        );
        
        const results = await Promise.all(deletePromises);
        const successCount = results.filter(response => response.ok).length;
        
        if (successCount === selectedTasks.length) {
            showNotification(`Successfully deleted ${successCount} tasks`, 'success');
            // Reload the page to show updated tasks
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showNotification(`Deleted ${successCount} of ${selectedTasks.length} tasks`, 'warning');
        }
    } catch (error) {
        console.error('Error in bulk delete:', error);
        showNotification('Error deleting tasks', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

function getSelectedTasks() {
    const selectedCheckboxes = document.querySelectorAll('.task-checkbox:checked');
    return Array.from(selectedCheckboxes).map(checkbox => checkbox.value);
}

// ==================== SORTING ====================

function sortTasks(sortBy) {
    const tbody = document.getElementById('tasks-table-body');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        let aValue, bValue;
        
        switch (sortBy) {
            case 'created_at':
                aValue = new Date(a.dataset.createdAt || 0);
                bValue = new Date(b.dataset.createdAt || 0);
                return bValue - aValue; // Newest first
            case 'priority':
                const priorityOrder = { 'Urgent': 4, 'High': 3, 'Medium': 2, 'Low': 1 };
                aValue = priorityOrder[a.dataset.priority] || 0;
                bValue = priorityOrder[b.dataset.priority] || 0;
                return bValue - aValue; // Highest priority first
            case 'status':
                aValue = a.dataset.status || '';
                bValue = b.dataset.status || '';
                return aValue.localeCompare(bValue);
            default:
                return 0;
        }
    });
    
    // Clear tbody and append sorted rows
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
    
    showNotification(`Tasks sorted by ${sortBy}`, 'info');
}

// ==================== PAGINATION ====================

function initializePagination() {
    console.log('Pagination initialized');
    totalTasks = document.querySelectorAll('#tasks-table-body tr').length;
    updatePaginationDisplay();
}

function changePage(direction) {
    const totalPages = Math.ceil(totalTasks / itemsPerPage);
    
    if (direction === 'first') {
        currentPage = 1;
    } else if (direction === 'last') {
        currentPage = totalPages;
    } else if (direction === 'prev' && currentPage > 1) {
        currentPage--;
    } else if (direction === 'next' && currentPage < totalPages) {
        currentPage++;
    } else if (typeof direction === 'number') {
        currentPage = direction;
    }
    
    updatePaginationDisplay();
    renderCurrentPage();
}

function updatePaginationDisplay() {
    const totalPages = Math.ceil(totalTasks / itemsPerPage);
    const startItem = (currentPage - 1) * itemsPerPage + 1;
    const endItem = Math.min(currentPage * itemsPerPage, totalTasks);
    
    // Update pagination info
    document.getElementById('showing-start').textContent = startItem;
    document.getElementById('showing-end').textContent = endItem;
    document.getElementById('total-tasks-count').textContent = totalTasks;
    
    // Update pagination controls
    const paginationControls = document.getElementById('pagination-controls');
    if (paginationControls) {
        updatePaginationButtons(totalPages);
    }
}

function updatePaginationButtons(totalPages) {
    const paginationControls = document.getElementById('pagination-controls');
    if (!paginationControls) return;
    
    let paginationHTML = `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage('first')">
                <i class="bi bi-chevron-double-left"></i>
            </a>
        </li>
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage('prev')">
                <i class="bi bi-chevron-left"></i>
            </a>
        </li>
    `;
    
    // Add page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>
        `;
    }
    
    paginationHTML += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage('next')">
                <i class="bi bi-chevron-right"></i>
            </a>
        </li>
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage('last')">
                <i class="bi bi-chevron-double-right"></i>
            </a>
        </li>
    `;
    
    paginationControls.innerHTML = paginationHTML;
}

function renderCurrentPage() {
    const tbody = document.getElementById('tasks-table-body');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    
    // Hide all rows
    rows.forEach(row => row.style.display = 'none');
    
    // Show only rows for current page
    for (let i = startIndex; i < Math.min(endIndex, rows.length); i++) {
        if (rows[i]) {
            rows[i].style.display = '';
        }
    }
}

// ==================== BULK OPERATIONS ====================

function initializeBulkOperations() {
    console.log('Bulk operations initialized');
    
    // Add event listener for bulk operation selection
    const bulkOperationSelect = document.getElementById('bulk-operation');
    if (bulkOperationSelect) {
        bulkOperationSelect.addEventListener('change', updateBulkOperationUI);
    }
}

function updateBulkOperationUI() {
    const operation = document.getElementById('bulk-operation').value;
    const container = document.getElementById('bulk-value-container');
    
    let html = '';
    
    switch (operation) {
        case 'status':
            html = `
                <label class="form-label">New Status</label>
                <select class="form-select" id="bulk-value">
                    <option value="New">New</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                    <option value="On Hold">On Hold</option>
                </select>
            `;
            break;
        case 'priority':
            html = `
                <label class="form-label">New Priority</label>
                <select class="form-select" id="bulk-value">
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Urgent">Urgent</option>
                </select>
            `;
            break;
        case 'category':
            html = `
                <label class="form-label">New Category</label>
                <select class="form-select" id="bulk-value">
                    <option value="Technical Issue">Technical Issue</option>
                    <option value="Billing Question">Billing Question</option>
                    <option value="Feature Request">Feature Request</option>
                    <option value="Complaint">Complaint</option>
                    <option value="General Inquiry">General Inquiry</option>
                    <option value="Account Issue">Account Issue</option>
                </select>
            `;
            break;
        case 'assign':
            html = `
                <label class="form-label">Assign To</label>
                <input type="text" class="form-control" id="bulk-value" placeholder="Enter assignee name">
            `;
            break;
        case 'delete':
            html = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    This will permanently delete the selected tasks. This action cannot be undone.
                </div>
            `;
            break;
    }
    
    container.innerHTML = html;
}

function bulkUpdateStatus() {
    const selected = getSelectedTasks();
    if (selected.length === 0) {
        showNotification('Please select tasks to update', 'warning');
        return;
    }
    
    document.getElementById('bulk-operation').value = 'status';
    updateBulkOperationUI();
    document.getElementById('bulk-count').textContent = selected.length;
    
    const modal = new bootstrap.Modal(document.getElementById('bulkModal'));
    modal.show();
}

function bulkUpdatePriority() {
    const selected = getSelectedTasks();
    if (selected.length === 0) {
        showNotification('Please select tasks to update', 'warning');
        return;
    }
    
    document.getElementById('bulk-operation').value = 'priority';
    updateBulkOperationUI();
    document.getElementById('bulk-count').textContent = selected.length;
    
    const modal = new bootstrap.Modal(document.getElementById('bulkModal'));
    modal.show();
}

function executeBulkOperation() {
    const operation = document.getElementById('bulk-operation').value;
    const value = document.getElementById('bulk-value') ? document.getElementById('bulk-value').value : null;
    const selected = getSelectedTasks();
    
    if (selected.length === 0) {
        showNotification('No tasks selected', 'warning');
        return;
    }
    
    if (operation !== 'delete' && !value) {
        showNotification('Please provide a value for the operation', 'warning');
        return;
    }
    
    showLoadingIndicator();
    
    const promises = selected.map(taskId => {
        if (operation === 'delete') {
            return fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
        } else {
            const updateData = {};
            updateData[operation] = value;
            return fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updateData)
            });
        }
    });
    
    Promise.all(promises)
        .then(results => {
            const successCount = results.filter(response => response.ok).length;
            showNotification(`Successfully updated ${successCount} of ${selected.length} tasks`, 'success');
            
            // Close modal and refresh
            const modal = bootstrap.Modal.getInstance(document.getElementById('bulkModal'));
            modal.hide();
            
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        })
        .catch(error => {
            console.error('Bulk operation error:', error);
            showNotification('Error performing bulk operation', 'error');
        })
        .finally(() => {
            hideLoadingIndicator();
        });
}

// ==================== ENHANCED TASK MANAGEMENT ====================

// Removed duplicate viewTask function - using the async version above

// Removed loadTaskDetails function - functionality moved to viewTask

function displayTaskDetails(task, retryCount = 0) {
    console.log('displayTaskDetails called with task:', task, 'retry:', retryCount);
    
    try {
        // Check if elements exist
        const modalTaskId = document.getElementById('modal-task-id');
        const taskInfo = document.getElementById('task-info');
        const taskContent = document.getElementById('task-content');
        const taskNotes = document.getElementById('task-notes');
        const threadInfo = document.getElementById('thread-info');
        
        console.log('Elements found:', {
            modalTaskId: !!modalTaskId,
            taskInfo: !!taskInfo,
            taskContent: !!taskContent,
            taskNotes: !!taskNotes,
            threadInfo: !!threadInfo
        });
        
        // If elements are not found, wait a bit and try again (max 5 retries)
        if ((!modalTaskId || !taskInfo || !taskContent || !taskNotes || !threadInfo) && retryCount < 5) {
            console.log('Some elements not found, retrying in 200ms... (attempt', retryCount + 1, 'of 5)');
            setTimeout(() => {
                displayTaskDetails(task, retryCount + 1);
            }, 200);
            return;
        }
        
        // If still not found after retries, show error
        if (!modalTaskId || !taskInfo || !taskContent || !taskNotes || !threadInfo) {
            throw new Error('Modal elements not found after 5 retries');
        }
        
        modalTaskId.textContent = `#${task.id}`;
        
        // Task info
        taskInfo.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Subject</h6>
                <p>${task.subject || 'N/A'}</p>
                
                <h6>Sender</h6>
                <p>${task.sender || 'N/A'} <br><small class="text-muted">${task.sender_email || 'N/A'}</small></p>
                
                <h6>Summary</h6>
                <p>${task.summary || 'No summary available'}</p>
            </div>
            <div class="col-md-6">
                <h6>Created</h6>
                <p>${task.created_at ? new Date(task.created_at).toLocaleString() : 'N/A'}</p>
                
                <h6>Updated</h6>
                <p>${task.updated_at ? new Date(task.updated_at).toLocaleString() : 'N/A'}</p>
                
                <h6>Assigned To</h6>
                <p>${task.assigned_to || 'Unassigned'}</p>
            </div>
        </div>
    `;
    
    // Email content
    taskContent.innerHTML = `
        <div class="email-content">
            ${task.content ? task.content.replace(/\n/g, '<br>') : 'No content available'}
        </div>
    `;
    
    // Notes
    taskNotes.innerHTML = `
        ${task.notes ? `<div class="note-item">${task.notes.replace(/\n/g, '<br>')}</div>` : '<p class="text-muted">No notes yet</p>'}
    `;
    
    // Thread info
    if (task.thread_info) {
        threadInfo.innerHTML = `
            <div class="thread-details">
                <h6>Thread ID</h6>
                <p>${task.thread_info.thread_id || 'N/A'}</p>
                
                <h6>Thread Status</h6>
                <p><span class="badge bg-secondary">${task.thread_info.thread_status || 'N/A'}</span></p>
                
                <h6>Email Count</h6>
                <p>${task.thread_info.email_count || 0}</p>
            </div>
        `;
    }
    
    // Set form values
    const statusSelect = document.getElementById('modal-status-select');
    const prioritySelect = document.getElementById('modal-priority-select');
    const assignedToInput = document.getElementById('modal-assigned-to');
    const categorySelect = document.getElementById('modal-category-select');
    
    if (statusSelect) statusSelect.value = task.status || 'New';
    if (prioritySelect) prioritySelect.value = task.priority || 'Medium';
    if (assignedToInput) assignedToInput.value = task.assigned_to || '';
    if (categorySelect) categorySelect.value = task.category || 'General Inquiry';
    
    } catch (error) {
        console.error('Error in displayTaskDetails:', error);
        document.getElementById('taskModalBody').innerHTML = `
            <div class="alert alert-danger">
                <h5>Error loading task details</h5>
                <p>There was an error displaying the task information.</p>
                <small>Error: ${error.message}</small>
            </div>
        `;
    }
}

function saveTaskChanges() {
    if (!currentTaskId) return;
    
    const updateData = {
        status: document.getElementById('modal-status-select').value,
        priority: document.getElementById('modal-priority-select').value,
        assigned_to: document.getElementById('modal-assigned-to').value,
        category: document.getElementById('modal-category-select').value
    };
    
    showLoadingIndicator();
    
    fetch(`/api/tasks/${currentTaskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Task updated successfully', 'success');
            // Close modal and refresh
            const modal = bootstrap.Modal.getInstance(document.getElementById('taskModal'));
            modal.hide();
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification('Error updating task', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating task:', error);
        showNotification('Error updating task', 'error');
    })
    .finally(() => {
        hideLoadingIndicator();
    });
}

function addNote() {
    const noteText = document.getElementById('new-note').value.trim();
    if (!noteText || !currentTaskId) return;
    
    showLoadingIndicator();
    
    fetch(`/api/tasks/${currentTaskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes: noteText })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Note added successfully', 'success');
            document.getElementById('new-note').value = '';
            // Reload task details
            loadTaskDetails(currentTaskId);
        } else {
            showNotification('Error adding note', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding note:', error);
        showNotification('Error adding note', 'error');
    })
    .finally(() => {
        hideLoadingIndicator();
    });
}

function deleteTaskFromModal() {
    if (!currentTaskId) return;
    
    if (confirm('Are you sure you want to delete this task?')) {
        deleteTask(currentTaskId);
        const modal = bootstrap.Modal.getInstance(document.getElementById('taskModal'));
        modal.hide();
    }
}

// ==================== UTILITY FUNCTIONS ====================

function clearSelection() {
    selectedTasks.clear();
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    document.getElementById('select-all-tasks').checked = false;
    updateSelectedCount();
    document.getElementById('bulk-operations').style.display = 'none';
}

function updateSelectedCount() {
    const selected = getSelectedTasks();
    selectedTasks = new Set(selected);
    
    document.getElementById('selected-count').textContent = `${selected.length} tasks selected`;
    
    const bulkOperations = document.getElementById('bulk-operations');
    if (bulkOperations) {
        bulkOperations.style.display = selected.length > 0 ? 'block' : 'none';
    }
}

function toggleAllTasks() {
    const selectAll = document.getElementById('select-all-tasks');
    const checkboxes = document.querySelectorAll('.task-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
    });
    
    updateSelectedCount();
}
