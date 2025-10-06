/**
 * Resident Info Sidebar Manager
 * Handles resident profile display in task detail modal
 */
(function() {
    'use strict';

    const ResidentSidebarManager = {
        sidebar: null,
        isOpen: false,
        isPinned: false,
        currentResident: null,

        init() {
            this.loadSettings();
            this.createSidebar();
            this.setupEventListeners();
        },

        createSidebar() {
            this.sidebar = document.createElement('div');
            this.sidebar.id = 'resident-sidebar';
            this.sidebar.className = 'resident-sidebar';
            this.sidebar.style.cssText = `
                position: fixed;
                top: 0;
                right: -400px;
                width: 400px;
                height: 100vh;
                background: var(--bs-body-bg);
                border-left: 1px solid var(--bs-border-color);
                z-index: 1050;
                transition: right 0.3s ease;
                overflow-y: auto;
                box-shadow: -2px 0 10px rgba(0,0,0,0.1);
            `;

            this.sidebar.innerHTML = `
                <div class="resident-sidebar-header p-3 border-bottom">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">Resident Profile</h6>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-secondary" id="pin-sidebar" title="Pin Sidebar">
                                <i class="bi bi-pin"></i>
                            </button>
                            <button class="btn btn-outline-secondary" id="close-sidebar" title="Close">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                    </div>
                </div>
                <div class="resident-sidebar-content p-3" id="resident-content">
                    <div class="text-center text-muted">
                        <i class="bi bi-person-circle fs-1"></i>
                        <p>Select a task to view resident profile</p>
                    </div>
                </div>
            `;

            document.body.appendChild(this.sidebar);
        },

        show(residentData) {
            this.currentResident = residentData;
            this.loadResidentData(residentData);
            this.sidebar.style.right = '0';
            this.isOpen = true;
            
            // Focus trap
            this.setupFocusTrap();
        },

        hide() {
            if (!this.isPinned) {
                this.sidebar.style.right = '-400px';
                this.isOpen = false;
                this.currentResident = null;
            }
        },

        toggle() {
            if (this.isOpen) {
                this.hide();
            } else if (this.currentResident) {
                this.show(this.currentResident);
            }
        },

        async loadResidentData(residentData) {
            const content = document.getElementById('resident-content');
            
            // Show loading state
            content.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border" role="status"></div>
                    <p class="mt-2">Loading resident profile...</p>
                </div>
            `;

            try {
                // Fetch additional resident data
                const residentInfo = await this.fetchResidentInfo(residentData.email);
                
                // Render resident profile
                this.renderResidentProfile(residentInfo);
                
            } catch (error) {
                this.renderErrorState(error);
            }
        },

        async fetchResidentInfo(email) {
            // Mock API call - replace with actual endpoint
            const response = await API.get(`/api/residents/${encodeURIComponent(email)}`);
            return response.data || this.createMockResidentData(email);
        },

        createMockResidentData(email) {
            // Mock data for demonstration
            return {
                name: email.split('@')[0].replace(/[._]/g, ' '),
                email: email,
                unit: 'Apt 101',
                joinDate: '2023-01-15',
                totalTasks: Math.floor(Math.random() * 50) + 10,
                avgResolutionTime: Math.floor(Math.random() * 48) + 12,
                sentimentHistory: ['Positive', 'Neutral', 'Positive', 'Negative', 'Positive'],
                recentTasks: [
                    { id: 1, subject: 'Heating Issue', status: 'Completed', created_at: '2024-01-15' },
                    { id: 2, subject: 'Noise Complaint', status: 'In Progress', created_at: '2024-01-10' },
                    { id: 3, subject: 'Package Delivery', status: 'Completed', created_at: '2024-01-05' }
                ]
            };
        },

        renderResidentProfile(residentInfo) {
            const content = document.getElementById('resident-content');
            
            const avatarColor = this.getAvatarColor(residentInfo.name);
            const initials = this.getInitials(residentInfo.name);
            
            content.innerHTML = `
                <div class="resident-profile">
                    <!-- Avatar and Basic Info -->
                    <div class="text-center mb-4">
                        <div class="resident-avatar mb-3" style="width: 80px; height: 80px; background: ${avatarColor}; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 2rem; color: white; font-weight: bold;">
                            ${initials}
                        </div>
                        <h5 class="mb-1">${this.escapeHtml(residentInfo.name)}</h5>
                        <p class="text-muted mb-2">${this.escapeHtml(residentInfo.email)}</p>
                        <span class="badge bg-secondary">Unit ${residentInfo.unit}</span>
                    </div>

                    <!-- Quick Stats -->
                    <div class="row g-2 mb-4">
                        <div class="col-6">
                            <div class="card text-center">
                                <div class="card-body p-2">
                                    <h6 class="card-title mb-1">${residentInfo.totalTasks}</h6>
                                    <small class="text-muted">Total Tasks</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="card text-center">
                                <div class="card-body p-2">
                                    <h6 class="card-title mb-1">${residentInfo.avgResolutionTime}h</h6>
                                    <small class="text-muted">Avg Resolution</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Recent Tasks -->
                    <div class="mb-4">
                        <h6 class="mb-3">Recent Tasks</h6>
                        <div class="list-group list-group-flush">
                            ${residentInfo.recentTasks.map(task => `
                                <div class="list-group-item px-0 py-2">
                                    <div class="d-flex justify-content-between align-items-start">
                                        <div>
                                            <h6 class="mb-1" style="font-size: 0.9rem;">${this.escapeHtml(task.subject)}</h6>
                                            <small class="text-muted">${new Date(task.created_at).toLocaleDateString()}</small>
                                        </div>
                                        <span class="badge bg-${this.getStatusColor(task.status)}">${task.status}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="text-center mt-2">
                            <button class="btn btn-outline-primary btn-sm" onclick="ResidentSidebarManager.viewAllTasks('${residentInfo.email}')">
                                View All Tasks
                            </button>
                        </div>
                    </div>

                    <!-- Sentiment History -->
                    <div class="mb-4">
                        <h6 class="mb-3">Sentiment History</h6>
                        <div class="d-flex gap-1">
                            ${residentInfo.sentimentHistory.map(sentiment => `
                                <span class="badge bg-${this.getSentimentColor(sentiment)}">${sentiment}</span>
                            `).join('')}
                        </div>
                    </div>

                    <!-- Actions -->
                    <div class="d-grid gap-2">
                        <button class="btn btn-primary" onclick="ResidentSidebarManager.createNewTask('${residentInfo.email}')">
                            <i class="bi bi-plus"></i> New Task
                        </button>
                        <button class="btn btn-outline-secondary" onclick="ResidentSidebarManager.sendMessage('${residentInfo.email}')">
                            <i class="bi bi-envelope"></i> Send Message
                        </button>
                    </div>
                </div>
            `;
        },

        renderErrorState(error) {
            const content = document.getElementById('resident-content');
            content.innerHTML = `
                <div class="text-center">
                    <i class="bi bi-exclamation-triangle text-warning fs-1"></i>
                    <h6 class="mt-2">Error Loading Profile</h6>
                    <p class="text-muted">${this.escapeHtml(error.message)}</p>
                    <button class="btn btn-outline-primary btn-sm" onclick="ResidentSidebarManager.retryLoad()">
                        <i class="bi bi-arrow-clockwise"></i> Retry
                    </button>
                </div>
            `;
        },

        getAvatarColor(name) {
            const colors = ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#20c997', '#fd7e14'];
            const hash = name.split('').reduce((a, b) => {
                a = ((a << 5) - a) + b.charCodeAt(0);
                return a & a;
            }, 0);
            return colors[Math.abs(hash) % colors.length];
        },

        getInitials(name) {
            return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
        },

        getStatusColor(status) {
            const colors = {
                'New': 'secondary',
                'In Progress': 'primary',
                'Completed': 'success',
                'On Hold': 'warning'
            };
            return colors[status] || 'secondary';
        },

        getSentimentColor(sentiment) {
            const colors = {
                'Positive': 'success',
                'Neutral': 'secondary',
                'Negative': 'danger',
                'Frustrated': 'danger'
            };
            return colors[sentiment] || 'secondary';
        },

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        setupEventListeners() {
            // Close button
            document.getElementById('close-sidebar').addEventListener('click', () => {
                this.hide();
            });

            // Pin button
            document.getElementById('pin-sidebar').addEventListener('click', (e) => {
                this.togglePin();
            });

            // Click outside to close (if not pinned)
            document.addEventListener('click', (e) => {
                if (this.isOpen && !this.isPinned && 
                    !this.sidebar.contains(e.target) && 
                    !e.target.closest('[data-resident-email]')) {
                    this.hide();
                }
            });

            // Escape key to close
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen && !this.isPinned) {
                    this.hide();
                }
            });
        },

        setupFocusTrap() {
            const focusableElements = this.sidebar.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            
            if (focusableElements.length > 0) {
                focusableElements[0].focus();
            }
        },

        togglePin() {
            this.isPinned = !this.isPinned;
            const pinButton = document.getElementById('pin-sidebar');
            pinButton.innerHTML = this.isPinned ? '<i class="bi bi-pin-fill"></i>' : '<i class="bi bi-pin"></i>';
            pinButton.title = this.isPinned ? 'Unpin Sidebar' : 'Pin Sidebar';
            
            this.saveSettings();
        },

        viewAllTasks(email) {
            // Navigate to tasks filtered by this resident
            const url = new URL(window.location);
            url.searchParams.set('resident', email);
            window.location.href = url.toString();
        },

        createNewTask(email) {
            // Open new task modal with pre-filled resident email
            if (window.TaskManager && window.TaskManager.showNewTaskModal) {
                window.TaskManager.showNewTaskModal(email);
            }
        },

        sendMessage(email) {
            // Open message modal or compose email
            window.open(`mailto:${email}?subject=Re: Your Support Request`);
        },

        retryLoad() {
            if (this.currentResident) {
                this.loadResidentData(this.currentResident);
            }
        },

        loadSettings() {
            const settings = localStorage.getItem('residentSidebarSettings');
            if (settings) {
                const parsed = JSON.parse(settings);
                this.isPinned = parsed.isPinned || false;
            }
        },

        saveSettings() {
            const settings = {
                isPinned: this.isPinned
            };
            localStorage.setItem('residentSidebarSettings', JSON.stringify(settings));
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => ResidentSidebarManager.init());
    } else {
        ResidentSidebarManager.init();
    }

    // Expose globally
    window.ResidentSidebarManager = ResidentSidebarManager;

})();



