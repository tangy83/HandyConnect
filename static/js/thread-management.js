// Thread Management JavaScript
// Advanced functionality for the thread management interface

// Global variables for thread management
let currentThreadPage = 1;
let threadsPerPage = 20; // Default page size
let totalThreads = 0;
let filteredThreads = [];
let selectedThreads = new Set();
let currentThreadId = null;
let currentThreadSort = { field: 'created_at', direction: 'desc' };

document.addEventListener('DOMContentLoaded', function() {
    console.log('Thread management frontend loaded');
    
    // Initialize all thread functionality
    initializeThreadManagement();
    initializeThreadFilters();
    initializeThreadPagination();
    initializeThreadBulkOperations();
    initializeThreadModals();
});

function initializeThreadManagement() {
    console.log('Initializing thread management...');
    
    // Load initial thread data
    loadThreads();
    
    // Set up real-time updates
    initializeRealTimeUpdates();
}

function initializeRealTimeUpdates() {
    console.log('Initializing real-time updates...');
    
    // Set up periodic refresh
    setInterval(loadThreads, 30000); // Update every 30 seconds
    
    // Set up WebSocket connection if available
    if (typeof WebSocket !== 'undefined') {
        initializeWebSocket();
    }
    
    // Set up visibility change listener for refresh when tab becomes active
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            console.log('Tab became visible, refreshing threads...');
            loadThreads();
        }
    });
    
    // Set up focus listener for refresh when window regains focus
    window.addEventListener('focus', function() {
        console.log('Window focused, refreshing threads...');
        loadThreads();
    });
}

