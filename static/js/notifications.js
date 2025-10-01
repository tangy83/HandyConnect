/**
 * Notification Manager
 * Handles toast notifications and browser push notifications
 */
(function() {
    'use strict';

    const NotificationManager = {
        container: null,
        notificationQueue: [],
        isProcessingQueue: false,
        quietHours: { start: 22, end: 8 }, // 10 PM to 8 AM
        maxNotifications: 5,
        deduplicationWindow: 10000, // 10 seconds

        init() {
            this.createContainer();
            this.setupPushNotifications();
            this.loadSettings();
        },

        createContainer() {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
                pointer-events: none;
            `;
            document.body.appendChild(this.container);
        },

        show(title, message, type = 'info', action = null, options = {}) {
            const notification = {
                id: this.generateId(),
                title,
                message,
                type,
                action,
                timestamp: Date.now(),
                options
            };

            // Check for duplicates
            if (this.isDuplicate(notification)) {
                return;
            }

            // Check quiet hours
            if (this.isQuietHours() && !options.urgent) {
                this.addToQueue(notification);
                return;
            }

            this.renderNotification(notification);
        },

        isDuplicate(notification) {
            const now = Date.now();
            return this.notificationQueue.some(n => 
                n.title === notification.title && 
                n.message === notification.message &&
                (now - n.timestamp) < this.deduplicationWindow
            );
        },

        isQuietHours() {
            const now = new Date();
            const hour = now.getHours();
            const { start, end } = this.quietHours;
            
            if (start > end) {
                return hour >= start || hour < end;
            }
            return hour >= start && hour < end;
        },

        addToQueue(notification) {
            this.notificationQueue.push(notification);
            if (!this.isProcessingQueue) {
                this.processQueue();
            }
        },

        processQueue() {
            if (this.notificationQueue.length === 0) return;

            this.isProcessingQueue = true;
            const notification = this.notificationQueue.shift();
            this.renderNotification(notification);

            // Process next notification after delay
            setTimeout(() => {
                this.isProcessingQueue = false;
                this.processQueue();
            }, 3000);
        },

        renderNotification(notification) {
            const element = document.createElement('div');
            element.className = `alert alert-${this.getAlertClass(notification.type)} alert-dismissible fade show notification-item`;
            element.style.cssText = `
                margin-bottom: 10px;
                pointer-events: auto;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                animation: slideInRight 0.3s ease-out;
            `;

            element.innerHTML = `
                <div class="d-flex align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="alert-heading mb-1">
                            <i class="bi ${this.getIcon(notification.type)} me-2"></i>
                            ${this.escapeHtml(notification.title)}
                        </h6>
                        <p class="mb-2">${this.escapeHtml(notification.message)}</p>
                        ${notification.action ? `
                            <button class="btn btn-sm btn-outline-primary" onclick="window.NotificationManager.handleAction('${notification.id}')">
                                View Details
                            </button>
                        ` : ''}
                    </div>
                    <button type="button" class="btn-close" onclick="window.NotificationManager.dismiss('${notification.id}')"></button>
                </div>
            `;

            // Store action for later execution
            if (notification.action) {
                element.dataset.action = JSON.stringify(notification.action);
            }

            this.container.appendChild(element);

            // Auto-dismiss after delay
            setTimeout(() => {
                this.dismiss(notification.id);
            }, notification.options.duration || 5000);

            // Limit number of notifications
            this.limitNotifications();
        },

        getAlertClass(type) {
            const typeMap = {
                success: 'success',
                error: 'danger',
                warning: 'warning',
                info: 'info',
                urgent: 'danger'
            };
            return typeMap[type] || 'info';
        },

        getIcon(type) {
            const iconMap = {
                success: 'bi-check-circle',
                error: 'bi-exclamation-triangle',
                warning: 'bi-exclamation-circle',
                info: 'bi-info-circle',
                urgent: 'bi-lightning'
            };
            return iconMap[type] || 'bi-info-circle';
        },

        dismiss(id) {
            const element = document.querySelector(`[data-notification-id="${id}"]`);
            if (element) {
                element.classList.remove('show');
                setTimeout(() => {
                    if (element.parentNode) {
                        element.parentNode.removeChild(element);
                    }
                }, 150);
            }
        },

        handleAction(id) {
            const element = document.querySelector(`[data-notification-id="${id}"]`);
            if (element && element.dataset.action) {
                const action = JSON.parse(element.dataset.action);
                if (typeof action === 'function') {
                    action();
                }
            }
            this.dismiss(id);
        },

        limitNotifications() {
            const notifications = this.container.querySelectorAll('.notification-item');
            if (notifications.length > this.maxNotifications) {
                const oldest = notifications[0];
                this.dismiss(oldest.dataset.notificationId);
            }
        },

        setupPushNotifications() {
            if (!('Notification' in window) || !('serviceWorker' in navigator)) {
                return;
            }

            // Request permission
            if (Notification.permission === 'default') {
                Notification.requestPermission().then(permission => {
                    if (permission === 'granted') {
                        this.registerServiceWorker();
                    }
                });
            } else if (Notification.permission === 'granted') {
                this.registerServiceWorker();
            }
        },

        registerServiceWorker() {
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/js/sw.js')
                    .then(registration => {
                        console.log('Service Worker registered:', registration);
                    })
                    .catch(error => {
                        console.log('Service Worker registration failed:', error);
                    });
            }
        },

        sendPushNotification(title, message, data = {}) {
            if (Notification.permission === 'granted') {
                const notification = new Notification(title, {
                    body: message,
                    icon: '/static/images/icon-192x192.png',
                    badge: '/static/images/badge-72x72.png',
                    data: data,
                    requireInteraction: true
                });

                notification.onclick = () => {
                    window.focus();
                    if (data.url) {
                        window.location.href = data.url;
                    }
                    notification.close();
                };
            }
        },

        loadSettings() {
            const settings = localStorage.getItem('notificationSettings');
            if (settings) {
                const parsed = JSON.parse(settings);
                this.quietHours = parsed.quietHours || this.quietHours;
                this.maxNotifications = parsed.maxNotifications || this.maxNotifications;
            }
        },

        saveSettings() {
            const settings = {
                quietHours: this.quietHours,
                maxNotifications: this.maxNotifications
            };
            localStorage.setItem('notificationSettings', JSON.stringify(settings));
        },

        generateId() {
            return 'notification_' + Math.random().toString(36).substr(2, 9);
        },

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        // Public API methods
        showSuccess(title, message, action = null) {
            this.show(title, message, 'success', action);
        },

        showError(title, message, action = null) {
            this.show(title, message, 'error', action);
        },

        showWarning(title, message, action = null) {
            this.show(title, message, 'warning', action);
        },

        showInfo(title, message, action = null) {
            this.show(title, message, 'info', action);
        },

        showUrgent(title, message, action = null) {
            this.show(title, message, 'urgent', action, { urgent: true });
        },

        clearAll() {
            const notifications = this.container.querySelectorAll('.notification-item');
            notifications.forEach(notification => {
                this.dismiss(notification.dataset.notificationId);
            });
        },

        // Enhanced features for Feature 11
        showSLAWarning(taskId, taskSubject, timeRemaining) {
            const message = `SLA breach approaching for "${taskSubject}" in ${timeRemaining}`;
            this.showUrgent('SLA Warning', message, () => {
                if (window.TaskManager) {
                    window.TaskManager.viewTask(taskId);
                }
            });
        },

        showAssignmentNotification(taskId, taskSubject, assigner) {
            const message = `Assigned to you by ${assigner}: "${taskSubject}"`;
            this.showSuccess('New Assignment', message, () => {
                if (window.TaskManager) {
                    window.TaskManager.viewTask(taskId);
                }
            });
        },

        showStatusChangeNotification(taskId, taskSubject, oldStatus, newStatus) {
            const message = `"${taskSubject}" changed from ${oldStatus} to ${newStatus}`;
            this.showInfo('Status Updated', message, () => {
                if (window.TaskManager) {
                    window.TaskManager.viewTask(taskId);
                }
            });
        },

        // Notification categories and muting
        muteCategory(category) {
            const mutedCategories = this.getMutedCategories();
            mutedCategories.add(category);
            localStorage.setItem('mutedNotificationCategories', JSON.stringify([...mutedCategories]));
        },

        unmuteCategory(category) {
            const mutedCategories = this.getMutedCategories();
            mutedCategories.delete(category);
            localStorage.setItem('mutedNotificationCategories', JSON.stringify([...mutedCategories]));
        },

        getMutedCategories() {
            const stored = localStorage.getItem('mutedNotificationCategories');
            return new Set(stored ? JSON.parse(stored) : []);
        },

        isCategoryMuted(category) {
            return this.getMutedCategories().has(category);
        },

        // Unread notifications counter
        updateUnreadCounter() {
            const counter = document.getElementById('unread-notifications-counter');
            if (counter) {
                const unreadCount = this.getUnreadCount();
                counter.textContent = unreadCount;
                counter.style.display = unreadCount > 0 ? 'inline' : 'none';
            }
        },

        getUnreadCount() {
            return parseInt(localStorage.getItem('unreadNotificationsCount') || '0');
        },

        incrementUnreadCount() {
            const current = this.getUnreadCount();
            localStorage.setItem('unreadNotificationsCount', (current + 1).toString());
            this.updateUnreadCounter();
        },

        clearUnreadCount() {
            localStorage.setItem('unreadNotificationsCount', '0');
            this.updateUnreadCounter();
        }
    };

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .notification-item {
            transition: all 0.3s ease-in-out;
        }
        
        .notification-item.fade-out {
            transform: translateX(100%);
            opacity: 0;
        }
    `;
    document.head.appendChild(style);

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => NotificationManager.init());
    } else {
        NotificationManager.init();
    }

    // Expose globally
    window.NotificationManager = NotificationManager;

})();
