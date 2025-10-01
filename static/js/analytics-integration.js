// HandyConnect Phase 11: Analytics Integration
// Real-time analytics dashboard integration with backend

class AnalyticsIntegration {
    constructor(integrationManager) {
        this.integrationManager = integrationManager;
        this.charts = new Map();
        this.metrics = {};
        this.updateInterval = 30000; // 30 seconds
        this.isInitialized = false;
        
        this.initializeAnalytics();
    }

    initializeAnalytics() {
        console.log('📊 Initializing Analytics Integration');
        
        // Set up analytics event listeners
        this.setupEventListeners();
        
        // Initialize dashboard components
        this.initializeDashboard();
        
        // Start real-time updates
        this.startRealTimeUpdates();
        
        this.isInitialized = true;
        console.log('✅ Analytics Integration initialized');
    }

    setupEventListeners() {
        // Listen for analytics updates from integration manager
        this.integrationManager.on('analytics:updated', (data) => {
            this.updateAnalytics(data);
        });
        
        this.integrationManager.on('analytics:synced', (data) => {
            this.updateAnalytics(data);
        });
        
        this.integrationManager.on('analytics:realtime_update', (data) => {
            this.handleRealtimeUpdate(data);
        });
        
        // Listen for task updates that affect analytics
        this.integrationManager.on('task:updated', (data) => {
            this.handleTaskUpdate(data);
        });
        
        this.integrationManager.on('task:deleted', (data) => {
            this.handleTaskDeletion(data);
        });
    }

    async initializeDashboard() {
        try {
            // Load initial analytics data
            const analyticsData = await this.loadAnalyticsData();
            
            // Initialize dashboard components
            this.initializeMetricsCards(analyticsData.metrics);
            this.initializeCharts(analyticsData.charts);
            this.initializeRealTimeMetrics(analyticsData.realtime);
            
            // Set up auto-refresh
            this.setupAutoRefresh();
            
        } catch (error) {
            console.error('Failed to initialize analytics dashboard:', error);
            this.showAnalyticsError('Failed to load analytics data');
        }
    }

    async loadAnalyticsData() {
        const endpoints = [
            '/api/analytics/current-metrics',
            '/api/analytics/charts',
            '/api/analytics/report',
            '/api/realtime/dashboard/live'
        ];
        
        const requests = endpoints.map(endpoint => 
            this.integrationManager.apiRequest(endpoint)
        );
        
        const results = await Promise.allSettled(requests);
        
        return {
            metrics: results[0].status === 'fulfilled' ? results[0].value.data : {},
            charts: results[1].status === 'fulfilled' ? results[1].value.data : {},
            report: results[2].status === 'fulfilled' ? results[2].value.data : {},
            realtime: results[3].status === 'fulfilled' ? results[3].value.data : {}
        };
    }

