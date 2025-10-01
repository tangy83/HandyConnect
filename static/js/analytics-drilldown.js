/**
 * Analytics Drill-down Manager
 * Handles interactive charts and filtering
 */
(function() {
    'use strict';

    const AnalyticsDrilldownManager = {
        activeFilters: new Map(),
        chartInstances: new Map(),
        breadcrumbs: null,
        timeRange: '30d',
        isInitialized: false,

        init() {
            this.createBreadcrumbContainer();
            this.setupTimeRangePicker();
            this.setupEventListeners();
            this.isInitialized = true;
        },

        createBreadcrumbContainer() {
            this.breadcrumbs = document.createElement('div');
            this.breadcrumbs.id = 'analytics-breadcrumbs';
            this.breadcrumbs.className = 'analytics-breadcrumbs mb-3';
            this.breadcrumbs.style.cssText = `
                display: none;
                padding: 0.75rem;
                background: var(--bs-light);
                border-radius: 0.375rem;
                border: 1px solid var(--bs-border-color);
            `;

            // Insert before the first chart container
            const firstChart = document.querySelector('.chart-container, .analytics-chart');
            if (firstChart) {
                firstChart.parentNode.insertBefore(this.breadcrumbs, firstChart);
            }
        },

        setupTimeRangePicker() {
            const timeRangeContainer = document.createElement('div');
            timeRangeContainer.className = 'time-range-picker mb-3';
            timeRangeContainer.innerHTML = `
                <div class="btn-group" role="group">
                    <input type="radio" class="btn-check" name="timeRange" id="today" value="today">
                    <label class="btn btn-outline-primary" for="today">Today</label>
                    
                    <input type="radio" class="btn-check" name="timeRange" id="7d" value="7d">
                    <label class="btn btn-outline-primary" for="7d">7 Days</label>
                    
                    <input type="radio" class="btn-check" name="timeRange" id="30d" value="30d" checked>
                    <label class="btn btn-outline-primary" for="30d">30 Days</label>
                    
                    <input type="radio" class="btn-check" name="timeRange" id="custom" value="custom">
                    <label class="btn btn-outline-primary" for="custom">Custom</label>
                </div>
                <button class="btn btn-outline-secondary ms-2" id="reset-drilldown">
                    <i class="bi bi-arrow-clockwise"></i> Reset
                </button>
            `;

            // Insert before breadcrumbs (with safety check)
            if (this.breadcrumbs && this.breadcrumbs.parentNode) {
                this.breadcrumbs.parentNode.insertBefore(timeRangeContainer, this.breadcrumbs);
            } else {
                // Fallback: append to body or skip if container doesn't exist
                console.warn('Analytics drilldown: breadcrumbs container not found, skipping time range picker');
            }

            // Add event listeners
            document.querySelectorAll('input[name="timeRange"]').forEach(radio => {
                radio.addEventListener('change', (e) => {
                    this.handleTimeRangeChange(e.target.value);
                });
            });

            document.getElementById('reset-drilldown').addEventListener('click', () => {
                this.resetDrilldown();
            });
        },

        setupEventListeners() {
            // Listen for chart clicks
            document.addEventListener('click', (e) => {
                if (e.target.closest('.chart-container')) {
                    this.handleChartClick(e);
                }
            });

            // Listen for URL changes
            window.addEventListener('popstate', () => {
                this.parseURLFilters();
            });

            // Initial URL parsing
            this.parseURLFilters();
        },

        handleChartClick(e) {
            const chartElement = e.target.closest('.chart-container');
            if (!chartElement) return;

            const chartId = chartElement.dataset.chartId;
            const chartType = chartElement.dataset.chartType;
            const clickedElement = e.target;

            // Get chart data and clicked segment
            const chartData = this.getChartData(chartElement);
            const clickedData = this.getClickedData(clickedElement, chartData, chartType);

            if (clickedData) {
                this.applyDrilldownFilter(chartId, clickedData);
            }
        },

        getChartData(chartElement) {
            // This would typically get data from Chart.js instance
            // For now, return mock data structure
            return {
                labels: ['Category A', 'Category B', 'Category C'],
                datasets: [{
                    data: [30, 50, 20],
                    backgroundColor: ['#007bff', '#28a745', '#ffc107']
                }]
            };
        },

        getClickedData(element, chartData, chartType) {
            // Determine what was clicked based on chart type
            if (chartType === 'pie' || chartType === 'doughnut') {
                // For pie charts, find the segment
                const segments = element.closest('canvas').parentElement.querySelectorAll('.chart-segment');
                const clickedSegment = Array.from(segments).find(seg => 
                    seg.contains(element) || element.contains(seg)
                );
                
                if (clickedSegment) {
                    const index = Array.from(segments).indexOf(clickedSegment);
                    return {
                        type: 'category',
                        value: chartData.labels[index],
                        count: chartData.datasets[0].data[index]
                    };
                }
            } else if (chartType === 'bar') {
                // For bar charts, find the bar
                const bars = element.closest('canvas').parentElement.querySelectorAll('.chart-bar');
                const clickedBar = Array.from(bars).find(bar => 
                    bar.contains(element) || element.contains(bar)
                );
                
                if (clickedBar) {
                    const index = Array.from(bars).indexOf(clickedBar);
                    return {
                        type: 'category',
                        value: chartData.labels[index],
                        count: chartData.datasets[0].data[index]
                    };
                }
            }

            return null;
        },

        applyDrilldownFilter(chartId, filterData) {
            // Add filter to active filters
            this.activeFilters.set(chartId, filterData);
            
            // Update breadcrumbs
            this.updateBreadcrumbs();
            
            // Apply filter to task list
            this.applyFiltersToTaskList();
            
            // Update URL
            this.updateURL();
            
            // Show notification
            if (window.NotificationManager) {
                window.NotificationManager.showInfo(
                    'Filter Applied', 
                    `Filtered by ${filterData.type}: ${filterData.value}`
                );
            }
        },

        updateBreadcrumbs() {
            if (this.activeFilters.size === 0) {
                this.breadcrumbs.style.display = 'none';
                return;
            }

            this.breadcrumbs.style.display = 'block';
            
            const breadcrumbItems = Array.from(this.activeFilters.entries()).map(([chartId, filter]) => `
                <span class="badge bg-primary me-2">
                    ${filter.type}: ${filter.value} (${filter.count})
                    <button class="btn-close btn-close-white ms-1" onclick="AnalyticsDrilldownManager.removeFilter('${chartId}')"></button>
                </span>
            `).join('');

            this.breadcrumbs.innerHTML = `
                <div class="d-flex align-items-center">
                    <span class="me-2">Active Filters:</span>
                    ${breadcrumbItems}
                </div>
            `;
        },

        removeFilter(chartId) {
            this.activeFilters.delete(chartId);
            this.updateBreadcrumbs();
            this.applyFiltersToTaskList();
            this.updateURL();
        },

        applyFiltersToTaskList() {
            // Apply filters to the task list
            const filters = Object.fromEntries(this.activeFilters);
            
            // Update task list with filters
            if (window.TaskManager && window.TaskManager.applyFilters) {
                window.TaskManager.applyFilters(filters);
            } else {
                // Fallback: reload page with filters
                this.reloadWithFilters();
            }
        },

        reloadWithFilters() {
            const url = new URL(window.location);
            
            // Clear existing filter params
            url.searchParams.delete('filter');
            
            // Add new filter params
            this.activeFilters.forEach((filter, chartId) => {
                url.searchParams.set(`filter_${chartId}`, `${filter.type}:${filter.value}`);
            });
            
            window.location.href = url.toString();
        },

        updateURL() {
            const url = new URL(window.location);
            
            // Clear existing filter params
            Array.from(url.searchParams.keys()).forEach(key => {
                if (key.startsWith('filter_')) {
                    url.searchParams.delete(key);
                }
            });
            
            // Add new filter params
            this.activeFilters.forEach((filter, chartId) => {
                url.searchParams.set(`filter_${chartId}`, `${filter.type}:${filter.value}`);
            });
            
            // Update URL without reload
            window.history.pushState({}, '', url.toString());
        },

        parseURLFilters() {
            const url = new URL(window.location);
            this.activeFilters.clear();
            
            // Parse filter parameters
            Array.from(url.searchParams.entries()).forEach(([key, value]) => {
                if (key.startsWith('filter_')) {
                    const chartId = key.replace('filter_', '');
                    const [type, filterValue] = value.split(':');
                    this.activeFilters.set(chartId, {
                        type: type,
                        value: filterValue,
                        count: 0 // Will be updated when data loads
                    });
                }
            });
            
            this.updateBreadcrumbs();
        },

        handleTimeRangeChange(range) {
            this.timeRange = range;
            
            if (range === 'custom') {
                this.showCustomDatePicker();
            } else {
                this.loadAnalyticsData(range);
            }
        },

        showCustomDatePicker() {
            // Create custom date picker modal
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Select Date Range</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <label class="form-label">Start Date</label>
                                    <input type="date" class="form-control" id="start-date">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">End Date</label>
                                    <input type="date" class="form-control" id="end-date">
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="apply-custom-range">Apply</button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            // Set default dates
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - 30);
            
            document.getElementById('start-date').value = startDate.toISOString().split('T')[0];
            document.getElementById('end-date').value = endDate.toISOString().split('T')[0];
            
            // Apply custom range
            document.getElementById('apply-custom-range').addEventListener('click', () => {
                const startDate = document.getElementById('start-date').value;
                const endDate = document.getElementById('end-date').value;
                
                this.loadAnalyticsData('custom', { startDate, endDate });
                bsModal.hide();
                modal.remove();
            });
        },

        async loadAnalyticsData(range, customDates = null) {
            try {
                // Show loading state
                this.showLoadingState();
                
                // Load analytics data
                const params = { range };
                if (customDates) {
                    params.startDate = customDates.startDate;
                    params.endDate = customDates.endDate;
                }
                
                const response = await API.get(`/api/analytics?${new URLSearchParams(params)}`);
                
                if (response.status === 'success') {
                    this.updateCharts(response.data);
                }
                
            } catch (error) {
                this.showErrorState(error);
            }
        },

        updateCharts(data) {
            // Update all charts with new data
            this.chartInstances.forEach((chart, chartId) => {
                if (data[chartId]) {
                    chart.data = data[chartId];
                    chart.update();
                }
            });
        },

        showLoadingState() {
            document.querySelectorAll('.chart-container').forEach(container => {
                container.innerHTML = `
                    <div class="text-center p-4">
                        <div class="spinner-border" role="status"></div>
                        <p class="mt-2">Loading analytics data...</p>
                    </div>
                `;
            });
        },

        showErrorState(error) {
            document.querySelectorAll('.chart-container').forEach(container => {
                container.innerHTML = `
                    <div class="text-center p-4">
                        <i class="bi bi-exclamation-triangle text-warning fs-1"></i>
                        <h6 class="mt-2">Error Loading Data</h6>
                        <p class="text-muted">${this.escapeHtml(error.message)}</p>
                        <button class="btn btn-outline-primary btn-sm" onclick="AnalyticsDrilldownManager.loadAnalyticsData('${this.timeRange}')">
                            <i class="bi bi-arrow-clockwise"></i> Retry
                        </button>
                    </div>
                `;
            });
        },

        resetDrilldown() {
            this.activeFilters.clear();
            this.updateBreadcrumbs();
            this.applyFiltersToTaskList();
            this.updateURL();
            
            // Reset time range to default
            document.getElementById('30d').checked = true;
            this.timeRange = '30d';
            this.loadAnalyticsData('30d');
        },

        exportDrilledDownData() {
            const filters = Object.fromEntries(this.activeFilters);
            const params = new URLSearchParams({
                ...filters,
                range: this.timeRange,
                format: 'csv'
            });
            
            window.open(`/api/analytics/export?${params.toString()}`);
        },

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };

    // Initialize when DOM is ready (only on analytics pages)
    const initIfAnalyticsPage = () => {
        // Only initialize if we're on an analytics page or if analytics elements exist
        const isAnalyticsPage = window.location.pathname.includes('/analytics') || 
                               document.querySelector('#analytics-dashboard') ||
                               document.querySelector('.analytics-container');
        
        if (isAnalyticsPage) {
            AnalyticsDrilldownManager.init();
        }
    };
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initIfAnalyticsPage);
    } else {
        initIfAnalyticsPage();
    }

    // Expose globally
    window.AnalyticsDrilldownManager = AnalyticsDrilldownManager;

})();


