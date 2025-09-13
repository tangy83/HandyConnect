// HandyConnect JavaScript functionality

// Global variables
let currentTasks = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadTasks();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Status change handlers
    document.querySelectorAll('.status-select').forEach(select => {
        select.addEventListener('change', function() {
            updateTaskStatus(this.dataset.taskId, this.value);
        });
    });

    // Filter handlers
    const statusFilter = document.getElementById('status-filter');
    const priorityFilter = document.getElementById('priority-filter');
    const categoryFilter = document.getElementById('category-filter');
    const searchInput = document.getElementById('search-input');

    if (statusFilter) statusFilter.addEventListener('change', filterTasks);
    if (priorityFilter) priorityFilter.addEventListener('change', filterTasks);
    if (categoryFilter) categoryFilter.addEventListener('change', filterTasks);
    if (searchInput) searchInput.addEventListener('input', filterTasks);
}

// Load tasks from API
async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        if (response.ok) {
            currentTasks = await response.json();
            updateTasksDisplay();
            updateStatistics();
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
        showNotification('Error loading tasks', 'error');
    }
}

// Poll for new emails
async function pollEmails() {
    const button = event.target;
    const originalText = button.innerHTML;
    
    // Show loading state
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Polling...';
    button.disabled = true;

    try {
        const response = await fetch('/api/poll-emails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            showNotification(result.message, 'success');
            await loadTasks(); // Reload tasks
        } else {
            const error = await response.json();
            showNotification(error.error || 'Error polling emails', 'error');
        }
    } catch (error) {
        console.error('Error polling emails:', error);
        showNotification('Error polling emails', 'error');
    } finally {
        // Restore button state
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Update task status
async function updateTaskStatus(taskId, status) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: status })
        });

        if (response.ok) {
            const updatedTask = await response.json();
            showNotification(`Task status updated to ${status}`, 'success');
            
            // Update local task data
            const taskIndex = currentTasks.findIndex(t => t.id == taskId);
            if (taskIndex !== -1) {
                currentTasks[taskIndex] = updatedTask;
                updateStatistics();
                
                // Highlight the updated row
                const row = document.querySelector(`tr[data-task-id="${taskId}"]`);
                if (row) {
                    row.classList.add('task-updated');
                    setTimeout(() => row.classList.remove('task-updated'), 1000);
                }
            }
        } else {
            showNotification('Error updating task status', 'error');
        }
    } catch (error) {
        console.error('Error updating task status:', error);
        showNotification('Error updating task status', 'error');
    }
}

// View task details
async function viewTask(taskId) {
    const task = currentTasks.find(t => t.id == taskId);
    if (!task) return;

    const modalBody = document.getElementById('taskModalBody');
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Subject</h6>
                <p>${task.subject}</p>
            </div>
            <div class="col-md-6">
                <h6>Sender</h6>
                <p>${task.sender} (${task.sender_email})</p>
            </div>
        </div>
        <div class="row">
            <div class="col-md-4">
                <h6>Category</h6>
                <p><span class="badge bg-secondary">${task.category}</span></p>
            </div>
            <div class="col-md-4">
                <h6>Priority</h6>
                <p><span class="badge bg-${getPriorityColor(task.priority)}">${task.priority}</span></p>
            </div>
            <div class="col-md-4">
                <h6>Status</h6>
                <p><span class="badge bg-${getStatusColor(task.status)}">${task.status}</span></p>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <h6>Summary</h6>
                <p class="task-detail-content">${task.summary || 'No summary available'}</p>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <h6>Original Email Content</h6>
                <div class="task-detail-content">${task.content}</div>
            </div>
        </div>
        <div class="row mt-3">
            <div class="col-12">
                <h6>Notes</h6>
                <textarea class="form-control task-notes" id="taskNotes" rows="4" placeholder="Add notes...">${task.notes || ''}</textarea>
                <button class="btn btn-primary mt-2" onclick="updateTaskNotes(${task.id})">Save Notes</button>
            </div>
        </div>
    `;

    const modal = new bootstrap.Modal(document.getElementById('taskModal'));
    modal.show();
}

// Update task notes
async function updateTaskNotes(taskId) {
    const notes = document.getElementById('taskNotes').value;
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ notes: notes })
        });

        if (response.ok) {
            showNotification('Notes updated successfully', 'success');
            await loadTasks(); // Reload tasks
        } else {
            showNotification('Error updating notes', 'error');
        }
    } catch (error) {
        console.error('Error updating notes:', error);
        showNotification('Error updating notes', 'error');
    }
}

// Delete task
async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showNotification('Task deleted successfully', 'success');
            await loadTasks(); // Reload tasks
        } else {
            showNotification('Error deleting task', 'error');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showNotification('Error deleting task', 'error');
    }
}

// Filter tasks
function filterTasks() {
    const statusFilter = document.getElementById('status-filter')?.value || '';
    const priorityFilter = document.getElementById('priority-filter')?.value || '';
    const categoryFilter = document.getElementById('category-filter')?.value || '';
    const searchTerm = document.getElementById('search-input')?.value.toLowerCase() || '';

    const rows = document.querySelectorAll('#tasks-table-body tr');
    
    rows.forEach(row => {
        const status = row.dataset.status;
        const priority = row.dataset.priority;
        const category = row.dataset.category;
        const text = row.textContent.toLowerCase();

        const statusMatch = !statusFilter || status === statusFilter;
        const priorityMatch = !priorityFilter || priority === priorityFilter;
        const categoryMatch = !categoryFilter || category === categoryFilter;
        const searchMatch = !searchTerm || text.includes(searchTerm);

        if (statusMatch && priorityMatch && categoryMatch && searchMatch) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Update statistics
function updateStatistics() {
    const totalElement = document.getElementById('total-tasks');
    const newElement = document.getElementById('new-tasks');
    const inProgressElement = document.getElementById('in-progress-tasks');
    const completedElement = document.getElementById('completed-tasks');

    if (totalElement) totalElement.textContent = currentTasks.length;
    if (newElement) newElement.textContent = currentTasks.filter(t => t.status === 'New').length;
    if (inProgressElement) inProgressElement.textContent = currentTasks.filter(t => t.status === 'In Progress').length;
    if (completedElement) completedElement.textContent = currentTasks.filter(t => t.status === 'Completed').length;
}

// Helper functions
function getPriorityColor(priority) {
    switch (priority) {
        case 'Urgent': return 'danger';
        case 'High': return 'warning';
        case 'Medium': return 'info';
        case 'Low': return 'secondary';
        default: return 'secondary';
    }
}

function getStatusColor(status) {
    switch (status) {
        case 'New': return 'warning';
        case 'In Progress': return 'info';
        case 'Completed': return 'success';
        case 'On Hold': return 'danger';
        default: return 'secondary';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());

    // Create notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible notification polling-indicator`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Update tasks display (for future use with real-time updates)
function updateTasksDisplay() {
    // This function can be extended to update the table dynamically
    // For now, it's a placeholder for future enhancements
}

// Auto-refresh tasks every 5 minutes
setInterval(loadTasks, 5 * 60 * 1000);