function initializeWebSocket() {
    console.log('Initializing WebSocket connection...');
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/threads`;
    
    try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = function(event) {
            console.log('WebSocket connected for real-time thread updates');
            showNotification('Real-time updates enabled', 'success');
        };
        
        ws.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        ws.onclose = function(event) {
            console.log('WebSocket disconnected, falling back to polling');
            showNotification('Real-time updates disabled, using polling', 'warning');
            
            // Fallback to more frequent polling
            setInterval(loadThreads, 10000); // Update every 10 seconds
        };
        
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
            showNotification('Real-time connection error, using polling', 'warning');
        };
        
        // Store WebSocket reference for cleanup
        window.threadWebSocket = ws;
        
    } catch (error) {
        console.error('Failed to initialize WebSocket:', error);
        showNotification('WebSocket not available, using polling', 'info');
    }
}

function handleWebSocketMessage(data) {
    console.log('Received WebSocket message:', data);
    
    switch (data.type) {
        case 'thread_created':
            handleThreadCreated(data.thread);
            break;
        case 'thread_updated':
            handleThreadUpdated(data.thread);
            break;
        case 'thread_deleted':
            handleThreadDeleted(data.thread_id);
            break;
        case 'message_added':
            handleMessageAdded(data.thread_id, data.message);
            break;
        case 'thread_merged':
            handleThreadMerged(data.source_threads, data.target_thread);
            break;
        case 'bulk_update':
            handleBulkUpdate(data.threads);
            break;
        default:
            console.log('Unknown WebSocket message type:', data.type);
    }
}

function handleThreadCreated(thread) {
    console.log('New thread created:', thread);
    
    // Add to filtered threads if it matches current filters
    if (matchesCurrentFilters(thread)) {
        filteredThreads.unshift(thread);
        totalThreads = filteredThreads.length;
        renderCurrentThreadPage();
        updateThreadPaginationDisplay();
        updateThreadCount();
        
        // Show notification
        showNotification(`New thread created: ${thread.subject}`, 'info');
        
        // Highlight the new thread
        setTimeout(() => {
            const row = document.querySelector(`tr[data-thread-id="${thread.id}"]`);
            if (row) {
                row.classList.add('table-success');
                setTimeout(() => row.classList.remove('table-success'), 3000);
            }
        }, 100);
    }
}

function handleThreadUpdated(thread) {
    console.log('Thread updated:', thread);
    
    // Update in filtered threads
    const index = filteredThreads.findIndex(t => t.id === thread.id);
    if (index !== -1) {
        filteredThreads[index] = thread;
        
        // Update the table row
        const row = document.querySelector(`tr[data-thread-id="${thread.id}"]`);
        if (row) {
            updateThreadRow(row, thread);
            row.classList.add('table-warning');
            setTimeout(() => row.classList.remove('table-warning'), 2000);
        }
        
        // Show notification
        showNotification(`Thread updated: ${thread.subject}`, 'info');
    }
}

function handleThreadDeleted(threadId) {
    console.log('Thread deleted:', threadId);
    
    // Remove from filtered threads
    filteredThreads = filteredThreads.filter(t => t.id !== threadId);
    totalThreads = filteredThreads.length;
    
    // Remove from table
    const row = document.querySelector(`tr[data-thread-id="${threadId}"]`);
    if (row) {
        row.classList.add('table-danger');
        setTimeout(() => {
            row.remove();
            renderCurrentThreadPage();
            updateThreadPaginationDisplay();
            updateThreadCount();
        }, 1000);
    }
    
    // Show notification
    showNotification('Thread deleted', 'warning');
}

function handleMessageAdded(threadId, message) {
    console.log('Message added to thread:', threadId, message);
    
    // Update thread in filtered threads
    const thread = filteredThreads.find(t => t.id === threadId);
    if (thread) {
        if (!thread.messages) thread.messages = [];
        thread.messages.push(message);
        thread.message_count = (thread.message_count || 0) + 1;
        thread.last_activity = message.timestamp;
        
        // Update the table row
        const row = document.querySelector(`tr[data-thread-id="${threadId}"]`);
        if (row) {
            updateThreadRow(row, thread);
            row.classList.add('table-info');
            setTimeout(() => row.classList.remove('table-info'), 2000);
        }
        
        // Show notification
        showNotification(`New message in thread: ${thread.subject}`, 'info');
    }
}

function handleThreadMerged(sourceThreads, targetThread) {
    console.log('Threads merged:', sourceThreads, targetThread);
    
    // Remove source threads from filtered threads
    sourceThreads.forEach(sourceId => {
        filteredThreads = filteredThreads.filter(t => t.id !== sourceId);
    });
    
    // Update target thread
    const index = filteredThreads.findIndex(t => t.id === targetThread.id);
    if (index !== -1) {
        filteredThreads[index] = targetThread;
    } else {
        filteredThreads.unshift(targetThread);
    }
    
    totalThreads = filteredThreads.length;
    renderCurrentThreadPage();
    updateThreadPaginationDisplay();
    updateThreadCount();
    
    // Show notification
    showNotification(`${sourceThreads.length} threads merged into: ${targetThread.subject}`, 'success');
}

function handleBulkUpdate(threads) {
    console.log('Bulk update received:', threads);
    
    // Update all threads in filtered threads
    threads.forEach(updatedThread => {
        const index = filteredThreads.findIndex(t => t.id === updatedThread.id);
        if (index !== -1) {
            filteredThreads[index] = updatedThread;
        }
    });
    
    renderCurrentThreadPage();
    updateThreadPaginationDisplay();
    
    // Show notification
    showNotification(`${threads.length} threads updated`, 'info');
}

function matchesCurrentFilters(thread) {
    const statusFilter = document.getElementById('thread-status-filter')?.value || '';
    const priorityFilter = document.getElementById('thread-priority-filter')?.value || '';
    const categoryFilter = document.getElementById('thread-category-filter')?.value || '';
    const searchTerm = document.getElementById('thread-search-input')?.value.toLowerCase() || '';
    
    const matchesStatus = !statusFilter || thread.status === statusFilter;
    const matchesPriority = !priorityFilter || thread.priority === priorityFilter;
    const matchesCategory = !categoryFilter || thread.category === categoryFilter;
    const matchesSearch = !searchTerm || 
        (thread.subject && thread.subject.toLowerCase().includes(searchTerm)) ||
        (thread.participants && thread.participants.toLowerCase().includes(searchTerm));
    
    return matchesStatus && matchesPriority && matchesCategory && matchesSearch;
}

function updateThreadRow(row, thread) {
    // Update status
    const statusCell = row.querySelector('.thread-status');
    if (statusCell) {
        statusCell.innerHTML = `<span class="badge bg-${getStatusColor(thread.status)}">${thread.status || 'N/A'}</span>`;
    }
    
    // Update priority
    const priorityCell = row.querySelector('.thread-priority');
    if (priorityCell) {
        priorityCell.innerHTML = `<span class="badge bg-${getPriorityColor(thread.priority)}">${thread.priority || 'N/A'}</span>`;
    }
    
    // Update last activity
    const lastActivityCell = row.querySelector('.thread-last-activity');
    if (lastActivityCell) {
        lastActivityCell.textContent = thread.last_activity || 'N/A';
    }
    
    // Update message count
    const messageCountCell = row.querySelector('.thread-message-count');
    if (messageCountCell) {
        messageCountCell.textContent = thread.message_count || 0;
    }
    
    // Update data attributes
    row.dataset.status = thread.status || '';
    row.dataset.priority = thread.priority || '';
}

function initializeThreadFilters() {
    console.log('Initializing thread filters...');
    
    // Status filter
    const statusFilter = document.getElementById('thread-status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', filterThreads);
    }
    
    // Priority filter
    const priorityFilter = document.getElementById('thread-priority-filter');
    if (priorityFilter) {
        priorityFilter.addEventListener('change', filterThreads);
    }
    
    // Category filter
    const categoryFilter = document.getElementById('thread-category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterThreads);
    }
    
    // Search input
    const searchInput = document.getElementById('thread-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterThreads, 300));
    }
}

function initializeThreadPagination() {
    console.log('Initializing thread pagination...');
    
    // Calculate initial pagination
    updateThreadPaginationDisplay();
}

function initializeThreadBulkOperations() {
    console.log('Initializing thread bulk operations...');
    
    // Set up select all checkbox
    const selectAllCheckbox = document.getElementById('select-all-threads');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', toggleAllThreadSelection);
    }
}

function initializeThreadModals() {
    console.log('Initializing thread modals...');
    
    // Initialize Bootstrap modals
    const threadModal = new bootstrap.Modal(document.getElementById('threadModal'));
    const mergeModal = new bootstrap.Modal(document.getElementById('mergeModal'));
}

// ==================== PAGE SIZE MANAGEMENT ====================

// Change page size
function changePageSize() {
    const pageSizeSelect = document.getElementById('page-size-select');
    if (pageSizeSelect) {
        threadsPerPage = parseInt(pageSizeSelect.value);
        currentThreadPage = 1; // Reset to first page when changing page size
        renderCurrentThreadPage();
        updateThreadPaginationDisplay();
        showNotification(`Showing ${threadsPerPage} records per page`, 'info');
    }
}

// Handle row click for threads
function handleThreadRowClick(event, threadId) {
    // Don't trigger if clicking on interactive elements
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'SELECT' || event.target.tagName === 'BUTTON') {
        return;
    }
    
    // Prevent default if it was a link
    if (event.target.tagName === 'A') {
        event.preventDefault();
    }
    
    // Open thread detail (you may need to implement this function)
    console.log('Opening thread:', threadId);
    // viewThreadDetail(threadId); // Uncomment when implemented
}

// Thread data management
function loadThreads() {
    console.log('Loading threads...');
    
    fetch('/api/threads')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                filteredThreads = data.data.threads || [];
                totalThreads = filteredThreads.length;
                renderCurrentThreadPage();
                updateThreadPaginationDisplay();
                updateThreadCount();
            } else {
                console.error('Failed to load threads:', data.message);
                showNotification('Failed to load threads', 'error');
            }
        })
        .catch(error => {
            console.error('Error loading threads:', error);
            showNotification('Error loading threads', 'error');
        });
}

function filterThreads() {
    console.log('Filtering threads...');
    
    const statusFilter = document.getElementById('thread-status-filter').value;
    const priorityFilter = document.getElementById('thread-priority-filter').value;
    const categoryFilter = document.getElementById('thread-category-filter').value;
    const searchTerm = document.getElementById('thread-search-input').value.toLowerCase();
    
    // Get all threads from the table
    const allThreads = Array.from(document.querySelectorAll('tbody tr')).map(row => {
        const cells = row.querySelectorAll('td');
        return {
            id: row.dataset.threadId,
            subject: cells[1].textContent.trim(),
            participants: cells[2].textContent.trim(),
            status: cells[3].textContent.trim(),
            priority: cells[4].textContent.trim(),
            category: cells[5].textContent.trim(),
            lastActivity: cells[6].textContent.trim(),
            messageCount: cells[7].textContent.trim(),
            element: row
        };
    });
    
    // Apply filters
    filteredThreads = allThreads.filter(thread => {
        const matchesStatus = !statusFilter || thread.status === statusFilter;
        const matchesPriority = !priorityFilter || thread.priority === priorityFilter;
        const matchesCategory = !categoryFilter || thread.category === categoryFilter;
        const matchesSearch = !searchTerm || 
            thread.subject.toLowerCase().includes(searchTerm) ||
            thread.participants.toLowerCase().includes(searchTerm);
        
        return matchesStatus && matchesPriority && matchesCategory && matchesSearch;
    });
    
    totalThreads = filteredThreads.length;
    currentThreadPage = 1;
    renderCurrentThreadPage();
    updateThreadPaginationDisplay();
    updateThreadCount();
}

function renderCurrentThreadPage() {
    console.log(`Rendering thread page ${currentThreadPage}...`);
    
    const startIndex = (currentThreadPage - 1) * threadsPerPage;
    const endIndex = Math.min(startIndex + threadsPerPage, filteredThreads.length);
    const pageThreads = filteredThreads.slice(startIndex, endIndex);
    
    // Hide all thread rows
    document.querySelectorAll('tbody tr').forEach(row => {
        row.style.display = 'none';
    });
    
    // Show only current page threads
    pageThreads.forEach(thread => {
        if (thread.element) {
            thread.element.style.display = '';
        }
    });
    
    updateThreadPaginationButtons();
}

// Pagination functions
function changeThreadPage(page) {
    console.log(`Changing to thread page: ${page}`);
    
    if (page === 'first') {
        currentThreadPage = 1;
    } else if (page === 'prev') {
        currentThreadPage = Math.max(1, currentThreadPage - 1);
    } else if (page === 'next') {
        const maxPage = Math.ceil(totalThreads / threadsPerPage);
        currentThreadPage = Math.min(maxPage, currentThreadPage + 1);
    } else if (page === 'last') {
        currentThreadPage = Math.ceil(totalThreads / threadsPerPage);
    } else {
        currentThreadPage = parseInt(page);
    }
    
    renderCurrentThreadPage();
    updateThreadPaginationDisplay();
}

function updateThreadPaginationDisplay() {
    const startIndex = (currentThreadPage - 1) * threadsPerPage + 1;
    const endIndex = Math.min(currentThreadPage * threadsPerPage, totalThreads);
    
    document.getElementById('showing-thread-start').textContent = totalThreads > 0 ? startIndex : 0;
    document.getElementById('showing-thread-end').textContent = endIndex;
    document.getElementById('total-thread-count').textContent = totalThreads;
}

function updateThreadPaginationButtons() {
    const maxPage = Math.ceil(totalThreads / threadsPerPage);
    const paginationControls = document.getElementById('thread-pagination-controls');
    
    if (!paginationControls) return;
    
    // Clear existing page numbers
    const pageItems = paginationControls.querySelectorAll('.page-item:not(:first-child):not(:last-child)');
    pageItems.forEach(item => item.remove());
    
    // Add page numbers
    const startPage = Math.max(1, currentThreadPage - 2);
    const endPage = Math.min(maxPage, currentThreadPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageItem = document.createElement('li');
        pageItem.className = `page-item ${i === currentThreadPage ? 'active' : ''}`;
        pageItem.innerHTML = `<a class="page-link" href="#" onclick="changeThreadPage(${i})">${i}</a>`;
        
        // Insert before the next button
        const nextButton = paginationControls.querySelector('.page-item:last-child');
        paginationControls.insertBefore(pageItem, nextButton);
    }
    
    // Update navigation buttons
    const firstBtn = paginationControls.querySelector('.page-item:first-child');
    const prevBtn = paginationControls.querySelector('.page-item:nth-child(2)');
    const nextBtn = paginationControls.querySelector('.page-item:nth-last-child(2)');
    const lastBtn = paginationControls.querySelector('.page-item:last-child');
    
    if (firstBtn) firstBtn.className = `page-item ${currentThreadPage === 1 ? 'disabled' : ''}`;
    if (prevBtn) prevBtn.className = `page-item ${currentThreadPage === 1 ? 'disabled' : ''}`;
    if (nextBtn) nextBtn.className = `page-item ${currentThreadPage === maxPage ? 'disabled' : ''}`;
    if (lastBtn) lastBtn.className = `page-item ${currentThreadPage === maxPage ? 'disabled' : ''}`;
}

// Bulk operations
function initializeThreadBulkOperations() {
    console.log('Initializing thread bulk operations...');
    
    // Set up select all checkbox
    const selectAllCheckbox = document.getElementById('select-all-threads');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', toggleAllThreadSelection);
    }
}

function toggleAllThreadSelection() {
    const selectAllCheckbox = document.getElementById('select-all-threads');
    const isChecked = selectAllCheckbox.checked;
    
    // Get all visible thread checkboxes
    const visibleThreads = filteredThreads.slice(
        (currentThreadPage - 1) * threadsPerPage,
        currentThreadPage * threadsPerPage
    );
    
    visibleThreads.forEach(thread => {
        const checkbox = document.querySelector(`input[type="checkbox"][data-thread-id="${thread.id}"]`);
        if (checkbox) {
            checkbox.checked = isChecked;
            if (isChecked) {
                selectedThreads.add(thread.id);
            } else {
                selectedThreads.delete(thread.id);
            }
        }
    });
    
    updateThreadBulkOperationUI();
}

function toggleThreadSelection(threadId) {
    if (selectedThreads.has(threadId)) {
        selectedThreads.delete(threadId);
    } else {
        selectedThreads.add(threadId);
    }
    
    updateThreadBulkOperationUI();
    updateSelectAllCheckbox();
}

function updateSelectAllCheckbox() {
    const selectAllCheckbox = document.getElementById('select-all-threads');
    if (!selectAllCheckbox) return;
    
    const visibleThreads = filteredThreads.slice(
        (currentThreadPage - 1) * threadsPerPage,
        currentThreadPage * threadsPerPage
    );
    
    const selectedVisibleThreads = visibleThreads.filter(thread => selectedThreads.has(thread.id));
    
    selectAllCheckbox.checked = selectedVisibleThreads.length === visibleThreads.length && visibleThreads.length > 0;
    selectAllCheckbox.indeterminate = selectedVisibleThreads.length > 0 && selectedVisibleThreads.length < visibleThreads.length;
}

function updateThreadBulkOperationUI() {
    const bulkOperations = document.getElementById('thread-bulk-operations');
    const selectedCount = document.getElementById('selected-thread-count');
    
    if (selectedThreads.size > 0) {
        bulkOperations.style.display = 'block';
        selectedCount.textContent = selectedThreads.size;
    } else {
        bulkOperations.style.display = 'none';
    }
}

function clearThreadSelection() {
    selectedThreads.clear();
    document.querySelectorAll('input[type="checkbox"][data-thread-id]').forEach(checkbox => {
        checkbox.checked = false;
    });
    updateThreadBulkOperationUI();
    updateSelectAllCheckbox();
}

// Thread actions
function viewThread(threadId) {
    console.log(`Viewing thread: ${threadId}`);
    currentThreadId = threadId;
    
    // Load thread details
    fetch(`/api/threads/${threadId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayThreadDetails(data.data);
                const threadModal = new bootstrap.Modal(document.getElementById('threadModal'));
                threadModal.show();
            } else {
                showNotification('Failed to load thread details', 'error');
            }
        })
        .catch(error => {
            console.error('Error loading thread details:', error);
            showNotification('Error loading thread details', 'error');
        });
}

