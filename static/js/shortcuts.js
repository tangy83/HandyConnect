/**
 * Keyboard Shortcuts Manager
 * Handles keyboard shortcuts and help overlay
 */
(function() {
    'use strict';

    const ShortcutsManager = {
        shortcuts: {
            // Navigation
            'g d': { action: 'navigate', target: '/', description: 'Go to Dashboard' },
            'g t': { action: 'navigate', target: '/threads', description: 'Go to Threads' },
            'g a': { action: 'navigate', target: '/analytics', description: 'Go to Analytics' },
            
            // General
            'n': { action: 'newTask', description: 'New Task' },
            '?': { action: 'help', description: 'Show Keyboard Shortcuts' },
            'Escape': { action: 'closeModals', description: 'Close Modals/Popovers' },
            
            // Search and Focus
            'ctrl+f': { action: 'focusSearch', description: 'Focus Search' },
            'cmd+f': { action: 'focusSearch', description: 'Focus Search' },
            'ctrl+k': { action: 'commandPalette', description: 'Command Palette' },
            'cmd+k': { action: 'commandPalette', description: 'Command Palette' },
            
            // Task Management
            'Delete': { action: 'deleteSelected', description: 'Delete Selected Tasks' },
            'Backspace': { action: 'deleteSelected', description: 'Delete Selected Tasks' },
            'Enter': { action: 'openSelected', description: 'Open Selected Task' },
            
            // Kanban Navigation
            '[': { action: 'moveCardLeft', description: 'Move Card Left (Kanban)' },
            ']': { action: 'moveCardRight', description: 'Move Card Right (Kanban)' },
            
            // Status and Priority
            's': { action: 'cycleStatus', description: 'Cycle Task Status' },
            'p': { action: 'cyclePriority', description: 'Cycle Task Priority' },
            'c': { action: 'changeCategory', description: 'Change Category' },
            
            // Selection
            'ctrl+a': { action: 'selectAll', description: 'Select All Tasks' },
            'cmd+a': { action: 'selectAll', description: 'Select All Tasks' },
            'a': { action: 'selectAll', description: 'Select All Tasks' },
            
            // Templates
            't': { action: 'showTemplates', description: 'Show Task Templates' },
            
            // View Toggle
            'v': { action: 'toggleView', description: 'Toggle Table/Kanban View' },
            
            // Refresh
            'r': { action: 'refresh', description: 'Refresh Data' },
            'F5': { action: 'refresh', description: 'Refresh Data' }
        },
        
        keySequence: [],
        sequenceTimeout: null,
        enabled: true,
        helpOverlay: null,

        init() {
            this.loadSettings();
            this.setupEventListeners();
            this.createHelpOverlay();
        },

        setupEventListeners() {
            document.addEventListener('keydown', (e) => {
                if (!this.enabled) return;
                
                // Handle key sequences (like 'g' then 'd')
                this.handleKeySequence(e);
                
                // Handle single key shortcuts
                this.handleSingleKey(e);
                
                // Handle modifier combinations
                this.handleModifierCombinations(e);
            });
        },

        handleKeySequence(e) {
            const key = e.key.toLowerCase();
            
            // Reset sequence if too much time has passed
            if (this.sequenceTimeout) {
                clearTimeout(this.sequenceTimeout);
            }
            
            this.keySequence.push(key);
            
            // Check for sequence matches
            const sequence = this.keySequence.join(' ');
            const shortcut = this.shortcuts[sequence];
            
            if (shortcut) {
                e.preventDefault();
                this.executeShortcut(shortcut);
                this.keySequence = [];
                return;
            }
            
            // Clear sequence after 1 second
            this.sequenceTimeout = setTimeout(() => {
                this.keySequence = [];
            }, 1000);
            
            // If sequence is too long, reset
            if (this.keySequence.length > 3) {
                this.keySequence = [];
            }
        },

        handleSingleKey(e) {
            const key = e.key;
            const shortcut = this.shortcuts[key];
            
            if (shortcut && !e.ctrlKey && !e.metaKey && !e.altKey) {
                // Check if we're in an input field
                if (this.isInputField(e.target)) {
                    // Only allow certain shortcuts in input fields
                    if (['Escape', 'Enter'].includes(key)) {
                        e.preventDefault();
                        this.executeShortcut(shortcut);
                    }
                    return;
                }
                
                e.preventDefault();
                this.executeShortcut(shortcut);
            }
        },

        handleModifierCombinations(e) {
            const modifiers = [];
            if (e.ctrlKey) modifiers.push('ctrl');
            if (e.metaKey) modifiers.push('cmd');
            if (e.altKey) modifiers.push('alt');
            if (e.shiftKey) modifiers.push('shift');
            
            if (modifiers.length > 0) {
                const key = modifiers.join('+') + '+' + e.key.toLowerCase();
                const shortcut = this.shortcuts[key];
                
                if (shortcut) {
                    e.preventDefault();
                    this.executeShortcut(shortcut);
                }
            }
        },

        executeShortcut(shortcut) {
            switch (shortcut.action) {
                case 'navigate':
                    window.location.href = shortcut.target;
                    break;
                    
                case 'newTask':
                    this.showNewTaskModal();
                    break;
                    
                case 'help':
                    this.showHelpOverlay();
                    break;
                    
                case 'closeModals':
                    this.closeModals();
                    break;
                    
                case 'focusSearch':
                    this.focusSearch();
                    break;
                    
                case 'commandPalette':
                    this.showCommandPalette();
                    break;
                    
                case 'deleteSelected':
                    this.deleteSelectedTasks();
                    break;
                    
                case 'openSelected':
                    this.openSelectedTask();
                    break;
                    
                case 'moveCardLeft':
                    this.moveCardLeft();
                    break;
                    
                case 'moveCardRight':
                    this.moveCardRight();
                    break;
                    
                case 'cycleStatus':
                    this.cycleStatus();
                    break;
                    
                case 'cyclePriority':
                    this.cyclePriority();
                    break;
                    
                case 'changeCategory':
                    this.changeCategory();
                    break;
                    
                case 'selectAll':
                    this.selectAllTasks();
                    break;
                    
                case 'showTemplates':
                    this.showTemplates();
                    break;
                    
                case 'toggleView':
                    this.toggleView();
                    break;
                    
                case 'refresh':
                    this.refreshData();
                    break;
            }
        },

        isInputField(element) {
            const inputTypes = ['input', 'textarea', 'select'];
            return inputTypes.includes(element.tagName.toLowerCase()) || 
                   element.contentEditable === 'true' ||
                   element.isContentEditable;
        },

        showNewTaskModal() {
            // Implementation depends on your task creation modal
            console.log('Opening new task modal');
            // Example: document.getElementById('newTaskModal').click();
        },

        showHelpOverlay() {
            if (this.helpOverlay) {
                this.helpOverlay.style.display = 'flex';
            }
        },

        closeModals() {
            // Close all Bootstrap modals
            document.querySelectorAll('.modal.show').forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
            
            // Close all dropdowns
            document.querySelectorAll('.dropdown-menu.show').forEach(dropdown => {
                const bsDropdown = bootstrap.Dropdown.getInstance(dropdown.previousElementSibling);
                if (bsDropdown) {
                    bsDropdown.hide();
                }
            });
            
            // Close help overlay
            if (this.helpOverlay) {
                this.helpOverlay.style.display = 'none';
            }
        },

        focusSearch() {
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        },

        showCommandPalette() {
            // Implementation for command palette
            console.log('Showing command palette');
        },

        deleteSelectedTasks() {
            const selectedTasks = document.querySelectorAll('.task-checkbox:checked');
            if (selectedTasks.length > 0) {
                if (confirm(`Delete ${selectedTasks.length} selected task(s)?`)) {
                    // Implementation for bulk delete
                    console.log('Deleting selected tasks');
                }
            }
        },

        openSelectedTask() {
            const selectedCard = document.querySelector('.kanban-card.selected, .task-row.selected');
            if (selectedCard) {
                const taskId = selectedCard.dataset.taskId;
                if (taskId && window.TaskManager) {
                    window.TaskManager.viewTask(taskId);
                }
            }
        },

        moveCardLeft() {
            if (window.KanbanManager) {
                const selectedCard = document.querySelector('.kanban-card.selected');
                if (selectedCard) {
                    window.KanbanManager.moveCardLeft(selectedCard);
                }
            }
        },

        moveCardRight() {
            if (window.KanbanManager) {
                const selectedCard = document.querySelector('.kanban-card.selected');
                if (selectedCard) {
                    window.KanbanManager.moveCardRight(selectedCard);
                }
            }
        },

        cycleStatus() {
            const selectedCard = document.querySelector('.kanban-card.selected, .task-row.selected');
            if (selectedCard) {
                // Implementation for cycling through statuses
                console.log('Cycling status for selected task');
            }
        },

        cyclePriority() {
            const selectedCard = document.querySelector('.kanban-card.selected, .task-row.selected');
            if (selectedCard) {
                // Implementation for cycling through priorities
                console.log('Cycling priority for selected task');
            }
        },

        changeCategory() {
            const selectedCard = document.querySelector('.kanban-card.selected, .task-row.selected');
            if (selectedCard) {
                // Implementation for changing category
                console.log('Changing category for selected task');
            }
        },

        selectAllTasks() {
            const selectAllCheckbox = document.getElementById('select-all-tasks');
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = !selectAllCheckbox.checked;
                selectAllCheckbox.dispatchEvent(new Event('change'));
            }
        },

        showTemplates() {
            // Implementation for showing task templates
            console.log('Showing task templates');
        },

        toggleView() {
            if (window.KanbanManager) {
                const currentView = localStorage.getItem('viewMode') || 'table';
                const newView = currentView === 'table' ? 'kanban' : 'table';
                window.KanbanManager.switchView(newView);
            }
        },

        refreshData() {
            if (window.TaskManager && window.TaskManager.refreshTasks) {
                window.TaskManager.refreshTasks();
            } else {
                window.location.reload();
            }
        },

        createHelpOverlay() {
            this.helpOverlay = document.createElement('div');
            this.helpOverlay.className = 'shortcuts-overlay';
            this.helpOverlay.style.display = 'none';
            
            this.helpOverlay.innerHTML = `
                <div class="shortcuts-modal">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h4>Keyboard Shortcuts</h4>
                        <button class="btn-close" onclick="ShortcutsManager.closeModals()"></button>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="shortcuts-category">
                                <h6>Navigation</h6>
                                <div class="shortcut-item">
                                    <span>Go to Dashboard</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">g</span>
                                        <span class="shortcut-key">d</span>
                                    </div>
                                </div>
                                <div class="shortcut-item">
                                    <span>Go to Threads</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">g</span>
                                        <span class="shortcut-key">t</span>
                                    </div>
                                </div>
                                <div class="shortcut-item">
                                    <span>Go to Analytics</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">g</span>
                                        <span class="shortcut-key">a</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="shortcuts-category">
                                <h6>General</h6>
                                <div class="shortcut-item">
                                    <span>New Task</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">n</span>
                                    </div>
                                </div>
                                <div class="shortcut-item">
                                    <span>Show Help</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">?</span>
                                    </div>
                                </div>
                                <div class="shortcut-item">
                                    <span>Close Modals</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">Esc</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="shortcuts-category">
                                <h6>Search & Focus</h6>
                                <div class="shortcut-item">
                                    <span>Focus Search</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">Ctrl</span>
                                        <span class="shortcut-key">f</span>
                                    </div>
                                </div>
                                <div class="shortcut-item">
                                    <span>Command Palette</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">Ctrl</span>
                                        <span class="shortcut-key">k</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="shortcuts-category">
                                <h6>Task Management</h6>
                                <div class="shortcut-item">
                                    <span>Delete Selected</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">Del</span>
                                    </div>
                                </div>
                                <div class="shortcut-item">
                                    <span>Open Selected</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">Enter</span>
                                    </div>
                                </div>
                                <div class="shortcut-item">
                                    <span>Select All</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">Ctrl</span>
                                        <span class="shortcut-key">a</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="shortcuts-category">
                                <h6>Kanban</h6>
                                <div class="shortcut-item">
                                    <span>Move Card Left</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">[</span>
                                    </div>
                                </div>
                                <div class="shortcut-item">
                                    <span>Move Card Right</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">]</span>
                                    </div>
                                </div>
                                <div class="shortcut-item">
                                    <span>Toggle View</span>
                                    <div class="shortcut-keys">
                                        <span class="shortcut-key">v</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-4 pt-3 border-top">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="shortcuts-enabled" checked>
                            <label class="form-check-label" for="shortcuts-enabled">
                                Enable keyboard shortcuts
                            </label>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(this.helpOverlay);
            
            // Add event listener for enable/disable toggle
            document.getElementById('shortcuts-enabled').addEventListener('change', (e) => {
                this.enabled = e.target.checked;
                this.saveSettings();
            });
            
            // Close on overlay click
            this.helpOverlay.addEventListener('click', (e) => {
                if (e.target === this.helpOverlay) {
                    this.closeModals();
                }
            });
        },

        loadSettings() {
            const settings = localStorage.getItem('shortcutsSettings');
            if (settings) {
                const parsed = JSON.parse(settings);
                this.enabled = parsed.enabled !== false;
            }
        },

        saveSettings() {
            const settings = {
                enabled: this.enabled
            };
            localStorage.setItem('shortcutsSettings', JSON.stringify(settings));
        },

        // Public API
        enable() {
            this.enabled = true;
            this.saveSettings();
        },

        disable() {
            this.enabled = false;
            this.saveSettings();
        },

        addShortcut(key, action, description) {
            this.shortcuts[key] = { action, description };
        },

        removeShortcut(key) {
            delete this.shortcuts[key];
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => ShortcutsManager.init());
    } else {
        ShortcutsManager.init();
    }

    // Expose globally
    window.ShortcutsManager = ShortcutsManager;
    window.showKeyboardShortcuts = () => ShortcutsManager.showHelpOverlay();

})();


