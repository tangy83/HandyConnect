/**
 * Kanban Board Manager
 * Handles drag-and-drop task management with status columns
 */
(function() {
    'use strict';

    const KanbanManager = {
        board: null,
        columns: ['New', 'In Progress', 'On Hold', 'Completed'],
        tasks: [],
        sortableInstances: [],
        currentView: 'table',
        wipLimits: {
            'New': 50,
            'In Progress': 10,
            'On Hold': 20,
            'Completed': 100
        },
        swimlanes: {
            enabled: false,
            type: 'category', // 'category' or 'assignee'
            value: null
        },

        init() {
            this.createViewToggle();
            this.loadViewPreference();
            this.setupEventListeners();
        },

        createViewToggle() {
            const toggleContainer = document.createElement('div');
            toggleContainer.className = 'btn-group mb-3';
            toggleContainer.innerHTML = `
                <button class="btn btn-outline-primary active" id="table-view-btn" onclick="KanbanManager.switchView('table')">
                    <i class="bi bi-table"></i> Table
                </button>
                <button class="btn btn-outline-primary" id="kanban-view-btn" onclick="KanbanManager.switchView('kanban')">
                    <i class="bi bi-kanban"></i> Kanban
                </button>
            `;

            // Insert before the filters section
            const filtersSection = document.querySelector('.card.mb-4');
            if (filtersSection) {
                filtersSection.parentNode.insertBefore(toggleContainer, filtersSection);
            }
        },

        switchView(view) {
            this.currentView = view;
            localStorage.setItem('viewMode', view);

            // Update button states
            document.getElementById('table-view-btn').classList.toggle('active', view === 'table');
            document.getElementById('kanban-view-btn').classList.toggle('active', view === 'kanban');

            if (view === 'kanban') {
                this.showKanbanView();
            } else {
                this.showTableView();
            }
        },

        showKanbanView() {
            const tableContainer = document.querySelector('.table-responsive');
            if (!tableContainer) return;

            // Hide table
            tableContainer.style.display = 'none';

            // Create or show kanban board
            let kanbanContainer = document.getElementById('kanban-board');
            if (!kanbanContainer) {
                kanbanContainer = this.createKanbanBoard();
                tableContainer.parentNode.insertBefore(kanbanContainer, tableContainer);
            }

            kanbanContainer.style.display = 'block';
            this.renderKanbanBoard();
        },

        showTableView() {
            const tableContainer = document.querySelector('.table-responsive');
            const kanbanContainer = document.getElementById('kanban-board');

            if (tableContainer) {
                tableContainer.style.display = 'block';
            }
            if (kanbanContainer) {
                kanbanContainer.style.display = 'none';
            }
        },

        createKanbanBoard() {
            const container = document.createElement('div');
            container.id = 'kanban-board';
            container.className = 'kanban-board';
            container.style.cssText = `
                display: flex;
                gap: 1rem;
                overflow-x: auto;
                padding: 1rem 0;
                min-height: 500px;
            `;

            // Create columns
            this.columns.forEach(status => {
                const column = this.createColumn(status);
                container.appendChild(column);
            });

            // Add swimlane controls
            this.addSwimlaneControls(container);

            return container;
        },

        createColumn(status) {
            const column = document.createElement('div');
            column.className = 'kanban-column';
            column.dataset.status = status;
            column.style.cssText = `
                flex: 1;
                min-width: 280px;
                background: #f8f9fa;
                border-radius: 0.5rem;
                padding: 1rem;
                border: 1px solid #dee2e6;
            `;

            const wipLimit = this.wipLimits[status];
            const taskCount = this.getTasksByStatus(status).length;

            column.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="mb-0 text-capitalize">${status}</h6>
                    <div class="d-flex align-items-center gap-2">
                        <span class="badge bg-secondary">${taskCount}</span>
                        ${wipLimit ? `<small class="text-muted">/ ${wipLimit}</small>` : ''}
                    </div>
                </div>
                <div class="kanban-cards" data-status="${status}">
                    <!-- Cards will be rendered here -->
                </div>
            `;

            // Add WIP limit warning
            if (wipLimit && taskCount >= wipLimit) {
                column.classList.add('wip-exceeded');
                column.style.borderColor = '#dc3545';
            }

            return column;
        },

        addSwimlaneControls(container) {
            const controls = document.createElement('div');
            controls.className = 'kanban-controls mb-3';
            controls.innerHTML = `
                <div class="row g-2">
                    <div class="col-md-4">
                        <label class="form-label">Swimlanes</label>
                        <select class="form-select form-select-sm" id="swimlane-type">
                            <option value="">None</option>
                            <option value="category">By Category</option>
                            <option value="assignee">By Assignee</option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Filter</label>
                        <select class="form-select form-select-sm" id="swimlane-filter" disabled>
                            <option value="">All</option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Actions</label>
                        <div class="btn-group w-100">
                            <button class="btn btn-outline-secondary btn-sm" onclick="KanbanManager.refreshBoard()">
                                <i class="bi bi-arrow-clockwise"></i> Refresh
                            </button>
                            <button class="btn btn-outline-primary btn-sm" onclick="KanbanManager.exportBoard()">
                                <i class="bi bi-download"></i> Export
                            </button>
                        </div>
                    </div>
                </div>
            `;

            container.parentNode.insertBefore(controls, container);

            // Add event listeners
            document.getElementById('swimlane-type').addEventListener('change', (e) => {
                this.setSwimlanes(e.target.value);
            });

            document.getElementById('swimlane-filter').addEventListener('change', (e) => {
                this.filterSwimlanes(e.target.value);
            });
        },

        renderKanbanBoard() {
            // Load tasks if not already loaded
            if (this.tasks.length === 0) {
                this.loadTasks();
                return;
            }

            // Clear existing cards
            document.querySelectorAll('.kanban-cards').forEach(container => {
                container.innerHTML = '';
            });

            // Group tasks by status
            const tasksByStatus = this.groupTasksByStatus();

            // Render cards for each column
            this.columns.forEach(status => {
                const container = document.querySelector(`[data-status="${status}"]`);
                const tasks = tasksByStatus[status] || [];

                tasks.forEach(task => {
                    const card = this.createTaskCard(task);
                    container.appendChild(card);
                });

                // Update task count
                const countElement = container.parentNode.querySelector('.badge');
                countElement.textContent = tasks.length;

                // Check WIP limit
                const wipLimit = this.wipLimits[status];
                if (wipLimit && tasks.length >= wipLimit) {
                    container.parentNode.classList.add('wip-exceeded');
                } else {
                    container.parentNode.classList.remove('wip-exceeded');
                }
            });

            // Initialize drag and drop
            this.initializeDragAndDrop();
        },

        createTaskCard(task) {
            const card = document.createElement('div');
            card.className = 'kanban-card card mb-2';
            card.dataset.taskId = task.id;
            card.style.cssText = `
                cursor: grab;
                transition: all 0.2s ease;
                border-left: 4px solid ${this.getPriorityColor(task.priority)};
            `;

            const assigneeInitials = this.getInitials(task.assigned_to || 'Unassigned');
            const updatedAt = new Date(task.updated_at || task.created_at).toLocaleDateString();

            card.innerHTML = `
                <div class="card-body p-2">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0" style="font-size: 0.9rem;">${this.escapeHtml(task.subject)}</h6>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="dropdown">
                                <i class="bi bi-three-dots-vertical"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" onclick="KanbanManager.openTaskModal(${task.id})">
                                    <i class="bi bi-eye"></i> View
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="KanbanManager.editTask(${task.id})">
                                    <i class="bi bi-pencil"></i> Edit
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="KanbanManager.assignTask(${task.id})">
                                    <i class="bi bi-person-plus"></i> Assign
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" href="#" onclick="KanbanManager.deleteTask(${task.id})">
                                    <i class="bi bi-trash"></i> Delete
                                </a></li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="mb-2">
                        <span class="badge bg-secondary me-1">${task.category}</span>
                        <span class="badge bg-${this.getPriorityClass(task.priority)}">${task.priority}</span>
                    </div>
                    
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                            <div class="avatar me-2" style="width: 24px; height: 24px; background: ${this.getAvatarColor(task.assigned_to)}; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; color: white;">
                                ${assigneeInitials}
                            </div>
                            <small class="text-muted">${task.assigned_to || 'Unassigned'}</small>
                        </div>
                        <small class="text-muted">${updatedAt}</small>
                    </div>
                </div>
            `;

            // Add hover effects
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = 'none';
            });

            return card;
        },

        initializeDragAndDrop() {
            // Destroy existing sortable instances
            this.sortableInstances.forEach(instance => instance.destroy());
            this.sortableInstances = [];

            // Initialize SortableJS for each column
            document.querySelectorAll('.kanban-cards').forEach(container => {
                const sortable = Sortable.create(container, {
                    group: 'kanban',
                    animation: 150,
                    ghostClass: 'kanban-card-ghost',
                    chosenClass: 'kanban-card-chosen',
                    dragClass: 'kanban-card-drag',
                    onEnd: (evt) => {
                        this.handleCardDrop(evt);
                    }
                });

                this.sortableInstances.push(sortable);
            });
        },

        handleCardDrop(evt) {
            const taskId = evt.item.dataset.taskId;
            const newStatus = evt.to.dataset.status;
            const oldStatus = evt.from.dataset.status;

            if (newStatus === oldStatus) return;

            // Optimistic UI update
            this.updateTaskStatus(taskId, newStatus);

            // API call
            this.updateTaskStatusAPI(taskId, newStatus)
                .catch(error => {
                    // Rollback on error
                    this.rollbackTaskMove(taskId, oldStatus, newStatus);
                    this.showError('Failed to update task status', error.message);
                });
        },

        async updateTaskStatusAPI(taskId, status) {
            try {
                const response = await API.put(`/api/tasks/${taskId}`, { status });
                if (response.status === 'success') {
                    this.showSuccess('Task status updated successfully');
                }
            } catch (error) {
                throw error;
            }
        },

        updateTaskStatus(taskId, status) {
            // Update task in local data
            const task = this.tasks.find(t => t.id == taskId);
            if (task) {
                task.status = status;
                task.updated_at = new Date().toISOString();
            }

            // Re-render board
            this.renderKanbanBoard();
        },

        rollbackTaskMove(taskId, oldStatus, newStatus) {
            // Move card back to original column
            const card = document.querySelector(`[data-task-id="${taskId}"]`);
            const oldContainer = document.querySelector(`[data-status="${oldStatus}"]`);
            
            if (card && oldContainer) {
                oldContainer.appendChild(card);
            }

            // Update local data
            const task = this.tasks.find(t => t.id == taskId);
            if (task) {
                task.status = oldStatus;
            }
        },

        groupTasksByStatus() {
            const grouped = {};
            this.columns.forEach(status => {
                grouped[status] = [];
            });

            this.tasks.forEach(task => {
                const status = task.status || 'New';
                if (grouped[status]) {
                    grouped[status].push(task);
                }
            });

            return grouped;
        },

        getTasksByStatus(status) {
            return this.tasks.filter(task => (task.status || 'New') === status);
        },

        async loadTasks() {
            try {
                const response = await API.get('/api/tasks');
                if (response.status === 'success') {
                    this.tasks = response.data || [];
                    this.renderKanbanBoard();
                }
            } catch (error) {
                this.showError('Failed to load tasks', error.message);
            }
        },

        setSwimlanes(type) {
            this.swimlanes.enabled = type !== '';
            this.swimlanes.type = type;
            this.swimlanes.value = null;

            const filterSelect = document.getElementById('swimlane-filter');
            filterSelect.disabled = !this.swimlanes.enabled;

            if (this.swimlanes.enabled) {
                this.populateSwimlaneFilter();
            } else {
                filterSelect.innerHTML = '<option value="">All</option>';
                this.renderKanbanBoard();
            }
        },

        populateSwimlaneFilter() {
            const filterSelect = document.getElementById('swimlane-filter');
            const values = new Set();

            this.tasks.forEach(task => {
                const value = this.swimlanes.type === 'category' ? task.category : task.assigned_to;
                if (value) {
                    values.add(value);
                }
            });

            filterSelect.innerHTML = '<option value="">All</option>' +
                Array.from(values).map(value => 
                    `<option value="${this.escapeHtml(value)}">${this.escapeHtml(value)}</option>`
                ).join('');
        },

        filterSwimlanes(value) {
            this.swimlanes.value = value;
            this.renderKanbanBoard();
        },

        getPriorityColor(priority) {
            const colors = {
                'Low': '#28a745',
                'Medium': '#ffc107',
                'High': '#fd7e14',
                'Urgent': '#dc3545'
            };
            return colors[priority] || '#6c757d';
        },

        getPriorityClass(priority) {
            const classes = {
                'Low': 'success',
                'Medium': 'warning',
                'High': 'danger',
                'Urgent': 'danger'
            };
            return classes[priority] || 'secondary';
        },

        getInitials(name) {
            return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
        },

        getAvatarColor(name) {
            const colors = ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#20c997', '#fd7e14'];
            const hash = name.split('').reduce((a, b) => {
                a = ((a << 5) - a) + b.charCodeAt(0);
                return a & a;
            }, 0);
            return colors[Math.abs(hash) % colors.length];
        },

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        loadViewPreference() {
            const savedView = localStorage.getItem('viewMode');
            if (savedView === 'kanban') {
                this.switchView('kanban');
            }
        },

        setupEventListeners() {
            // Keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (this.currentView !== 'kanban') return;

                const selectedCard = document.querySelector('.kanban-card.selected');
                if (!selectedCard) return;

                switch(e.key) {
                    case '[':
                        this.moveCardLeft(selectedCard);
                        break;
                    case ']':
                        this.moveCardRight(selectedCard);
                        break;
                    case 'Enter':
                        this.openTaskModal(selectedCard.dataset.taskId);
                        break;
                }
            });

            // Card selection
            document.addEventListener('click', (e) => {
                const card = e.target.closest('.kanban-card');
                if (card) {
                    document.querySelectorAll('.kanban-card').forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                }
            });
        },

        moveCardLeft(card) {
            const currentColumn = card.closest('.kanban-column');
            const prevColumn = currentColumn.previousElementSibling;
            if (prevColumn) {
                const cardsContainer = prevColumn.querySelector('.kanban-cards');
                cardsContainer.appendChild(card);
                this.handleCardDrop({ item: card, to: cardsContainer, from: currentColumn.querySelector('.kanban-cards') });
            }
        },

        moveCardRight(card) {
            const currentColumn = card.closest('.kanban-column');
            const nextColumn = currentColumn.nextElementSibling;
            if (nextColumn) {
                const cardsContainer = nextColumn.querySelector('.kanban-cards');
                cardsContainer.appendChild(card);
                this.handleCardDrop({ item: card, to: cardsContainer, from: currentColumn.querySelector('.kanban-cards') });
            }
        },

        openTaskModal(taskId) {
            if (window.TaskManager && window.TaskManager.viewTask) {
                window.TaskManager.viewTask(taskId);
            }
        },

        editTask(taskId) {
            // Implementation for editing task
            console.log('Edit task:', taskId);
        },

        assignTask(taskId) {
            // Implementation for assigning task
            console.log('Assign task:', taskId);
        },

        deleteTask(taskId) {
            if (confirm('Are you sure you want to delete this task?')) {
                // Implementation for deleting task
                console.log('Delete task:', taskId);
            }
        },

        refreshBoard() {
            this.loadTasks();
        },

        exportBoard() {
            // Implementation for exporting board
            console.log('Export board');
        },

        showSuccess(message) {
            if (window.NotificationManager) {
                window.NotificationManager.showSuccess('Success', message);
            }
        },

        showError(title, message) {
            if (window.NotificationManager) {
                window.NotificationManager.showError(title, message);
            }
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => KanbanManager.init());
    } else {
        KanbanManager.init();
    }

    // Expose globally
    window.KanbanManager = KanbanManager;

})();