function displayThreadDetails(thread) {
    console.log('Displaying thread details:', thread);
    
    // Update modal title
    document.getElementById('modal-thread-id').textContent = `#${thread.id}`;
    
    // Update thread info
    const threadInfo = document.getElementById('thread-info');
    if (threadInfo) {
        threadInfo.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <strong>Subject:</strong> ${thread.subject || 'N/A'}<br>
                    <strong>Status:</strong> <span class="badge bg-${getStatusColor(thread.status)}">${thread.status || 'N/A'}</span><br>
                    <strong>Priority:</strong> <span class="badge bg-${getPriorityColor(thread.priority)}">${thread.priority || 'N/A'}</span>
                </div>
                <div class="col-md-6">
                    <strong>Category:</strong> ${thread.category || 'N/A'}<br>
                    <strong>Participants:</strong> ${thread.participants || 'N/A'}<br>
                    <strong>Last Activity:</strong> ${thread.last_activity || 'N/A'}
                </div>
            </div>
        `;
    }
    
    // Update thread content
    const threadContent = document.getElementById('thread-content');
    if (threadContent) {
        threadContent.innerHTML = `
            <div class="thread-messages">
                ${thread.messages ? thread.messages.map(msg => `
                    <div class="message-item mb-3 p-3 border rounded">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <strong>${msg.sender || 'Unknown'}</strong>
                            <small class="text-muted">${msg.timestamp || 'N/A'}</small>
                        </div>
                        <div class="message-body">${msg.content || 'No content'}</div>
                    </div>
                `).join('') : '<p class="text-muted">No messages available</p>'}
            </div>
        `;
    }
    
    // Update thread info
    const threadInfo = document.getElementById('thread-info');
    if (threadInfo) {
        threadInfo.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <strong>Message Count:</strong> ${thread.message_count || 0}<br>
                    <strong>Created:</strong> ${thread.created_at || 'N/A'}<br>
                    <strong>Updated:</strong> ${thread.updated_at || 'N/A'}
                </div>
                <div class="col-md-6">
                    <strong>Tags:</strong> ${thread.tags ? thread.tags.join(', ') : 'None'}<br>
                    <strong>Assigned To:</strong> ${thread.assigned_to || 'Unassigned'}<br>
                    <strong>Due Date:</strong> ${thread.due_date || 'None'}
                </div>
            </div>
        `;
    }
}

