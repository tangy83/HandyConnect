/**
 * Advanced Search Manager
 * Handles boolean queries, field filters, and autocomplete
 */
(function() {
    'use strict';

    const AdvancedSearchManager = {
        searchInput: null,
        suggestionsContainer: null,
        queryChips: [],
        recentSearches: [],
        savedSearches: [],
        isInitialized: false,

        // Searchable fields
        fields: {
            'status': { type: 'select', values: ['New', 'In Progress', 'Completed', 'On Hold'] },
            'priority': { type: 'select', values: ['Low', 'Medium', 'High', 'Urgent'] },
            'category': { type: 'select', values: ['Technical Issue', 'Billing Question', 'Feature Request', 'Complaint', 'General Inquiry', 'Account Issue'] },
            'assignee': { type: 'text', values: [] },
            'resident': { type: 'text', values: [] },
            'has:attachment': { type: 'boolean', values: ['true', 'false'] },
            'sentiment': { type: 'select', values: ['Positive', 'Neutral', 'Negative', 'Frustrated'] }
        },

        // Query operators
        operators: ['AND', 'OR', 'NOT'],

        init() {
            this.loadSavedSearches();
            this.createSearchInterface();
            this.setupEventListeners();
            this.isInitialized = true;
        },

        createSearchInterface() {
            // Find existing search input or create one
            this.searchInput = document.getElementById('search-input');
            if (!this.searchInput) {
                this.searchInput = document.createElement('input');
                this.searchInput.id = 'search-input';
                this.searchInput.type = 'text';
                this.searchInput.className = 'form-control';
                this.searchInput.placeholder = 'Search tasks... (try: status:New AND priority:High)';
            }

            // Create suggestions container
            this.suggestionsContainer = document.createElement('div');
            this.suggestionsContainer.id = 'search-suggestions';
            this.suggestionsContainer.className = 'search-suggestions';
            this.suggestionsContainer.style.cssText = `
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 0.375rem 0.375rem;
                max-height: 300px;
                overflow-y: auto;
                z-index: 1000;
                display: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            `;

            // Create query chips container
            const chipsContainer = document.createElement('div');
            chipsContainer.id = 'query-chips';
            chipsContainer.className = 'query-chips mt-2';
            chipsContainer.style.cssText = `
                display: flex;
                flex-wrap: wrap;
                gap: 0.25rem;
                min-height: 2rem;
            `;

            // Wrap search input in relative container
            const searchContainer = this.searchInput.parentElement || document.querySelector('.search-container');
            if (searchContainer) {
                searchContainer.style.position = 'relative';
                searchContainer.appendChild(this.suggestionsContainer);
                searchContainer.appendChild(chipsContainer);
            }

            // Add search controls
            this.addSearchControls();
        },

        addSearchControls() {
            const controlsContainer = document.createElement('div');
            controlsContainer.className = 'search-controls mt-2';
            controlsContainer.innerHTML = `
                <div class="row g-2">
                    <div class="col-md-8">
                        <div class="btn-group btn-group-sm" role="group">
                            <button class="btn btn-outline-secondary" id="search-help" title="Search Help">
                                <i class="bi bi-question-circle"></i>
                            </button>
                            <button class="btn btn-outline-secondary" id="clear-search" title="Clear Search">
                                <i class="bi bi-x-circle"></i>
                            </button>
                            <button class="btn btn-outline-secondary" id="save-search" title="Save Search" disabled>
                                <i class="bi bi-bookmark"></i>
                            </button>
                        </div>
                        <div class="btn-group btn-group-sm ms-2" role="group">
                            <button class="btn btn-outline-primary" id="recent-searches" title="Recent Searches">
                                <i class="bi bi-clock-history"></i>
                            </button>
                            <button class="btn btn-outline-primary" id="saved-searches" title="Saved Searches">
                                <i class="bi bi-bookmark-star"></i>
                            </button>
                        </div>
                    </div>
                    <div class="col-md-4 text-end">
                        <small class="text-muted" id="search-results-count">0 results</small>
                    </div>
                </div>
            `;

            this.searchInput.parentElement.appendChild(controlsContainer);
        },

        setupEventListeners() {
            // Search input events
            this.searchInput.addEventListener('input', this.debounce((e) => {
                this.handleSearchInput(e.target.value);
            }, 300));

            this.searchInput.addEventListener('keydown', (e) => {
                this.handleSearchKeydown(e);
            });

            this.searchInput.addEventListener('focus', () => {
                this.showSuggestions();
            });

            this.searchInput.addEventListener('blur', (e) => {
                // Delay hiding to allow clicking on suggestions
                setTimeout(() => {
                    this.hideSuggestions();
                }, 200);
            });

            // Control buttons
            document.addEventListener('click', (e) => {
                if (e.target.id === 'search-help') {
                    this.showSearchHelp();
                } else if (e.target.id === 'clear-search') {
                    this.clearSearch();
                } else if (e.target.id === 'save-search') {
                    this.saveCurrentSearch();
                } else if (e.target.id === 'recent-searches') {
                    this.showRecentSearches();
                } else if (e.target.id === 'saved-searches') {
                    this.showSavedSearches();
                }
            });

            // Suggestion clicks
            this.suggestionsContainer.addEventListener('click', (e) => {
                if (e.target.classList.contains('suggestion-item')) {
                    this.selectSuggestion(e.target);
                }
            });
        },

        handleSearchInput(query) {
            if (query.length < 2) {
                this.hideSuggestions();
                return;
            }

            this.parseQuery(query);
            this.showSuggestions();
            this.updateQueryChips();
        },

        parseQuery(query) {
            // Simple query parser for field:value syntax
            const tokens = query.split(/\s+/);
            this.queryChips = [];

            tokens.forEach(token => {
                if (token.includes(':')) {
                    const [field, value] = token.split(':', 2);
                    if (this.fields[field]) {
                        this.queryChips.push({
                            type: 'field',
                            field: field,
                            value: value,
                            display: `${field}:${value}`
                        });
                    }
                } else if (this.operators.includes(token.toUpperCase())) {
                    this.queryChips.push({
                        type: 'operator',
                        value: token.toUpperCase(),
                        display: token.toUpperCase()
                    });
                } else if (token.length > 0) {
                    this.queryChips.push({
                        type: 'text',
                        value: token,
                        display: token
                    });
                }
            });
        },

        showSuggestions() {
            const query = this.searchInput.value;
            const cursorPos = this.searchInput.selectionStart;
            const currentToken = this.getCurrentToken(query, cursorPos);

            if (currentToken.length < 1) {
                this.hideSuggestions();
                return;
            }

            const suggestions = this.generateSuggestions(currentToken, query, cursorPos);
            this.renderSuggestions(suggestions);
        },

        getCurrentToken(query, cursorPos) {
            const beforeCursor = query.substring(0, cursorPos);
            const tokens = beforeCursor.split(/\s+/);
            return tokens[tokens.length - 1] || '';
        },

        generateSuggestions(token, fullQuery, cursorPos) {
            const suggestions = [];

            // Field suggestions
            if (token.includes(':')) {
                const [field, value] = token.split(':', 2);
                if (this.fields[field]) {
                    const fieldConfig = this.fields[field];
                    fieldConfig.values.forEach(val => {
                        if (val.toLowerCase().includes(value.toLowerCase())) {
                            suggestions.push({
                                type: 'field-value',
                                field: field,
                                value: val,
                                display: `${field}:${val}`,
                                description: `Filter by ${field} = ${val}`
                            });
                        }
                    });
                }
            } else {
                // Field name suggestions
                Object.keys(this.fields).forEach(field => {
                    if (field.toLowerCase().includes(token.toLowerCase())) {
                        suggestions.push({
                            type: 'field',
                            field: field,
                            display: field,
                            description: `Filter by ${field}`
                        });
                    }
                });

                // Operator suggestions
                this.operators.forEach(op => {
                    if (op.toLowerCase().includes(token.toLowerCase())) {
                        suggestions.push({
                            type: 'operator',
                            value: op,
                            display: op,
                            description: `Logical operator: ${op}`
                        });
                    }
                });

                // Recent searches
                this.recentSearches.forEach(search => {
                    if (search.toLowerCase().includes(token.toLowerCase())) {
                        suggestions.push({
                            type: 'recent',
                            value: search,
                            display: search,
                            description: 'Recent search'
                        });
                    }
                });
            }

            return suggestions.slice(0, 10); // Limit to 10 suggestions
        },

        renderSuggestions(suggestions) {
            if (suggestions.length === 0) {
                this.hideSuggestions();
                return;
            }

            const html = suggestions.map(suggestion => `
                <div class="suggestion-item p-2 border-bottom" data-type="${suggestion.type}" data-value="${this.escapeHtml(suggestion.value || suggestion.display)}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${this.escapeHtml(suggestion.display)}</strong>
                            <br>
                            <small class="text-muted">${suggestion.description}</small>
                        </div>
                        <i class="bi bi-arrow-right"></i>
                    </div>
                </div>
            `).join('');

            this.suggestionsContainer.innerHTML = html;
            this.suggestionsContainer.style.display = 'block';
        },

        selectSuggestion(element) {
            const value = element.dataset.value;
            const currentQuery = this.searchInput.value;
            const cursorPos = this.searchInput.selectionStart;
            
            // Replace current token with suggestion
            const beforeCursor = currentQuery.substring(0, cursorPos);
            const afterCursor = currentQuery.substring(cursorPos);
            const tokens = beforeCursor.split(/\s+/);
            tokens[tokens.length - 1] = value;
            
            const newQuery = tokens.join(' ') + (afterCursor ? ' ' + afterCursor : '');
            this.searchInput.value = newQuery;
            
            this.hideSuggestions();
            this.searchInput.focus();
            
            // Trigger search
            this.performSearch(newQuery);
        },

        hideSuggestions() {
            this.suggestionsContainer.style.display = 'none';
        },

        handleSearchKeydown(e) {
            switch (e.key) {
                case 'Enter':
                    e.preventDefault();
                    this.performSearch(this.searchInput.value);
                    break;
                case 'Escape':
                    this.hideSuggestions();
                    this.searchInput.blur();
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    this.navigateSuggestions(1);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.navigateSuggestions(-1);
                    break;
            }
        },

        navigateSuggestions(direction) {
            const suggestions = this.suggestionsContainer.querySelectorAll('.suggestion-item');
            const active = this.suggestionsContainer.querySelector('.suggestion-item.active');
            
            if (suggestions.length === 0) return;
            
            let newIndex = 0;
            if (active) {
                const currentIndex = Array.from(suggestions).indexOf(active);
                newIndex = Math.max(0, Math.min(suggestions.length - 1, currentIndex + direction));
            }
            
            suggestions.forEach((s, i) => s.classList.toggle('active', i === newIndex));
        },

        updateQueryChips() {
            const container = document.getElementById('query-chips');
            if (!container) return;

            container.innerHTML = this.queryChips.map(chip => `
                <span class="badge bg-primary d-inline-flex align-items-center">
                    ${this.escapeHtml(chip.display)}
                    <button type="button" class="btn-close btn-close-white ms-1" onclick="AdvancedSearchManager.removeChip('${chip.display}')"></button>
                </span>
            `).join('');
        },

        removeChip(chipDisplay) {
            const chipIndex = this.queryChips.findIndex(chip => chip.display === chipDisplay);
            if (chipIndex !== -1) {
                this.queryChips.splice(chipIndex, 1);
                this.updateQueryChips();
                this.updateSearchInput();
            }
        },

        updateSearchInput() {
            const query = this.queryChips.map(chip => chip.display).join(' ');
            this.searchInput.value = query;
        },

        async performSearch(query) {
            if (!query.trim()) {
                this.clearSearch();
                return;
            }

            try {
                // Add to recent searches
                this.addToRecentSearches(query);

                // Parse query into API parameters
                const searchParams = this.parseQueryToParams(query);

                // Perform search
                const response = await API.get(`/api/tasks/search?${new URLSearchParams(searchParams)}`);
                
                if (response.status === 'success') {
                    this.updateSearchResults(response.data);
                    this.updateResultsCount(response.data.length);
                }

            } catch (error) {
                console.error('Search error:', error);
                if (window.NotificationManager) {
                    window.NotificationManager.showError('Search Failed', error.message);
                }
            }
        },

        parseQueryToParams(query) {
            const params = {};
            const tokens = query.split(/\s+/);

            tokens.forEach(token => {
                if (token.includes(':')) {
                    const [field, value] = token.split(':', 2);
                    if (this.fields[field]) {
                        params[field] = value;
                    }
                } else if (!this.operators.includes(token.toUpperCase())) {
                    // Text search
                    if (!params.search) {
                        params.search = token;
                    } else {
                        params.search += ' ' + token;
                    }
                }
            });

            return params;
        },

        updateSearchResults(results) {
            // Update the task list with search results
            if (window.TaskManager && window.TaskManager.updateTaskList) {
                window.TaskManager.updateTaskList(results);
            }
        },

        updateResultsCount(count) {
            const countElement = document.getElementById('search-results-count');
            if (countElement) {
                countElement.textContent = `${count} result${count !== 1 ? 's' : ''}`;
            }
        },

        clearSearch() {
            this.searchInput.value = '';
            this.queryChips = [];
            this.updateQueryChips();
            this.hideSuggestions();
            this.updateResultsCount(0);
            
            // Reset task list
            if (window.TaskManager && window.TaskManager.resetTaskList) {
                window.TaskManager.resetTaskList();
            }
        },

        addToRecentSearches(query) {
            // Remove if already exists
            this.recentSearches = this.recentSearches.filter(q => q !== query);
            
            // Add to beginning
            this.recentSearches.unshift(query);
            
            // Keep only last 10
            this.recentSearches = this.recentSearches.slice(0, 10);
            
            // Save to localStorage
            localStorage.setItem('recentSearches', JSON.stringify(this.recentSearches));
        },

        loadSavedSearches() {
            const saved = localStorage.getItem('savedSearches');
            if (saved) {
                this.savedSearches = JSON.parse(saved);
            }

            const recent = localStorage.getItem('recentSearches');
            if (recent) {
                this.recentSearches = JSON.parse(recent);
            }
        },

        saveCurrentSearch() {
            const query = this.searchInput.value.trim();
            if (!query) return;

            const name = prompt('Enter a name for this search:');
            if (!name) return;

            this.savedSearches.push({
                name: name,
                query: query,
                createdAt: new Date().toISOString()
            });

            localStorage.setItem('savedSearches', JSON.stringify(this.savedSearches));
            
            if (window.NotificationManager) {
                window.NotificationManager.showSuccess('Search Saved', `"${name}" has been saved`);
            }
        },

        showSearchHelp() {
            const helpModal = document.createElement('div');
            helpModal.className = 'modal fade';
            helpModal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Advanced Search Help</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <h6>Field Filters</h6>
                            <p>Use <code>field:value</code> syntax to filter by specific fields:</p>
                            <ul>
                                <li><code>status:New</code> - Tasks with status "New"</li>
                                <li><code>priority:High</code> - High priority tasks</li>
                                <li><code>category:Technical Issue</code> - Technical issues</li>
                                <li><code>assignee:John</code> - Tasks assigned to John</li>
                            </ul>
                            
                            <h6>Logical Operators</h6>
                            <p>Combine filters with AND, OR, NOT:</p>
                            <ul>
                                <li><code>status:New AND priority:High</code> - New high priority tasks</li>
                                <li><code>category:Technical OR category:Billing</code> - Technical or billing issues</li>
                                <li><code>NOT status:Completed</code> - All non-completed tasks</li>
                            </ul>
                            
                            <h6>Text Search</h6>
                            <p>Search in task content:</p>
                            <ul>
                                <li><code>heating problem</code> - Tasks containing "heating" and "problem"</li>
                                <li><code>"exact phrase"</code> - Tasks containing exact phrase</li>
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(helpModal);
            new bootstrap.Modal(helpModal).show();
            
            helpModal.addEventListener('hidden.bs.modal', () => {
                helpModal.remove();
            });
        },

        showRecentSearches() {
            // Implementation for showing recent searches dropdown
            console.log('Show recent searches');
        },

        showSavedSearches() {
            // Implementation for showing saved searches dropdown
            console.log('Show saved searches');
        },

        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => AdvancedSearchManager.init());
    } else {
        AdvancedSearchManager.init();
    }

    // Expose globally
    window.AdvancedSearchManager = AdvancedSearchManager;

})();