    initializeMetricsCards(metrics) {
        const metricCards = {
            'total-tasks': metrics.total_tasks || 0,
            'new-tasks': metrics.new_tasks || 0,
            'in-progress-tasks': metrics.in_progress_tasks || 0,
            'completed-tasks': metrics.completed_tasks || 0,
            'avg-response-time': metrics.avg_response_time || 0,
            'satisfaction-score': metrics.satisfaction_score || 0
        };
        
        Object.entries(metricCards).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                this.animateValue(element, 0, value, 1000);
            }
        });
        
        // Store metrics for later updates
        this.metrics = metrics;
    }

    initializeCharts(chartsData) {
        // Initialize Chart.js charts if available
        if (typeof Chart !== 'undefined') {
            this.initializeChartJSDashboard(chartsData);
        } else {
            // Fallback to basic HTML charts
            this.initializeHTMLCharts(chartsData);
        }
    }

    initializeChartJSDashboard(chartsData) {
        // Task Status Chart
        if (chartsData.task_status && document.getElementById('taskStatusChart')) {
            const ctx = document.getElementById('taskStatusChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: chartsData.task_status.labels || ['New', 'In Progress', 'Completed', 'On Hold'],
                    datasets: [{
                        data: chartsData.task_status.data || [0, 0, 0, 0],
                        backgroundColor: ['#ffc107', '#17a2b8', '#28a745', '#dc3545'],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
            this.charts.set('taskStatus', chart);
        }
        
        // Priority Distribution Chart
        if (chartsData.priority_distribution && document.getElementById('priorityChart')) {
            const ctx = document.getElementById('priorityChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: chartsData.priority_distribution.labels || ['Low', 'Medium', 'High', 'Urgent'],
                    datasets: [{
                        label: 'Tasks by Priority',
                        data: chartsData.priority_distribution.data || [0, 0, 0, 0],
                        backgroundColor: ['#6c757d', '#17a2b8', '#ffc107', '#dc3545'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            this.charts.set('priority', chart);
        }
        
        // Response Time Trend Chart
        if (chartsData.response_time_trend && document.getElementById('responseTimeChart')) {
            const ctx = document.getElementById('responseTimeChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartsData.response_time_trend.labels || [],
                    datasets: [{
                        label: 'Average Response Time (hours)',
                        data: chartsData.response_time_trend.data || [],
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Hours'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Time'
                            }
                        }
                    }
                }
            });
            this.charts.set('responseTime', chart);
        }
        
        // Performance Metrics Chart
        if (chartsData.performance_metrics && document.getElementById('performanceChart')) {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: chartsData.performance_metrics.labels || ['CPU Usage', 'Memory Usage', 'Response Time', 'Error Rate'],
                    datasets: [{
                        label: 'System Performance',
                        data: chartsData.performance_metrics.data || [0, 0, 0, 0],
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
            this.charts.set('performance', chart);
        }
    }

    initializeHTMLCharts(chartsData) {
        // Fallback HTML-based charts
        console.log('Chart.js not available, using HTML fallback');
        
        // Create simple HTML charts
        this.createHTMLChart('taskStatusChart', 'Task Status Distribution', chartsData.task_status);
        this.createHTMLChart('priorityChart', 'Priority Distribution', chartsData.priority_distribution);
        this.createHTMLChart('responseTimeChart', 'Response Time Trend', chartsData.response_time_trend);
    }

    createHTMLChart(containerId, title, data) {
        const container = document.getElementById(containerId);
        if (!container || !data) return;
        
        const chartHTML = `
            <div class="chart-container">
                <h6>${title}</h6>
                <div class="chart-data">
                    ${this.generateHTMLChartData(data)}
                </div>
            </div>
        `;
        
        container.innerHTML = chartHTML;
    }

    generateHTMLChartData(data) {
        if (!data || !data.labels || !data.data) return '<p>No data available</p>';
        
        const maxValue = Math.max(...data.data);
        
        return data.labels.map((label, index) => {
            const value = data.data[index] || 0;
            const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
            
            return `
                <div class="chart-item">
                    <div class="chart-label">${label}</div>
                    <div class="chart-bar">
                        <div class="chart-fill" style="width: ${percentage}%"></div>
                    </div>
                    <div class="chart-value">${value}</div>
                </div>
            `;
        }).join('');
    }

    initializeRealTimeMetrics(realtimeData) {
        if (realtimeData) {
            this.updateRealTimeMetrics(realtimeData);
        }
        
        // Set up real-time metrics updates
        setInterval(() => {
            this.updateRealTimeMetrics();
        }, 5000); // Update every 5 seconds
    }

    async updateRealTimeMetrics(data = null) {
        try {
            if (!data) {
                const response = await this.integrationManager.apiRequest('/api/realtime/metrics/live');
                data = response.data;
            }
            
            // Update real-time metrics display
            this.updateRealTimeDisplay(data);
            
        } catch (error) {
            console.error('Failed to update real-time metrics:', error);
        }
    }

    updateRealTimeDisplay(data) {
        const realtimeElements = {
            'active-users': data.active_users || 0,
            'system-load': data.system_load || 0,
            'response-time': data.response_time || 0,
            'error-rate': data.error_rate || 0
        };
        
        Object.entries(realtimeElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                
                // Add visual indicator for changes
                element.classList.add('metric-updated');
                setTimeout(() => {
                    element.classList.remove('metric-updated');
                }, 1000);
            }
        });
    }

    setupAutoRefresh() {
        // Auto-refresh analytics every 30 seconds
        setInterval(() => {
            this.refreshAnalytics();
        }, this.updateInterval);
    }

    async refreshAnalytics() {
        try {
            const analyticsData = await this.loadAnalyticsData();
            this.updateAnalytics(analyticsData);
        } catch (error) {
            console.error('Failed to refresh analytics:', error);
        }
    }

    updateAnalytics(data) {
        // Update metrics cards
        if (data.metrics) {
            this.updateMetricsCards(data.metrics);
        }
        
        // Update charts
        if (data.charts) {
            this.updateCharts(data.charts);
        }
        
        // Update real-time metrics
        if (data.realtime) {
            this.updateRealTimeMetrics(data.realtime);
        }
    }

    updateMetricsCards(metrics) {
        const metricCards = {
            'total-tasks': metrics.total_tasks,
            'new-tasks': metrics.new_tasks,
            'in-progress-tasks': metrics.in_progress_tasks,
            'completed-tasks': metrics.completed_tasks,
            'avg-response-time': metrics.avg_response_time,
            'satisfaction-score': metrics.satisfaction_score
        };
        
        Object.entries(metricCards).forEach(([id, value]) => {
            if (value !== undefined) {
                const element = document.getElementById(id);
                if (element) {
                    const currentValue = parseInt(element.textContent) || 0;
                    if (currentValue !== value) {
                        this.animateValue(element, currentValue, value, 500);
                    }
                }
            }
        });
        
        this.metrics = { ...this.metrics, ...metrics };
    }

    updateCharts(chartsData) {
        // Update Chart.js charts
        if (chartsData.task_status && this.charts.has('taskStatus')) {
            const chart = this.charts.get('taskStatus');
            chart.data.datasets[0].data = chartsData.task_status.data || [];
            chart.update('active');
        }
        
        if (chartsData.priority_distribution && this.charts.has('priority')) {
            const chart = this.charts.get('priority');
            chart.data.datasets[0].data = chartsData.priority_distribution.data || [];
            chart.update('active');
        }
        
        if (chartsData.response_time_trend && this.charts.has('responseTime')) {
            const chart = this.charts.get('responseTime');
            chart.data.labels = chartsData.response_time_trend.labels || [];
            chart.data.datasets[0].data = chartsData.response_time_trend.data || [];
            chart.update('active');
        }
        
        if (chartsData.performance_metrics && this.charts.has('performance')) {
            const chart = this.charts.get('performance');
            chart.data.datasets[0].data = chartsData.performance_metrics.data || [];
            chart.update('active');
        }
        
        // Update HTML fallback charts
        if (typeof Chart === 'undefined') {
            this.createHTMLChart('taskStatusChart', 'Task Status Distribution', chartsData.task_status);
            this.createHTMLChart('priorityChart', 'Priority Distribution', chartsData.priority_distribution);
        }
    }

    handleRealtimeUpdate(data) {
        // Handle real-time analytics updates
        switch (data.type) {
            case 'metric_update':
                this.handleMetricUpdate(data.payload);
                break;
            case 'chart_update':
                this.handleChartUpdate(data.payload);
                break;
            case 'alert':
                this.handleAnalyticsAlert(data.payload);
                break;
            default:
                console.log('Unknown real-time analytics update:', data.type);
        }
    }

    handleMetricUpdate(payload) {
        const element = document.getElementById(payload.metric_id);
        if (element) {
            this.animateValue(element, parseInt(element.textContent) || 0, payload.value, 300);
        }
    }

    handleChartUpdate(payload) {
        if (this.charts.has(payload.chart_id)) {
            const chart = this.charts.get(payload.chart_id);
            chart.data.datasets[0].data = payload.data;
            chart.update('active');
        }
    }

    handleAnalyticsAlert(payload) {
        this.integrationManager.showNotification(payload.message, payload.severity || 'warning');
        
        // Show alert in analytics dashboard
        this.showAnalyticsAlert(payload);
    }

    handleTaskUpdate(data) {
        // Update analytics when tasks are updated
        this.refreshAnalytics();
    }

    handleTaskDeletion(data) {
        // Update analytics when tasks are deleted
        this.refreshAnalytics();
    }

    // ==================== UTILITY METHODS ====================
    
    animateValue(element, start, end, duration) {
        const startTime = performance.now();
        const isNumeric = typeof end === 'number';
        
        const updateValue = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            
            let currentValue;
            if (isNumeric) {
                currentValue = Math.round(start + (end - start) * easeOutQuart);
                element.textContent = currentValue;
            } else {
                element.textContent = end;
            }
            
            if (progress < 1) {
                requestAnimationFrame(updateValue);
            }
        };
        
        requestAnimationFrame(updateValue);
    }

    showAnalyticsError(message) {
        const errorContainer = document.getElementById('analytics-error') || this.createErrorContainer();
        errorContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                ${message}
                <button type="button" class="btn btn-sm btn-outline-danger ms-2" onclick="this.parentElement.parentElement.remove()">
                    Dismiss
                </button>
            </div>
        `;
    }

    createErrorContainer() {
        const container = document.createElement('div');
        container.id = 'analytics-error';
        container.style.position = 'fixed';
        container.style.top = '80px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    showAnalyticsAlert(payload) {
        const alertContainer = document.getElementById('analytics-alerts') || this.createAlertContainer();
        
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${payload.severity || 'warning'} alert-dismissible fade show`;
        alertElement.innerHTML = `
            <i class="bi bi-${this.getAlertIcon(payload.severity)}"></i>
            <strong>${payload.title || 'Analytics Alert'}</strong><br>
            ${payload.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertContainer.appendChild(alertElement);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (alertElement.parentNode) {
                alertElement.remove();
            }
        }, 10000);
    }

    createAlertContainer() {
        const container = document.createElement('div');
        container.id = 'analytics-alerts';
        container.style.position = 'fixed';
        container.style.top = '80px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        container.style.maxWidth = '400px';
        document.body.appendChild(container);
        return container;
    }

    getAlertIcon(severity) {
        const icons = {
            critical: 'exclamation-triangle-fill',
            warning: 'exclamation-triangle',
            info: 'info-circle',
            success: 'check-circle'
        };
        return icons[severity] || 'info-circle';
    }

    // ==================== EXPORT DATA ====================
    
    async exportAnalyticsData(format = 'json') {
        try {
            const response = await this.integrationManager.apiRequest('/api/analytics/admin/export', {
                method: 'POST',
                body: JSON.stringify({ format })
            });
            
            if (response.status === 'success') {
                this.downloadFile(response.data, `analytics-export-${new Date().toISOString().split('T')[0]}.${format}`);
                this.integrationManager.showNotification('Analytics data exported successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to export analytics data:', error);
            this.integrationManager.showNotification('Failed to export analytics data', 'error');
        }
    }

    downloadFile(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    // ==================== DESTRUCTOR ====================
    
    destroy() {
        // Destroy all charts
        this.charts.forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts.clear();
        
        // Clear metrics
        this.metrics = {};
        
        this.isInitialized = false;
        console.log('Analytics Integration destroyed');
    }
}

// Initialize analytics integration when integration manager is available
document.addEventListener('DOMContentLoaded', () => {
    if (window.integrationManager) {
        window.analyticsIntegration = new AnalyticsIntegration(window.integrationManager);
    } else {
        // Wait for integration manager to be ready
        const checkIntegrationManager = setInterval(() => {
            if (window.integrationManager) {
                clearInterval(checkIntegrationManager);
                window.analyticsIntegration = new AnalyticsIntegration(window.integrationManager);
            }
        }, 100);
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AnalyticsIntegration;
}