function getStatusColor(status) {
    const colors = {
        'Active': 'success',
        'Pending': 'warning',
        'Resolved': 'info',
        'Closed': 'secondary'
    };
    return colors[status] || 'secondary';
}

function getPriorityColor(priority) {
    const colors = {
        'Low': 'success',
        'Medium': 'warning',
        'High': 'danger',
        'Urgent': 'danger'
    };
    return colors[priority] || 'secondary';
}

// Bulk operations
function bulkUpdateThreadStatus() {
    if (selectedThreads.size === 0) {
        showNotification('Please select threads to update', 'warning');
        return;
    }
    
    const newStatus = prompt('Enter new status (Active, Pending, Resolved, Closed):');
    if (!newStatus) return;
    
    const validStatuses = ['Active', 'Pending', 'Resolved', 'Closed'];
    if (!validStatuses.includes(newStatus)) {
        showNotification('Invalid status. Please use: Active, Pending, Resolved, or Closed', 'error');
        return;
    }
    
    const threadIds = Array.from(selectedThreads);
    
    fetch('/api/threads/bulk-update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            thread_ids: threadIds,
            updates: { status: newStatus }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(`Updated ${threadIds.length} threads to ${newStatus}`, 'success');
            loadThreads();
            clearThreadSelection();
        } else {
            showNotification('Failed to update threads', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating threads:', error);
        showNotification('Error updating threads', 'error');
    });
}

