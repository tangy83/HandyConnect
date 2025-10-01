// HandyConnect Phase 11: System Integration Manager
// Comprehensive frontend-backend integration with real-time capabilities

class IntegrationManager {
    constructor() {
        this.baseURL = window.location.origin;
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.eventListeners = new Map();
        this.cache = new Map();
        this.cacheTimeout = 300000; // 5 minutes
        this.isOnline = navigator.onLine;
        this.pendingRequests = [];
        
        this.initializeIntegration();
    }

    initializeIntegration() {
        console.log('🚀 Initializing System Integration Manager');
        
        // Set up network status monitoring
        this.setupNetworkMonitoring();
        
        // Initialize WebSocket connection for real-time updates
        this.initializeWebSocket();
        
        // Set up periodic data synchronization
        this.setupPeriodicSync();
        
        // Initialize analytics integration
        this.initializeAnalyticsIntegration();
        
        // Set up error handling and retry mechanisms
        this.setupErrorHandling();
        
        console.log('✅ System Integration Manager initialized');
    }

    // ==================== NETWORK MONITORING ====================
    
    setupNetworkMonitoring() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.handleReconnection();
            this.showNotification('Connection restored', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showNotification('Connection lost', 'warning');
        });
    }

    handleReconnection() {
        // Process pending requests
        this.processPendingRequests();
        
        // Reconnect WebSocket
        if (this.websocket && this.websocket.readyState === WebSocket.CLOSED) {
            this.initializeWebSocket();
        }
        
        // Refresh critical data
        this.refreshCriticalData();
    }

    // ==================== WEBSOCKET INTEGRATION ====================
    
    initializeWebSocket() {
        if (!this.isOnline) return;
        
        try {
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsURL = `${wsProtocol}//${window.location.host}/socket.io/`;
            
            this.websocket = new WebSocket(wsURL);
            
            this.websocket.onopen = () => {
                console.log('🔌 WebSocket connected');
                this.reconnectAttempts = 0;
                this.emit('websocket:connected');
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                this.emit('websocket:disconnected');
                this.handleWebSocketReconnect();
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.emit('websocket:error', error);
            };
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            // Fallback to Server-Sent Events
            this.initializeSSE();
        }
    }

    initializeSSE() {
        try {
            const eventSource = new EventSource(`${this.baseURL}/api/realtime/dashboard/stream`);
            
            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing SSE message:', error);
                }
            };
            
            eventSource.onerror = (error) => {
                console.error('SSE error:', error);
                eventSource.close();
                setTimeout(() => this.initializeSSE(), 5000);
            };
            
            this.sse = eventSource;
            console.log('📡 Server-Sent Events initialized');
            
        } catch (error) {
            console.error('Failed to initialize SSE:', error);
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'task_update':
                this.handleTaskUpdate(data.payload);
                break;
            case 'analytics_update':
                this.handleAnalyticsUpdate(data.payload);
                break;
            case 'system_status':
                this.handleSystemStatusUpdate(data.payload);
                break;
            case 'notification':
                this.handleNotification(data.payload);
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }

    handleWebSocketReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting WebSocket reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.initializeWebSocket();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.log('❌ Max WebSocket reconnection attempts reached, falling back to polling');
            this.initializePollingFallback();
        }
    }

    // ==================== API INTEGRATION ====================
    
    async apiRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        };
        
        const requestOptions = { ...defaultOptions, ...options };
        
        // Add request to pending if offline
        if (!this.isOnline) {
            this.pendingRequests.push({ url, options: requestOptions });
            throw new Error('Offline - request queued');
        }
        
        try {
            const response = await fetch(url, requestOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            return data;
            
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    async getTasks(filters = {}) {
        const queryParams = new URLSearchParams(filters);
        const endpoint = `/api/tasks${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
        
        // Check cache first
        const cacheKey = `tasks_${JSON.stringify(filters)}`;
        const cached = this.getFromCache(cacheKey);
        if (cached) {
            return cached;
        }
        
        try {
            const data = await this.apiRequest(endpoint);
            this.setCache(cacheKey, data);
            return data;
        } catch (error) {
            throw error;
        }
    }

    async updateTask(taskId, updates) {
        try {
            const data = await this.apiRequest(`/api/tasks/${taskId}`, {
                method: 'PUT',
                body: JSON.stringify(updates)
            });
            
            // Clear related cache entries
            this.clearCachePattern('tasks_');
            
            // Emit update event
            this.emit('task:updated', { taskId, updates, data });
            
            return data;
        } catch (error) {
            throw error;
        }
    }

    async deleteTask(taskId) {
        try {
            const data = await this.apiRequest(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });
            
            // Clear related cache entries
            this.clearCachePattern('tasks_');
            
            // Emit delete event
            this.emit('task:deleted', { taskId, data });
            
            return data;
        } catch (error) {
            throw error;
        }
    }

    // ==================== ANALYTICS INTEGRATION ====================
    
    initializeAnalyticsIntegration() {
        // Track user interactions
        this.trackUserInteractions();
        
        // Set up analytics data collection
        this.setupAnalyticsCollection();
        
        // Initialize real-time analytics updates
        this.initializeAnalyticsUpdates();
    }

    trackUserInteractions() {
        // Track page views
        this.trackEvent('page_view', {
            page: window.location.pathname,
            timestamp: new Date().toISOString()
        });
        
        // Track button clicks
        document.addEventListener('click', (event) => {
            if (event.target.matches('button, .btn')) {
                this.trackEvent('button_click', {
                    button_text: event.target.textContent.trim(),
                    button_class: event.target.className,
                    page: window.location.pathname
                });
            }
        });
        
        // Track form submissions
        document.addEventListener('submit', (event) => {
            this.trackEvent('form_submit', {
                form_action: event.target.action,
                form_method: event.target.method,
                page: window.location.pathname
            });
        });
    }

    async trackEvent(eventType, eventData) {
        try {
            await this.apiRequest('/api/analytics/collect/user-behavior', {
                method: 'POST',
                body: JSON.stringify({
                    event_type: eventType,
                    event_data: eventData,
                    timestamp: new Date().toISOString(),
                    user_agent: navigator.userAgent,
                    url: window.location.href
                })
            });
        } catch (error) {
            console.error('Failed to track event:', error);
        }
    }

    setupAnalyticsCollection() {
        // Collect performance metrics
        this.collectPerformanceMetrics();
        
        // Collect user behavior data
        this.collectUserBehaviorData();
    }

    collectPerformanceMetrics() {
        // Navigation timing
        if (window.performance && window.performance.timing) {
            const timing = window.performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;
            
            this.trackEvent('performance_metrics', {
                load_time: loadTime,
                dom_content_loaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                page_load: timing.loadEventEnd - timing.navigationStart
            });
        }
        
        // Memory usage (if available)
        if (window.performance && window.performance.memory) {
            const memory = window.performance.memory;
            this.trackEvent('memory_usage', {
                used_js_heap_size: memory.usedJSHeapSize,
                total_js_heap_size: memory.totalJSHeapSize,
                js_heap_size_limit: memory.jsHeapSizeLimit
            });
        }
    }

    collectUserBehaviorData() {
        // Track scroll behavior
        let scrollDepth = 0;
        window.addEventListener('scroll', () => {
            const newScrollDepth = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
            if (newScrollDepth > scrollDepth + 10) { // Track every 10%
                scrollDepth = newScrollDepth;
                this.trackEvent('scroll_depth', { depth: scrollDepth });
            }
        });
        
        // Track time on page
        const startTime = Date.now();
        window.addEventListener('beforeunload', () => {
            const timeOnPage = Date.now() - startTime;
            this.trackEvent('time_on_page', { duration: timeOnPage });
        });
    }

    initializeAnalyticsUpdates() {
        // Request analytics data every 30 seconds
        setInterval(async () => {
            try {
                const analytics = await this.getAnalyticsData();
                this.emit('analytics:updated', analytics);
                this.updateAnalyticsDashboard(analytics);
            } catch (error) {
                console.error('Failed to update analytics:', error);
            }
        }, 30000);
    }

    async getAnalyticsData() {
        try {
            const [dashboard, metrics, charts] = await Promise.all([
                this.apiRequest('/api/analytics/dashboard'),
                this.apiRequest('/api/analytics/current-metrics'),
                this.apiRequest('/api/analytics/charts')
            ]);
            
            return {
                dashboard: dashboard.data,
                metrics: metrics.data,
                charts: charts.data
            };
        } catch (error) {
            console.error('Failed to get analytics data:', error);
            throw error;
        }
    }

    // ==================== REAL-TIME UPDATES ====================
    
    setupPeriodicSync() {
        // Sync tasks every 60 seconds
        setInterval(() => {
            this.syncTasks();
        }, 60000);
        
        // Sync analytics every 30 seconds
        setInterval(() => {
            this.syncAnalytics();
        }, 30000);
        
        // Sync system status every 10 seconds
        setInterval(() => {
            this.syncSystemStatus();
        }, 10000);
    }

    async syncTasks() {
        try {
            const tasks = await this.getTasks();
            this.emit('tasks:synced', tasks);
        } catch (error) {
            console.error('Failed to sync tasks:', error);
        }
    }

    async syncAnalytics() {
        try {
            const analytics = await this.getAnalyticsData();
            this.emit('analytics:synced', analytics);
        } catch (error) {
            console.error('Failed to sync analytics:', error);
        }
    }

    async syncSystemStatus() {
        try {
            const status = await this.apiRequest('/api/health');
            this.emit('system:status', status);
        } catch (error) {
            console.error('Failed to sync system status:', error);
        }
    }

    // ==================== EVENT SYSTEM ====================
    
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }

    off(event, callback) {
        if (this.eventListeners.has(event)) {
            const listeners = this.eventListeners.get(event);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }

    emit(event, data) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }

    // ==================== CACHE MANAGEMENT ====================
    
    setCache(key, value) {
        this.cache.set(key, {
            value,
            timestamp: Date.now()
        });
    }

    getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
            return cached.value;
        }
        if (cached) {
            this.cache.delete(key);
        }
        return null;
    }

    clearCache(key) {
        this.cache.delete(key);
    }

    clearCachePattern(pattern) {
        for (const key of this.cache.keys()) {
            if (key.includes(pattern)) {
                this.cache.delete(key);
            }
        }
    }

    // ==================== ERROR HANDLING ====================
    
    setupErrorHandling() {
        // Global error handler
        window.addEventListener('error', (event) => {
            this.handleError('JavaScript Error', event.error);
        });
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError('Unhandled Promise Rejection', event.reason);
        });
    }

    handleError(type, error) {
        console.error(`${type}:`, error);
        
        // Track error in analytics
        this.trackEvent('error', {
            type,
            message: error.message || error,
            stack: error.stack,
            url: window.location.href,
            timestamp: new Date().toISOString()
        });
        
        // Show user-friendly error message
        this.showNotification(`An error occurred: ${type}`, 'error');
    }

    // ==================== UTILITY METHODS ====================
    
    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.integration-notification');
        existingNotifications.forEach(notification => notification.remove());
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show integration-notification`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';
        
        notification.innerHTML = `
            <i class="bi bi-${this.getNotificationIcon(type)}"></i>
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

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    processPendingRequests() {
        const requests = [...this.pendingRequests];
        this.pendingRequests = [];
        
        requests.forEach(async ({ url, options }) => {
            try {
                await fetch(url, options);
            } catch (error) {
                console.error('Failed to process pending request:', error);
            }
        });
    }

    refreshCriticalData() {
        // Refresh tasks
        this.syncTasks();
        
        // Refresh analytics
        this.syncAnalytics();
        
        // Refresh system status
        this.syncSystemStatus();
    }

    initializePollingFallback() {
        console.log('🔄 Initializing polling fallback');
        
        // Increase polling frequency when WebSocket is unavailable
        setInterval(() => {
            this.syncTasks();
            this.syncAnalytics();
        }, 15000); // Every 15 seconds instead of 60/30
    }

    // ==================== DASHBOARD INTEGRATION ====================
    
    updateAnalyticsDashboard(analytics) {
        // Update dashboard metrics
        if (analytics.metrics) {
            this.updateDashboardMetrics(analytics.metrics);
        }
        
        // Update charts
        if (analytics.charts) {
            this.updateCharts(analytics.charts);
        }
    }

    updateDashboardMetrics(metrics) {
        // Update metric cards
        const metricElements = {
            'total-tasks': metrics.total_tasks,
            'new-tasks': metrics.new_tasks,
            'in-progress-tasks': metrics.in_progress_tasks,
            'completed-tasks': metrics.completed_tasks
        };
        
        Object.entries(metricElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element && value !== undefined) {
                element.textContent = value;
            }
        });
    }

    updateCharts(charts) {
        // This would integrate with chart libraries like Chart.js or D3.js
        console.log('Updating charts:', charts);
    }

    // ==================== TASK MANAGEMENT INTEGRATION ====================
    
    handleTaskUpdate(data) {
        // Update task in the UI
        const taskRow = document.querySelector(`tr[data-task-id="${data.task_id}"]`);
        if (taskRow) {
            // Update status
            if (data.status) {
                taskRow.dataset.status = data.status;
                const statusSelect = taskRow.querySelector('.status-select');
                if (statusSelect) {
                    statusSelect.value = data.status;
                }
            }
            
            // Update priority
            if (data.priority) {
                taskRow.dataset.priority = data.priority;
            }
            
            // Update category
            if (data.category) {
                taskRow.dataset.category = data.category;
            }
            
            // Add visual feedback
            taskRow.classList.add('task-updated');
            setTimeout(() => {
                taskRow.classList.remove('task-updated');
            }, 1000);
        }
        
        // Show notification
        this.showNotification('Task updated', 'success');
    }

    handleAnalyticsUpdate(data) {
        this.emit('analytics:realtime_update', data);
    }

    handleSystemStatusUpdate(data) {
        this.emit('system:realtime_update', data);
    }

    handleNotification(data) {
        this.showNotification(data.message, data.type || 'info');
    }

    // ==================== DESTRUCTOR ====================
    
    destroy() {
        // Close WebSocket
        if (this.websocket) {
            this.websocket.close();
        }
        
        // Close SSE
        if (this.sse) {
            this.sse.close();
        }
        
        // Clear cache
        this.cache.clear();
        
        // Clear event listeners
        this.eventListeners.clear();
        
        console.log('Integration Manager destroyed');
    }
}

// Initialize integration manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.integrationManager = new IntegrationManager();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IntegrationManager;
}
