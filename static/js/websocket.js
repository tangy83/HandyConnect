/**
 * WebSocket Manager for Real-time Updates
 * Handles connection, reconnection, and event processing
 */
(function() {
    'use strict';

    const WebSocketManager = {
        socket: null,
        reconnectAttempts: 0,
        maxReconnectAttempts: 5,
        reconnectDelay: 1000,
        maxReconnectDelay: 30000,
        eventQueue: [],
        isConnected: false,
        lastEventTime: 0,
        eventBatchTimeout: null,
        debugMode: false,
        muteNotifications: false,

        init() {
            this.debugMode = window.location.hostname === 'localhost';
            this.loadMutePreference();
            this.connect();
            this.setupEventListeners();
            this.setupDebugPanel();
        },

        connect() {
            try {
                // Use Socket.IO client
                this.socket = io({
                    transports: ['websocket', 'polling'],
                    timeout: 20000,
                    forceNew: true
                });

                this.socket.on('connect', () => {
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.updateConnectionStatus('connected');
                    this.log('Connected to WebSocket server');
                    this.processEventQueue();
                });

                this.socket.on('disconnect', (reason) => {
                    this.isConnected = false;
                    this.updateConnectionStatus('disconnected');
                    this.log(`Disconnected: ${reason}`);
                    this.scheduleReconnect();
                });

                this.socket.on('connect_error', (error) => {
                    this.log(`Connection error: ${error.message}`);
                    this.scheduleReconnect();
                });

                // Task events
                this.socket.on('task_created', (data) => this.handleEvent('task_created', data));
                this.socket.on('task_updated', (data) => this.handleEvent('task_updated', data));
                this.socket.on('task_deleted', (data) => this.handleEvent('task_deleted', data));
                this.socket.on('stats_updated', (data) => this.handleEvent('stats_updated', data));
                this.socket.on('thread_updated', (data) => this.handleEvent('thread_updated', data));

            } catch (error) {
                this.log(`WebSocket initialization failed: ${error.message}`);
                this.fallbackToPolling();
            }
        },

        handleEvent(eventType, data) {
            const event = {
                type: eventType,
                data: data,
                timestamp: Date.now(),
                id: `${eventType}_${data.id || Math.random()}`
            };

            this.log(`Received event: ${eventType}`, data);
            this.addToEventQueue(event);
        },

        addToEventQueue(event) {
            // Check for stale events
            if (event.data.updated_at && this.lastEventTime > new Date(event.data.updated_at).getTime()) {
                this.log(`Ignoring stale event: ${event.type}`);
                return;
            }

            this.eventQueue.push(event);
            this.lastEventTime = Math.max(this.lastEventTime, event.timestamp);

            // Batch events within 200ms
            if (this.eventBatchTimeout) {
                clearTimeout(this.eventBatchTimeout);
            }

            this.eventBatchTimeout = setTimeout(() => {
                this.processEventQueue();
            }, 200);
        },

        processEventQueue() {
            if (this.eventQueue.length === 0) return;

            const events = [...this.eventQueue];
            this.eventQueue = [];

            this.log(`Processing ${events.length} events`);

            // Group events by type for efficient processing
            const eventGroups = events.reduce((groups, event) => {
                if (!groups[event.type]) groups[event.type] = [];
                groups[event.type].push(event);
                return groups;
            }, {});

            // Process each group
            Object.entries(eventGroups).forEach(([eventType, groupEvents]) => {
                this.processEventGroup(eventType, groupEvents);
            });

            // Update debug panel
            this.updateDebugPanel(events);
        },

        processEventGroup(eventType, events) {
            switch (eventType) {
                case 'task_created':
                    this.handleTaskCreated(events);
                    break;
                case 'task_updated':
                    this.handleTaskUpdated(events);
                    break;
                case 'task_deleted':
                    this.handleTaskDeleted(events);
                    break;
                case 'stats_updated':
                    this.handleStatsUpdated(events);
                    break;
                case 'thread_updated':
                    this.handleThreadUpdated(events);
                    break;
            }
        },

        handleTaskCreated(events) {
            events.forEach(event => {
                // Add to task list
                if (window.TaskManager) {
                    window.TaskManager.addTask(event.data);
                }
                
                // Show notification
                if (!this.muteNotifications) {
                    this.showNotification('New Task', `Task "${event.data.subject}" has been created`, 'success', () => {
                        if (window.TaskManager) {
                            window.TaskManager.openTaskModal(event.data.id);
                        }
                    });
                }
            });
        },

        handleTaskUpdated(events) {
            events.forEach(event => {
                // Update task in list
                if (window.TaskManager) {
                    window.TaskManager.updateTask(event.data);
                }
            });
        },

        handleTaskDeleted(events) {
            events.forEach(event => {
                // Remove from task list
                if (window.TaskManager) {
                    window.TaskManager.removeTask(event.data.id);
                }
            });
        },

        handleStatsUpdated(events) {
            // Update dashboard stats
            if (window.DashboardManager) {
                window.DashboardManager.updateStats(events[0].data);
            }
        },

        handleThreadUpdated(events) {
            // Update thread list
            if (window.ThreadManager) {
                window.ThreadManager.updateThread(events[0].data);
            }
        },

        scheduleReconnect() {
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                this.log('Max reconnection attempts reached, falling back to polling');
                this.fallbackToPolling();
                return;
            }

            this.reconnectAttempts++;
            const delay = Math.min(
                this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
                this.maxReconnectDelay
            );

            this.log(`Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`);
            
            setTimeout(() => {
                this.connect();
            }, delay);
        },

        fallbackToPolling() {
            this.log('Falling back to polling mode');
            this.updateConnectionStatus('polling');
            
            // Start reduced polling (2-5 minutes)
            setInterval(() => {
                if (window.TaskManager) {
                    window.TaskManager.refreshTasks();
                }
            }, 120000); // 2 minutes
        },

        updateConnectionStatus(status) {
            const statusElement = document.getElementById('connection-status');
            if (!statusElement) return;

            const statusMap = {
                connected: { text: 'Live', class: 'text-success', icon: 'bi-circle-fill' },
                disconnected: { text: 'Offline', class: 'text-danger', icon: 'bi-circle' },
                polling: { text: 'Polling', class: 'text-warning', icon: 'bi-arrow-clockwise' }
            };

            const statusInfo = statusMap[status] || statusMap.disconnected;
            statusElement.innerHTML = `
                <i class="bi ${statusInfo.icon}"></i>
                <span class="${statusInfo.class}">${statusInfo.text}</span>
            `;
        },

        showNotification(title, message, type = 'info', action = null) {
            if (window.NotificationManager) {
                window.NotificationManager.show(title, message, type, action);
            }
        },

        setupEventListeners() {
            // Handle page visibility changes
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    this.log('Page hidden, pausing real-time updates');
                } else {
                    this.log('Page visible, resuming real-time updates');
                    if (!this.isConnected) {
                        this.connect();
                    }
                }
            });

            // Handle online/offline status
            window.addEventListener('online', () => {
                this.log('Network online, attempting reconnection');
                if (!this.isConnected) {
                    this.connect();
                }
            });

            window.addEventListener('offline', () => {
                this.log('Network offline');
                this.updateConnectionStatus('disconnected');
            });
        },

        setupDebugPanel() {
            if (!this.debugMode) return;

            // Create debug panel
            const debugPanel = document.createElement('div');
            debugPanel.id = 'websocket-debug';
            debugPanel.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                width: 300px;
                max-height: 400px;
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 0.375rem;
                padding: 10px;
                font-size: 12px;
                z-index: 9999;
                display: none;
                overflow-y: auto;
            `;

            debugPanel.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <strong>WebSocket Debug</strong>
                    <button class="btn btn-sm btn-outline-secondary" onclick="this.parentElement.parentElement.style.display='none'">×</button>
                </div>
                <div id="debug-events"></div>
            `;

            document.body.appendChild(debugPanel);

            // Toggle debug panel with Ctrl+Shift+D
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                    debugPanel.style.display = debugPanel.style.display === 'none' ? 'block' : 'none';
                }
            });
        },

        updateDebugPanel(events) {
            if (!this.debugMode) return;

            const debugEvents = document.getElementById('debug-events');
            if (!debugEvents) return;

            // Keep only last 10 events
            const recentEvents = events.slice(-10);
            
            debugEvents.innerHTML = recentEvents.map(event => `
                <div class="mb-1 p-1 border-bottom">
                    <div class="fw-bold">${event.type}</div>
                    <div class="text-muted">${new Date(event.timestamp).toLocaleTimeString()}</div>
                    <div class="small">${JSON.stringify(event.data, null, 2).substring(0, 100)}...</div>
                </div>
            `).join('');
        },

        loadMutePreference() {
            this.muteNotifications = localStorage.getItem('muteNotifications') === 'true';
        },

        toggleMute() {
            this.muteNotifications = !this.muteNotifications;
            localStorage.setItem('muteNotifications', this.muteNotifications);
            this.log(`Notifications ${this.muteNotifications ? 'muted' : 'unmuted'}`);
        },

        log(message, data = null) {
            if (this.debugMode) {
                console.debug('[WebSocket]', message, data);
            }
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => WebSocketManager.init());
    } else {
        WebSocketManager.init();
    }

    // Expose globally
    window.WebSocketManager = WebSocketManager;

})();