function bulkUpdateThreadPriority() {
    if (selectedThreads.size === 0) {
        showNotification('Please select threads to update', 'warning');
        return;
    }
    
    const newPriority = prompt('Enter new priority (Low, Medium, High, Urgent):');
    if (!newPriority) return;
    
    const validPriorities = ['Low', 'Medium', 'High', 'Urgent'];
    if (!validPriorities.includes(newPriority)) {
        showNotification('Invalid priority. Please use: Low, Medium, High, or Urgent', 'error');
        return;
    }
    
    const threadIds = Array.from(selectedThreads);
    
    fetch('/api/threads/bulk-update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            thread_ids: threadIds,
            updates: { priority: newPriority }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(`Updated ${threadIds.length} threads to ${newPriority} priority`, 'success');
            loadThreads();
            clearThreadSelection();
        } else {
            showNotification('Failed to update threads', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating threads:', error);
        showNotification('Error updating threads', 'error');
    });
}

function bulkDeleteThreads() {
    if (selectedThreads.size === 0) {
        showNotification('Please select threads to delete', 'warning');
        return;
    }
    
    if (!confirm(`Are you sure you want to delete ${selectedThreads.size} threads? This action cannot be undone.`)) {
        return;
    }
    
    const threadIds = Array.from(selectedThreads);
    
    fetch('/api/threads/bulk-delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            thread_ids: threadIds
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(`Deleted ${threadIds.length} threads`, 'success');
            loadThreads();
            clearThreadSelection();
        } else {
            showNotification('Failed to delete threads', 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting threads:', error);
        showNotification('Error deleting threads', 'error');
    });
}

function mergeSelectedThreads() {
    if (selectedThreads.size < 2) {
        showNotification('Please select at least 2 threads to merge', 'warning');
        return;
    }
    
    const threadIds = Array.from(selectedThreads);
    
    // Show merge modal
    const mergeModal = new bootstrap.Modal(document.getElementById('mergeModal'));
    mergeModal.show();
    
    // Populate merge modal with selected threads
    const mergeList = document.getElementById('merge-thread-list');
    if (mergeList) {
        mergeList.innerHTML = threadIds.map(id => {
            const thread = filteredThreads.find(t => t.id === id);
            return `<li class="list-group-item">${thread ? thread.subject : `Thread ${id}`}</li>`;
        }).join('');
    }
    
    // Set up merge form
    const mergeForm = document.getElementById('merge-form');
    if (mergeForm) {
        mergeForm.onsubmit = function(e) {
            e.preventDefault();
            
            const targetThreadId = document.getElementById('target-thread-id').value;
            if (!targetThreadId) {
                showNotification('Please select a target thread', 'error');
                return;
            }
            
            performThreadMerge(threadIds, targetThreadId);
            mergeModal.hide();
        };
    }
}

