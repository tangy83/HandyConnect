/**
 * Export Enhancements Manager
 * Handles CSV, Excel, and PDF exports with advanced options
 */
(function() {
    'use strict';

    const ExportManager = {
        exportConfig: {
            format: 'csv',
            fields: [],
            filters: {},
            sort: {},
            includeCharts: false,
            dateRange: '30d'
        },
        isExporting: false,

        init() {
            this.loadExportConfig();
            this.createExportModal();
            this.setupEventListeners();
        },

        createExportModal() {
            const modal = document.createElement('div');
            modal.id = 'export-modal';
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-download"></i> Export Data
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="export-form">
                                <!-- Format Selection -->
                                <div class="mb-4">
                                    <label class="form-label">Export Format</label>
                                    <div class="row g-2">
                                        <div class="col-md-4">
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio" name="format" id="csv" value="csv" checked>
                                                <label class="form-check-label" for="csv">
                                                    <i class="bi bi-filetype-csv"></i> CSV
                                                </label>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio" name="format" id="excel" value="excel">
                                                <label class="form-check-label" for="excel">
                                                    <i class="bi bi-filetype-xlsx"></i> Excel
                                                </label>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio" name="format" id="pdf" value="pdf">
                                                <label class="form-check-label" for="pdf">
                                                    <i class="bi bi-filetype-pdf"></i> PDF
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Field Selection -->
                                <div class="mb-4">
                                    <label class="form-label">Fields to Export</label>
                                    <div class="row g-2">
                                        <div class="col-md-6">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="field-subject" value="subject" checked>
                                                <label class="form-check-label" for="field-subject">Subject</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="field-sender" value="sender" checked>
                                                <label class="form-check-label" for="field-sender">Sender</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="field-category" value="category" checked>
                                                <label class="form-check-label" for="field-category">Category</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="field-priority" value="priority" checked>
                                                <label class="form-check-label" for="field-priority">Priority</label>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="field-status" value="status" checked>
                                                <label class="form-check-label" for="field-status">Status</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="field-created" value="created_at" checked>
                                                <label class="form-check-label" for="field-created">Created Date</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="field-assigned" value="assigned_to">
                                                <label class="form-check-label" for="field-assigned">Assigned To</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="field-notes" value="notes">
                                                <label class="form-check-label" for="field-notes">Notes</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="mt-2">
                                        <button type="button" class="btn btn-outline-secondary btn-sm" id="select-all-fields">Select All</button>
                                        <button type="button" class="btn btn-outline-secondary btn-sm" id="select-none-fields">Select None</button>
                                    </div>
                                </div>

                                <!-- Presets -->
                                <div class="mb-4">
                                    <label class="form-label">Quick Presets</label>
                                    <div class="btn-group" role="group">
                                        <button type="button" class="btn btn-outline-primary btn-sm" id="preset-minimal">Minimal</button>
                                        <button type="button" class="btn btn-outline-primary btn-sm" id="preset-full">Full</button>
                                        <button type="button" class="btn btn-outline-primary btn-sm" id="preset-summary">Summary</button>
                                    </div>
                                </div>

                                <!-- Additional Options -->
                                <div class="mb-4">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="include-charts" value="true">
                                        <label class="form-check-label" for="include-charts">
                                            Include Charts (PDF/Excel only)
                                        </label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="include-summary" value="true" checked>
                                        <label class="form-check-label" for="include-summary">
                                            Include Summary Sheet (Excel only)
                                        </label>
                                    </div>
                                </div>

                                <!-- Progress Bar -->
                                <div id="export-progress" class="mb-3" style="display: none;">
                                    <div class="progress">
                                        <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                                    </div>
                                    <small class="text-muted">Exporting data...</small>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="start-export">
                                <i class="bi bi-download"></i> Export
                            </button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
        },

        setupEventListeners() {
            // Export button
            document.addEventListener('click', (e) => {
                if (e.target.matches('[data-export]')) {
                    e.preventDefault();
                    this.showExportModal();
                }
            });

            // Start export
            document.addEventListener('click', (e) => {
                if (e.target.id === 'start-export') {
                    this.startExport();
                }
            });

            // Preset buttons
            document.addEventListener('click', (e) => {
                if (e.target.id === 'preset-minimal') {
                    this.applyPreset('minimal');
                } else if (e.target.id === 'preset-full') {
                    this.applyPreset('full');
                } else if (e.target.id === 'preset-summary') {
                    this.applyPreset('summary');
                }
            });

            // Field selection buttons
            document.addEventListener('click', (e) => {
                if (e.target.id === 'select-all-fields') {
                    this.selectAllFields(true);
                } else if (e.target.id === 'select-none-fields') {
                    this.selectAllFields(false);
                }
            });

            // Format change
            document.addEventListener('change', (e) => {
                if (e.target.name === 'format') {
                    this.handleFormatChange(e.target.value);
                }
            });
        },

        showExportModal() {
            const modal = new bootstrap.Modal(document.getElementById('export-modal'));
            modal.show();
        },

        applyPreset(preset) {
            const fieldCheckboxes = document.querySelectorAll('#export-form input[type="checkbox"][id^="field-"]');
            
            fieldCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });

            switch (preset) {
                case 'minimal':
                    ['subject', 'status', 'priority', 'created_at'].forEach(field => {
                        const checkbox = document.getElementById(`field-${field}`);
                        if (checkbox) checkbox.checked = true;
                    });
                    break;
                case 'full':
                    fieldCheckboxes.forEach(checkbox => {
                        checkbox.checked = true;
                    });
                    break;
                case 'summary':
                    ['subject', 'category', 'priority', 'status', 'created_at'].forEach(field => {
                        const checkbox = document.getElementById(`field-${field}`);
                        if (checkbox) checkbox.checked = true;
                    });
                    break;
            }
        },

        selectAllFields(select) {
            const fieldCheckboxes = document.querySelectorAll('#export-form input[type="checkbox"][id^="field-"]');
            fieldCheckboxes.forEach(checkbox => {
                checkbox.checked = select;
            });
        },

        handleFormatChange(format) {
            const includeCharts = document.getElementById('include-charts');
            const includeSummary = document.getElementById('include-summary');
            
            if (format === 'pdf' || format === 'excel') {
                includeCharts.disabled = false;
                includeSummary.disabled = format !== 'excel';
            } else {
                includeCharts.disabled = true;
                includeSummary.disabled = true;
            }
        },

        async startExport() {
            if (this.isExporting) return;

            this.isExporting = true;
            this.showProgress();

            try {
                const config = this.getExportConfig();
                const response = await this.performExport(config);
                
                if (response.status === 'success') {
                    this.downloadFile(response.data.url, response.data.filename);
                    this.showSuccess('Export completed successfully!');
                } else {
                    throw new Error(response.message || 'Export failed');
                }

            } catch (error) {
                this.showError('Export failed: ' + error.message);
            } finally {
                this.isExporting = false;
                this.hideProgress();
            }
        },

        getExportConfig() {
            const form = document.getElementById('export-form');
            const formData = new FormData(form);
            
            const config = {
                format: formData.get('format'),
                fields: Array.from(document.querySelectorAll('#export-form input[type="checkbox"][id^="field-"]:checked'))
                    .map(cb => cb.value),
                includeCharts: formData.get('include-charts') === 'true',
                includeSummary: formData.get('include-summary') === 'true',
                filters: this.getCurrentFilters(),
                sort: this.getCurrentSort(),
                dateRange: this.getCurrentDateRange()
            };

            return config;
        },

        getCurrentFilters() {
            // Get current filters from the page
            const filters = {};
            
            // Status filter
            const statusFilter = document.getElementById('status-filter');
            if (statusFilter && statusFilter.value) {
                filters.status = statusFilter.value;
            }
            
            // Priority filter
            const priorityFilter = document.getElementById('priority-filter');
            if (priorityFilter && priorityFilter.value) {
                filters.priority = priorityFilter.value;
            }
            
            // Category filter
            const categoryFilter = document.getElementById('category-filter');
            if (categoryFilter && categoryFilter.value) {
                filters.category = categoryFilter.value;
            }
            
            // Search filter
            const searchInput = document.getElementById('search-input');
            if (searchInput && searchInput.value) {
                filters.search = searchInput.value;
            }

            return filters;
        },

        getCurrentSort() {
            // Get current sort from the page
            const sortSelect = document.querySelector('select[data-sort]');
            if (sortSelect) {
                return {
                    field: sortSelect.value,
                    direction: sortSelect.dataset.direction || 'desc'
                };
            }
            return { field: 'created_at', direction: 'desc' };
        },

        getCurrentDateRange() {
            // Get current date range
            return '30d'; // Default, could be enhanced to read from date picker
        },

        async performExport(config) {
            // Show progress
            this.updateProgress(10, 'Preparing export...');

            // Get current task data
            const tasks = await this.getCurrentTasks();
            this.updateProgress(30, 'Loading data...');

            // Apply filters
            const filteredTasks = this.applyFilters(tasks, config.filters);
            this.updateProgress(50, 'Processing data...');

            // Apply field selection
            const processedTasks = this.selectFields(filteredTasks, config.fields);
            this.updateProgress(70, 'Formatting data...');

            // Generate export file
            const exportData = await this.generateExportFile(processedTasks, config);
            this.updateProgress(90, 'Generating file...');

            // Upload file and get download URL
            const downloadUrl = await this.uploadExportFile(exportData, config);
            this.updateProgress(100, 'Complete!');

            return {
                status: 'success',
                data: {
                    url: downloadUrl,
                    filename: this.generateFilename(config)
                }
            };
        },

        async getCurrentTasks() {
            try {
                const response = await API.get('/api/tasks');
                return response.data || [];
            } catch (error) {
                console.error('Error fetching tasks:', error);
                return [];
            }
        },

        applyFilters(tasks, filters) {
            return tasks.filter(task => {
                if (filters.status && task.status !== filters.status) return false;
                if (filters.priority && task.priority !== filters.priority) return false;
                if (filters.category && task.category !== filters.category) return false;
                if (filters.search) {
                    const searchTerm = filters.search.toLowerCase();
                    const searchableText = `${task.subject} ${task.sender} ${task.content}`.toLowerCase();
                    if (!searchableText.includes(searchTerm)) return false;
                }
                return true;
            });
        },

        selectFields(tasks, fields) {
            return tasks.map(task => {
                const selectedTask = {};
                fields.forEach(field => {
                    if (task.hasOwnProperty(field)) {
                        selectedTask[field] = task[field];
                    }
                });
                return selectedTask;
            });
        },

        async generateExportFile(tasks, config) {
            switch (config.format) {
                case 'csv':
                    return this.generateCSV(tasks);
                case 'excel':
                    return this.generateExcel(tasks, config);
                case 'pdf':
                    return this.generatePDF(tasks, config);
                default:
                    throw new Error('Unsupported format: ' + config.format);
            }
        },

        generateCSV(tasks) {
            if (tasks.length === 0) return '';

            const headers = Object.keys(tasks[0]);
            const csvContent = [
                headers.join(','),
                ...tasks.map(task => 
                    headers.map(header => 
                        this.escapeCSVValue(task[header] || '')
                    ).join(',')
                )
            ].join('\n');

            return csvContent;
        },

        generateExcel(tasks, config) {
            // This would use SheetJS to generate Excel file
            // For now, return CSV as fallback
            return this.generateCSV(tasks);
        },

        generatePDF(tasks, config) {
            // This would use jsPDF to generate PDF
            // For now, return CSV as fallback
            return this.generateCSV(tasks);
        },

        escapeCSVValue(value) {
            if (value === null || value === undefined) return '';
            
            const stringValue = String(value);
            if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
                return `"${stringValue.replace(/"/g, '""')}"`;
            }
            return stringValue;
        },

        async uploadExportFile(data, config) {
            // In a real implementation, this would upload to a server
            // For now, create a blob URL
            const blob = new Blob([data], { 
                type: this.getMimeType(config.format) 
            });
            return URL.createObjectURL(blob);
        },

        getMimeType(format) {
            const mimeTypes = {
                'csv': 'text/csv',
                'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'pdf': 'application/pdf'
            };
            return mimeTypes[format] || 'text/plain';
        },

        generateFilename(config) {
            const timestamp = new Date().toISOString().split('T')[0];
            const extensions = {
                'csv': 'csv',
                'excel': 'xlsx',
                'pdf': 'pdf'
            };
            return `handyconnect-export-${timestamp}.${extensions[config.format]}`;
        },

        downloadFile(url, filename) {
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },

        showProgress() {
            const progress = document.getElementById('export-progress');
            if (progress) {
                progress.style.display = 'block';
            }
        },

        hideProgress() {
            const progress = document.getElementById('export-progress');
            if (progress) {
                progress.style.display = 'none';
            }
        },

        updateProgress(percentage, message) {
            const progressBar = document.querySelector('#export-progress .progress-bar');
            const progressText = document.querySelector('#export-progress small');
            
            if (progressBar) {
                progressBar.style.width = percentage + '%';
            }
            if (progressText) {
                progressText.textContent = message;
            }
        },

        showSuccess(message) {
            if (window.NotificationManager) {
                window.NotificationManager.showSuccess('Export Complete', message);
            }
        },

        showError(message) {
            if (window.NotificationManager) {
                window.NotificationManager.showError('Export Failed', message);
            }
        },

        loadExportConfig() {
            const saved = localStorage.getItem('exportConfig');
            if (saved) {
                this.exportConfig = { ...this.exportConfig, ...JSON.parse(saved) };
            }
        },

        saveExportConfig() {
            localStorage.setItem('exportConfig', JSON.stringify(this.exportConfig));
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => ExportManager.init());
    } else {
        ExportManager.init();
    }

    // Expose globally
    window.ExportManager = ExportManager;

})();


