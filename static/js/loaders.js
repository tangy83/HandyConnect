/**
 * Loading Indicators Manager
 * Handles skeletons, spinners, and loading states
 */
(function() {
    'use strict';

    const LoaderManager = {
        activeLoaders: new Set(),
        skeletonDelay: 150,
        progressBar: null,

        init() {
            this.createProgressBar();
            this.setupGlobalStyles();
        },

        createProgressBar() {
            this.progressBar = document.createElement('div');
            this.progressBar.id = 'global-progress-bar';
            this.progressBar.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 0%;
                height: 3px;
                background: linear-gradient(90deg, #007bff, #28a745);
                z-index: 9999;
                transition: width 0.3s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            `;
            document.body.appendChild(this.progressBar);
        },

        setupGlobalStyles() {
            const style = document.createElement('style');
            style.textContent = `
                .skeleton {
                    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                    background-size: 200% 100%;
                    animation: skeleton-loading 1.5s infinite;
                    border-radius: 4px;
                }
                
                @keyframes skeleton-loading {
                    0% { background-position: 200% 0; }
                    100% { background-position: -200% 0; }
                }
                
                .skeleton-text {
                    height: 1em;
                    margin-bottom: 0.5em;
                }
                
                .skeleton-text:last-child {
                    margin-bottom: 0;
                }
                
                .skeleton-avatar {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                }
                
                .skeleton-button {
                    height: 38px;
                    width: 100px;
                    border-radius: 0.375rem;
                }
                
                .skeleton-card {
                    padding: 1rem;
                    border: 1px solid #dee2e6;
                    border-radius: 0.375rem;
                    margin-bottom: 1rem;
                }
                
                .loading-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(255, 255, 255, 0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                }
                
                .loading-spinner {
                    width: 2rem;
                    height: 2rem;
                    border: 0.25rem solid #f3f3f3;
                    border-top: 0.25rem solid #007bff;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                .fade-in {
                    animation: fadeIn 0.3s ease-in;
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        },

        // Global progress bar
        showProgress(percentage = 0) {
            this.progressBar.style.width = `${percentage}%`;
            if (percentage >= 100) {
                setTimeout(() => {
                    this.progressBar.style.width = '0%';
                }, 300);
            }
        },

        hideProgress() {
            this.progressBar.style.width = '0%';
        },

        // Skeleton loaders
        showTableSkeleton(container, rowCount = 5) {
            const skeleton = this.createTableSkeleton(rowCount);
            this.showSkeleton(container, skeleton);
        },


        showCardSkeleton(container) {
            const skeleton = this.createCardSkeleton();
            this.showSkeleton(container, skeleton);
        },

        showChartSkeleton(container) {
            const skeleton = this.createChartSkeleton();
            this.showSkeleton(container, skeleton);
        },

        createTableSkeleton(rowCount) {
            const rows = Array(rowCount).fill().map(() => `
                <tr>
                    <td><div class="skeleton skeleton-text" style="width: 20px; height: 20px;"></div></td>
                    <td><div class="skeleton skeleton-text" style="width: 80%;"></div></td>
                    <td><div class="skeleton skeleton-text" style="width: 60%;"></div></td>
                    <td><div class="skeleton skeleton-text" style="width: 40%;"></div></td>
                    <td><div class="skeleton skeleton-text" style="width: 30%;"></div></td>
                    <td><div class="skeleton skeleton-text" style="width: 25%;"></div></td>
                    <td><div class="skeleton skeleton-text" style="width: 35%;"></div></td>
                    <td><div class="skeleton skeleton-text" style="width: 50px;"></div></td>
                </tr>
            `).join('');

            return `
                <tbody class="skeleton-container">
                    ${rows}
                </tbody>
            `;
        },

        createKanbanSkeleton(cardCount) {
            const cards = Array(cardCount).fill().map(() => `
                <div class="card mb-2 skeleton-card">
                    <div class="skeleton skeleton-text" style="width: 80%; height: 1.2em; margin-bottom: 0.5rem;"></div>
                    <div class="skeleton skeleton-text" style="width: 60%; height: 0.8em; margin-bottom: 0.5rem;"></div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="skeleton skeleton-avatar"></div>
                        <div class="skeleton skeleton-text" style="width: 50px; height: 0.8em;"></div>
                    </div>
                </div>
            `).join('');

            return `
                <div class="skeleton-container">
                    ${cards}
                </div>
            `;
        },

        createCardSkeleton() {
            return `
                <div class="skeleton-container">
                    <div class="skeleton-card">
                        <div class="skeleton skeleton-text" style="width: 70%; height: 1.5em; margin-bottom: 1rem;"></div>
                        <div class="skeleton skeleton-text" style="width: 100%; height: 1em; margin-bottom: 0.5rem;"></div>
                        <div class="skeleton skeleton-text" style="width: 90%; height: 1em; margin-bottom: 0.5rem;"></div>
                        <div class="skeleton skeleton-text" style="width: 60%; height: 1em; margin-bottom: 1rem;"></div>
                        <div class="d-flex justify-content-between">
                            <div class="skeleton skeleton-button"></div>
                            <div class="skeleton skeleton-button"></div>
                        </div>
                    </div>
                </div>
            `;
        },

        createChartSkeleton() {
            return `
                <div class="skeleton-container position-relative">
                    <div class="skeleton" style="width: 100%; height: 300px; border-radius: 0.375rem;"></div>
                    <div class="loading-overlay">
                        <div class="loading-spinner"></div>
                    </div>
                </div>
            `;
        },

        showSkeleton(container, skeleton) {
            if (typeof container === 'string') {
                container = document.querySelector(container);
            }

            if (!container) return;

            // Delay skeleton display to avoid flicker
            setTimeout(() => {
                container.innerHTML = skeleton;
                container.classList.add('fade-in');
                container.setAttribute('aria-busy', 'true');
            }, this.skeletonDelay);
        },

        hideSkeleton(container) {
            if (typeof container === 'string') {
                container = document.querySelector(container);
            }

            if (!container) return;

            const skeletonContainer = container.querySelector('.skeleton-container');
            if (skeletonContainer) {
                skeletonContainer.remove();
            }
            container.removeAttribute('aria-busy');
        },

        // Button loading states
        showButtonLoading(button, text = 'Loading...') {
            const originalText = button.innerHTML;
            const originalDisabled = button.disabled;

            button.dataset.originalText = originalText;
            button.dataset.originalDisabled = originalDisabled;
            button.disabled = true;
            button.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                ${text}
            `;

            this.activeLoaders.add(button);
        },

        hideButtonLoading(button) {
            if (!this.activeLoaders.has(button)) return;

            button.innerHTML = button.dataset.originalText || button.innerHTML;
            button.disabled = button.dataset.originalDisabled === 'true';
            delete button.dataset.originalText;
            delete button.dataset.originalDisabled;

            this.activeLoaders.delete(button);
        },

        // Inline loading for specific elements
        showInlineLoading(element, text = 'Loading...') {
            const loadingElement = document.createElement('div');
            loadingElement.className = 'd-flex align-items-center text-muted';
            loadingElement.innerHTML = `
                <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
                ${text}
            `;

            element.style.position = 'relative';
            element.appendChild(loadingElement);
            element.setAttribute('aria-busy', 'true');
        },

        hideInlineLoading(element) {
            const loadingElement = element.querySelector('.spinner-border').parentElement;
            if (loadingElement) {
                loadingElement.remove();
            }
            element.removeAttribute('aria-busy');
        },

        // Overlay loading for modals/forms
        showOverlayLoading(container, text = 'Loading...') {
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="text-center">
                    <div class="loading-spinner mb-2"></div>
                    <div class="text-muted">${text}</div>
                </div>
            `;

            container.style.position = 'relative';
            container.appendChild(overlay);
            container.setAttribute('aria-busy', 'true');
        },

        hideOverlayLoading(container) {
            const overlay = container.querySelector('.loading-overlay');
            if (overlay) {
                overlay.remove();
            }
            container.removeAttribute('aria-busy');
        },

        // Loading states for API calls
        async withLoading(container, asyncFunction, options = {}) {
            const {
                skeleton = true,
                skeletonType = 'table',
                skeletonCount = 5,
                showProgress = false,
                delay = this.skeletonDelay
            } = options;

            try {
                // Show loading state
                if (skeleton) {
                    switch (skeletonType) {
                        case 'table':
                            this.showTableSkeleton(container, skeletonCount);
                            break;
                        case 'card':
                            this.showCardSkeleton(container);
                            break;
                        case 'chart':
                            this.showChartSkeleton(container);
                            break;
                    }
                }

                if (showProgress) {
                    this.showProgress(10);
                }

                // Execute async function
                const result = await asyncFunction();

                // Hide loading state
                if (skeleton) {
                    this.hideSkeleton(container);
                }

                if (showProgress) {
                    this.showProgress(100);
                }

                return result;

            } catch (error) {
                // Hide loading state on error
                if (skeleton) {
                    this.hideSkeleton(container);
                }

                if (showProgress) {
                    this.hideProgress();
                }

                throw error;
            }
        },

        // Utility methods
        isElementLoading(element) {
            return element.hasAttribute('aria-busy') && element.getAttribute('aria-busy') === 'true';
        },

        clearAllLoaders() {
            // Clear all button loaders
            this.activeLoaders.forEach(button => {
                this.hideButtonLoading(button);
            });

            // Clear all skeleton loaders
            document.querySelectorAll('.skeleton-container').forEach(container => {
                container.remove();
            });

            // Clear all overlay loaders
            document.querySelectorAll('.loading-overlay').forEach(overlay => {
                overlay.remove();
            });

            // Hide progress bar
            this.hideProgress();
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => LoaderManager.init());
    } else {
        LoaderManager.init();
    }

    // Expose globally
    window.LoaderManager = LoaderManager;

})();