function performThreadMerge(sourceThreadIds, targetThreadId) {
    console.log(`Merging threads ${sourceThreadIds.join(', ')} into ${targetThreadId}`);
    
    fetch('/api/threads/merge', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            source_thread_ids: sourceThreadIds,
            target_thread_id: targetThreadId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(`Successfully merged ${sourceThreadIds.length} threads`, 'success');
            loadThreads();
            clearThreadSelection();
        } else {
            showNotification('Failed to merge threads', 'error');
        }
    })
    .catch(error => {
        console.error('Error merging threads:', error);
        showNotification('Error merging threads', 'error');
    });
}

// Utility functions
function refreshThreads() {
    console.log('Refreshing threads...');
    loadThreads();
    showNotification('Threads refreshed', 'success');
}

function exportThreads() {
    console.log('Exporting threads...');
    
    const exportData = filteredThreads.map(thread => ({
        id: thread.id,
        subject: thread.subject,
        participants: thread.participants,
        status: thread.status,
        priority: thread.priority,
        category: thread.category,
        lastActivity: thread.lastActivity,
        messageCount: thread.messageCount
    }));
    
    const csv = convertToCSV(exportData);
    downloadCSV(csv, 'threads_export.csv');
    showNotification('Threads exported successfully', 'success');
}

function showThreadAnalytics() {
    console.log('Showing thread analytics...');
    
    // Calculate comprehensive analytics
    const analytics = calculateThreadAnalytics();
    
    // Display analytics in modal
    displayThreadAnalyticsModal(analytics);
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('threadAnalyticsModal'));
    modal.show();
}

function calculateThreadAnalytics() {
    console.log('Calculating thread analytics...');
    
    const analytics = {
        overview: {
            total: filteredThreads.length,
            active: 0,
            pending: 0,
            resolved: 0,
            closed: 0
        },
        byStatus: {},
        byPriority: {},
        byCategory: {},
        byAssignee: {},
        performance: {
            highPriorityCount: 0,
            urgentCount: 0,
            avgMessagesPerThread: 0
        }
    };
    
    let totalMessages = 0;
    
    filteredThreads.forEach(thread => {
        // Status breakdown
        const status = thread.status || 'Unknown';
        analytics.byStatus[status] = (analytics.byStatus[status] || 0) + 1;
        
        // Priority breakdown
        const priority = thread.priority || 'Unknown';
        analytics.byPriority[priority] = (analytics.byPriority[priority] || 0) + 1;
        
        // Category breakdown
        const category = thread.category || 'Unknown';
        analytics.byCategory[category] = (analytics.byCategory[category] || 0) + 1;
        
        // Assignee breakdown
        const assignee = thread.assigned_to || 'Unassigned';
        analytics.byAssignee[assignee] = (analytics.byAssignee[assignee] || 0) + 1;
        
        // Overview counts
        if (status === 'Active') analytics.overview.active++;
        else if (status === 'Pending') analytics.overview.pending++;
        else if (status === 'Resolved') analytics.overview.resolved++;
        else if (status === 'Closed') analytics.overview.closed++;
        
        // Performance metrics
        if (priority === 'High') analytics.performance.highPriorityCount++;
        if (priority === 'Urgent') analytics.performance.urgentCount++;
        
        // Message count
        const messageCount = thread.message_count || 0;
        totalMessages += messageCount;
    });
    
    // Calculate averages
    analytics.performance.avgMessagesPerThread = filteredThreads.length > 0 ? 
        Math.round(totalMessages / filteredThreads.length * 100) / 100 : 0;
    
    return analytics;
}

function displayThreadAnalyticsModal(analytics) {
    console.log('Displaying thread analytics modal:', analytics);
    
    const modalBody = document.getElementById('threadAnalyticsModalBody');
    if (!modalBody) return;
    
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-3 mb-3">
                <div class="card bg-primary text-white">
                    <div class="card-body">
                        <h5 class="card-title">Total Threads</h5>
                        <h2 class="card-text">${analytics.overview.total}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card bg-success text-white">
                    <div class="card-body">
                        <h5 class="card-title">Active</h5>
                        <h2 class="card-text">${analytics.overview.active}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card bg-warning text-white">
                    <div class="card-body">
                        <h5 class="card-title">Pending</h5>
                        <h2 class="card-text">${analytics.overview.pending}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card bg-info text-white">
                    <div class="card-body">
                        <h5 class="card-title">Resolved</h5>
                        <h2 class="card-text">${analytics.overview.resolved}</h2>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Status Distribution</h6>
                    </div>
                    <div class="card-body">
                        ${Object.entries(analytics.byStatus).map(([status, count]) => `
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>${status}</span>
                                <span class="badge bg-${getStatusColor(status)}">${count}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Priority Distribution</h6>
                    </div>
                    <div class="card-body">
                        ${Object.entries(analytics.byPriority).map(([priority, count]) => `
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>${priority}</span>
                                <span class="badge bg-${getPriorityColor(priority)}">${count}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Category Distribution</h6>
                    </div>
                    <div class="card-body">
                        ${Object.entries(analytics.byCategory).map(([category, count]) => `
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>${category}</span>
                                <span class="badge bg-secondary">${count}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Performance Metrics</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <div class="text-center">
                                    <h4 class="text-danger">${analytics.performance.urgentCount}</h4>
                                    <small class="text-muted">Urgent</small>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="text-center">
                                    <h4 class="text-warning">${analytics.performance.highPriorityCount}</h4>
                                    <small class="text-muted">High Priority</small>
                                </div>
                            </div>
                        </div>
                        <hr>
                        <div class="text-center">
                            <h4 class="text-info">${analytics.performance.avgMessagesPerThread}</h4>
                            <small class="text-muted">Avg Messages/Thread</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-12 text-center">
                <button class="btn btn-primary" onclick="exportAnalytics()">
                    <i class="bi bi-download"></i> Export Analytics
                </button>
                <button class="btn btn-secondary" onclick="refreshAnalytics()">
                    <i class="bi bi-arrow-clockwise"></i> Refresh
                </button>
            </div>
        </div>
    `;
}

function exportAnalytics() {
    console.log('Exporting analytics...');
    
    const analytics = calculateThreadAnalytics();
    const csvData = convertAnalyticsToCSV(analytics);
    downloadCSV(csvData, 'thread_analytics.csv');
    showNotification('Analytics exported successfully', 'success');
}

function refreshAnalytics() {
    console.log('Refreshing analytics...');
    showThreadAnalytics();
}

function convertAnalyticsToCSV(analytics) {
    const csvRows = [];
    
    // Overview
    csvRows.push(['Metric', 'Value']);
    csvRows.push(['Total Threads', analytics.overview.total]);
    csvRows.push(['Active Threads', analytics.overview.active]);
    csvRows.push(['Pending Threads', analytics.overview.pending]);
    csvRows.push(['Resolved Threads', analytics.overview.resolved]);
    csvRows.push(['Closed Threads', analytics.overview.closed]);
    csvRows.push([]);
    
    // Status Distribution
    csvRows.push(['Status', 'Count']);
    Object.entries(analytics.byStatus).forEach(([status, count]) => {
        csvRows.push([status, count]);
    });
    csvRows.push([]);
    
    // Priority Distribution
    csvRows.push(['Priority', 'Count']);
    Object.entries(analytics.byPriority).forEach(([priority, count]) => {
        csvRows.push([priority, count]);
    });
    csvRows.push([]);
    
    // Category Distribution
    csvRows.push(['Category', 'Count']);
    Object.entries(analytics.byCategory).forEach(([category, count]) => {
        csvRows.push([category, count]);
    });
    
    return csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
}

function convertToCSV(data) {
    if (data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];
    
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header] || '';
            return `"${value.toString().replace(/"/g, '""')}"`;
        });
        csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
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

function updateThreadCount() {
    const threadCount = document.getElementById('thread-count');
    if (threadCount) {
        threadCount.textContent = totalThreads;
    }
}

// Additional thread management functions
function editThread() {
    console.log('Editing thread:', currentThreadId);
    // Enable editing mode in the modal
    const modal = document.getElementById('threadModal');
    const editMode = modal.dataset.editMode === 'true';
    
    if (editMode) {
        // Save changes
        saveThreadChanges();
    } else {
        // Enter edit mode
        modal.dataset.editMode = 'true';
        document.querySelectorAll('#threadModal .form-control, #threadModal .form-select').forEach(input => {
            input.disabled = false;
        });
        document.querySelector('#threadModal .btn-outline-primary').innerHTML = '<i class="bi bi-check"></i> Save';
    }
}

function deleteThreadFromModal() {
    if (currentThreadId && confirm('Are you sure you want to delete this thread?')) {
        deleteThread(currentThreadId);
        const modal = bootstrap.Modal.getInstance(document.getElementById('threadModal'));
        modal.hide();
    }
}

function saveThreadChanges() {
    if (!currentThreadId) return;
    
    const updates = {
        status: document.getElementById('modal-status-select').value,
        priority: document.getElementById('modal-priority-select').value,
        category: document.getElementById('modal-category-select').value,
        assigned_to: document.getElementById('modal-assigned-to').value
    };
    
    fetch(`/api/threads/${currentThreadId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Thread updated successfully', 'success');
            loadThreads();
            
            // Exit edit mode
            const modal = document.getElementById('threadModal');
            modal.dataset.editMode = 'false';
            document.querySelectorAll('#threadModal .form-control, #threadModal .form-select').forEach(input => {
                input.disabled = true;
            });
            document.querySelector('#threadModal .btn-outline-primary').innerHTML = '<i class="bi bi-pencil"></i> Edit';
        } else {
            showNotification('Failed to update thread', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating thread:', error);
        showNotification('Error updating thread', 'error');
    });
}

function addMessage() {
    if (!currentThreadId) return;
    
    const messageContent = document.getElementById('new-message').value.trim();
    if (!messageContent) {
        showNotification('Please enter a message', 'warning');
        return;
    }
    
    fetch(`/api/threads/${currentThreadId}/messages`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content: messageContent
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Message added successfully', 'success');
            document.getElementById('new-message').value = '';
            // Refresh thread details
            viewThread(currentThreadId);
        } else {
            showNotification('Failed to add message', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding message:', error);
        showNotification('Error adding message', 'error');
    });
}

function confirmMerge() {
    const targetThreadId = document.getElementById('target-thread-id').value;
    const sourceThreadIds = Array.from(selectedThreads);
    
    if (!targetThreadId) {
        showNotification('Please select a target thread', 'error');
        return;
    }
    
    if (sourceThreadIds.length < 2) {
        showNotification('Please select at least 2 threads to merge', 'warning');
        return;
    }
    
    performThreadMerge(sourceThreadIds, targetThreadId);
}

// Enhanced display functions
function displayThreadDetails(thread) {
    console.log('Displaying thread details:', thread);
    
    // Update modal title
    document.getElementById('modal-thread-id').textContent = `#${thread.id}`;
    
    // Update thread info
    const threadInfo = document.getElementById('thread-info');
    if (threadInfo) {
        threadInfo.innerHTML = `
            <div class="row">
                <div class="col-12">
                    <strong>Subject:</strong> ${thread.subject || 'N/A'}<br>
                    <strong>Status:</strong> <span class="badge bg-${getStatusColor(thread.status)}">${thread.status || 'N/A'}</span><br>
                    <strong>Priority:</strong> <span class="badge bg-${getPriorityColor(thread.priority)}">${thread.priority || 'N/A'}</span><br>
                    <strong>Category:</strong> ${thread.category || 'N/A'}<br>
                    <strong>Assigned To:</strong> ${thread.assigned_to || 'Unassigned'}<br>
                    <strong>Created:</strong> ${thread.created_at || 'N/A'}<br>
                    <strong>Last Activity:</strong> ${thread.last_activity || 'N/A'}<br>
                    <strong>Message Count:</strong> ${thread.message_count || 0}
                </div>
            </div>
        `;
    }
    
    // Update thread messages
    const threadMessages = document.getElementById('thread-messages');
    if (threadMessages) {
        threadMessages.innerHTML = `
            <div class="thread-messages" style="max-height: 400px; overflow-y: auto;">
                ${thread.messages ? thread.messages.map(msg => `
                    <div class="message-item mb-3 p-3 border rounded">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <strong>${msg.sender || 'Unknown'}</strong>
                            <small class="text-muted">${msg.timestamp || 'N/A'}</small>
                        </div>
                        <div class="message-body">${msg.content || 'No content'}</div>
                    </div>
                `).join('') : '<p class="text-muted">No messages available</p>'}
            </div>
        `;
    }
    
    // Update participants
    const threadParticipants = document.getElementById('thread-participants');
    if (threadParticipants) {
        threadParticipants.innerHTML = `
            ${thread.participants ? thread.participants.map(participant => `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span>${participant.name || participant.email}</span>
                    <small class="text-muted">${participant.email || ''}</small>
                </div>
            `).join('') : '<p class="text-muted">No participants</p>'}
        `;
    }
    
    // Update form values
    document.getElementById('modal-status-select').value = thread.status || 'Active';
    document.getElementById('modal-priority-select').value = thread.priority || 'Medium';
    document.getElementById('modal-category-select').value = thread.category || 'General Inquiry';
    document.getElementById('modal-assigned-to').value = thread.assigned_to || '';
    
    // Disable form fields initially
    document.querySelectorAll('#threadModal .form-control, #threadModal .form-select').forEach(input => {
        input.disabled = true;
    });
}

// Utility functions for status and priority colors
function getStatusBadgeClass(status) {
    const classes = {
        'Active': 'bg-success',
        'Pending': 'bg-warning',
        'Resolved': 'bg-info',
        'Closed': 'bg-secondary'
    };
    return classes[status] || 'bg-secondary';
}

function getPriorityBadgeClass(priority) {
    const classes = {
        'Low': 'bg-success',
        'Medium': 'bg-warning',
        'High': 'bg-danger',
        'Urgent': 'bg-danger'
    };
    return classes[priority] || 'bg-secondary';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (error) {
        return dateString;
    }
}

// ==================== THREAD SORTING ====================

function sortThreads(sortBy) {
    // Toggle sort direction if same field is clicked
    if (currentThreadSort.field === sortBy) {
        currentThreadSort.direction = currentThreadSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentThreadSort.field = sortBy;
        currentThreadSort.direction = 'desc'; // Default to descending for new fields
    }
    
    // Update sort icons
    updateThreadSortIcons();
    
    // Sort the filtered threads
    filteredThreads.sort((a, b) => {
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
        if (currentThreadSort.direction === 'desc') {
            return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
        } else {
            return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        }
    });
    
    // Update thread count display
    document.getElementById('threads-count').textContent = filteredThreads.length;
    
    // Reset to first page and render
    currentThreadPage = 1;
    renderThreads();
    updateThreadPagination();
    
    // Show notification
    showNotification(`Threads sorted by ${sortBy} (${currentThreadSort.direction})`, 'info');
}

// Update thread sort icon states
function updateThreadSortIcons() {
    // Reset all icons
    document.getElementById('thread-sort-newest-icon').className = 'bi bi-sort-down';
    document.getElementById('thread-sort-priority-icon').className = 'bi bi-sort-up';
    document.getElementById('thread-sort-status-icon').className = 'bi bi-sort-alpha-down';
    
    // Update active sort icon
    const iconMap = {
        'created_at': 'thread-sort-newest-icon',
        'priority': 'thread-sort-priority-icon',
        'status': 'thread-sort-status-icon'
    };
    
    const activeIcon = document.getElementById(iconMap[currentThreadSort.field]);
    if (activeIcon) {
        const iconMap2 = {
            'created_at': { asc: 'bi-sort-up', desc: 'bi-sort-down' },
            'priority': { asc: 'bi-sort-down', desc: 'bi-sort-up' },
            'status': { asc: 'bi-sort-alpha-up', desc: 'bi-sort-alpha-down' }
        };
        activeIcon.className = `bi ${iconMap2[currentThreadSort.field][currentThreadSort.direction]}`;
    }
}
