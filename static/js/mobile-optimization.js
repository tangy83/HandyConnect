/**
 * HandyConnect Phase 12: Mobile Optimization JavaScript
 * Enhanced mobile experience and touch interactions
 */

// Mobile detection and optimization
class MobileOptimizer {
    constructor() {
        this.isMobile = this.detectMobile();
        this.isTouch = this.detectTouch();
        this.viewport = this.getViewport();
        
        this.init();
    }
    
    init() {
        console.log('Mobile Optimizer initialized');
        console.log(`Mobile: ${this.isMobile}, Touch: ${this.isTouch}, Viewport: ${this.viewport}`);
        
        this.optimizeForDevice();
        this.setupTouchInteractions();
        this.optimizePerformance();
        this.setupResponsiveHandlers();
    }
    
    detectMobile() {
        // Multiple mobile detection methods
        const userAgent = navigator.userAgent.toLowerCase();
        const mobileKeywords = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone'];
        const isMobileUA = mobileKeywords.some(keyword => userAgent.includes(keyword));
        
        // Check screen size
        const isMobileScreen = window.innerWidth <= 768;
        
        // Check touch capability
        const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        
        return isMobileUA || (isMobileScreen && hasTouch);
    }
    
    detectTouch() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    }
    
    getViewport() {
        const width = window.innerWidth;
        if (width <= 576) return 'xs';
        if (width <= 768) return 'sm';
        if (width <= 992) return 'md';
        if (width <= 1200) return 'lg';
        return 'xl';
    }
    
    optimizeForDevice() {
        // Add device-specific classes
        document.body.classList.add(`device-${this.viewport}`);
        if (this.isMobile) document.body.classList.add('mobile-device');
        if (this.isTouch) document.body.classList.add('touch-device');
        
        // Optimize for mobile if needed
        if (this.isMobile) {
            this.optimizeMobileLayout();
            this.setupMobileNavigation();
            this.optimizeMobileTables();
            this.setupMobileModals();
        }
        
        // Setup touch interactions
        if (this.isTouch) {
            this.setupTouchGestures();
            this.optimizeTouchTargets();
        }
    }
    
    optimizeMobileLayout() {
        console.log('Optimizing mobile layout...');
        
        // Adjust container padding
        const containers = document.querySelectorAll('.container, .container-fluid');
        containers.forEach(container => {
            container.style.padding = '0.5rem';
        });
        
        // Optimize card layouts
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.marginBottom = '1rem';
            card.style.borderRadius = '0.5rem';
        });
        
        // Optimize button sizes
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            btn.style.minHeight = '44px';
            btn.style.fontSize = '0.875rem';
        });
        
        // Optimize form controls
        const formControls = document.querySelectorAll('.form-control, .form-select');
        formControls.forEach(control => {
            control.style.minHeight = '44px';
            control.style.fontSize = '16px'; // Prevents zoom on iOS
        });
    }
    
    setupMobileNavigation() {
        // Enhance mobile navigation
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            // Add mobile-specific navigation enhancements
            navbar.addEventListener('click', (e) => {
                if (e.target.classList.contains('navbar-toggler')) {
                    this.handleMobileNavToggle();
                }
            });
        }
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            const navbar = document.querySelector('.navbar-collapse');
            const toggler = document.querySelector('.navbar-toggler');
            
            if (navbar && navbar.classList.contains('show') && 
                !navbar.contains(e.target) && 
                !toggler.contains(e.target)) {
                this.closeMobileMenu();
            }
        });
    }
    
    handleMobileNavToggle() {
        const navbar = document.querySelector('.navbar-collapse');
        if (navbar) {
            navbar.classList.toggle('show');
        }
    }
    
    closeMobileMenu() {
        const navbar = document.querySelector('.navbar-collapse');
        const toggler = document.querySelector('.navbar-toggler');
        
        if (navbar) navbar.classList.remove('show');
        if (toggler) toggler.setAttribute('aria-expanded', 'false');
    }
    
    optimizeMobileTables() {
        // Make tables mobile-friendly
        const tables = document.querySelectorAll('.table-responsive');
        tables.forEach(table => {
            // Add horizontal scroll indicator
            this.addScrollIndicator(table);
            
            // Optimize table for mobile
            const tableElement = table.querySelector('table');
            if (tableElement) {
                this.optimizeTableForMobile(tableElement);
            }
        });
    }
    
    addScrollIndicator(table) {
        if (this.isMobile) {
            const indicator = document.createElement('div');
            indicator.className = 'scroll-indicator';
            indicator.innerHTML = '← Scroll to see more →';
            indicator.style.cssText = `
                text-align: center;
                font-size: 0.75rem;
                color: #6c757d;
                padding: 0.25rem;
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            `;
            table.insertBefore(indicator, table.firstChild);
        }
    }
    
    optimizeTableForMobile(table) {
        // Add mobile-specific table optimizations
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.style.cursor = 'pointer';
            
            // Add touch feedback
            row.addEventListener('touchstart', () => {
                row.style.backgroundColor = '#f8f9fa';
            });
            
            row.addEventListener('touchend', () => {
                setTimeout(() => {
                    row.style.backgroundColor = '';
                }, 150);
            });
        });
    }
    
    setupMobileModals() {
        // Optimize modals for mobile
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            // Make modals fullscreen on mobile
            if (this.isMobile) {
                modal.classList.add('modal-fullscreen-mobile');
            }
            
            // Add mobile-specific modal enhancements
            this.enhanceModalForMobile(modal);
        });
    }
    
    enhanceModalForMobile(modal) {
        // Add swipe-to-close gesture
        let startY = 0;
        let currentY = 0;
        let isDragging = false;
        
        modal.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
            isDragging = true;
        });
        
        modal.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            
            currentY = e.touches[0].clientY;
            const deltaY = currentY - startY;
            
            // If swiping down significantly, close modal
            if (deltaY > 100) {
                this.closeModal(modal);
                isDragging = false;
            }
        });
        
        modal.addEventListener('touchend', () => {
            isDragging = false;
        });
    }
    
    closeModal(modal) {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    }
    
    setupTouchInteractions() {
        // Enhanced touch interactions
        this.setupTouchFeedback();
        this.setupSwipeGestures();
        this.optimizeTouchTargets();
    }
    
    setupTouchFeedback() {
        // Add visual feedback for touch interactions
        const touchElements = document.querySelectorAll('.btn, .nav-link, .dropdown-item, .page-link');
        
        touchElements.forEach(element => {
            element.addEventListener('touchstart', () => {
                element.style.opacity = '0.7';
                element.style.transform = 'scale(0.95)';
            });
            
            element.addEventListener('touchend', () => {
                setTimeout(() => {
                    element.style.opacity = '';
                    element.style.transform = '';
                }, 150);
            });
        });
    }
    
    setupSwipeGestures() {
        // Add swipe gestures for navigation
        let startX = 0;
        let startY = 0;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            
            // Horizontal swipe detection
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                if (deltaX > 0) {
                    // Swipe right - could implement previous page navigation
                    this.handleSwipeRight();
                } else {
                    // Swipe left - could implement next page navigation
                    this.handleSwipeLeft();
                }
            }
        });
    }
    
    handleSwipeRight() {
        // Implement swipe right action (e.g., go back)
        console.log('Swipe right detected');
    }
    
    handleSwipeLeft() {
        // Implement swipe left action (e.g., go forward)
        console.log('Swipe left detected');
    }
    
    setupTouchGestures() {
        // Advanced touch gestures
        this.setupPinchZoom();
        this.setupDoubleTap();
    }
    
    setupPinchZoom() {
        // Disable pinch zoom on critical elements
        const criticalElements = document.querySelectorAll('.table, .modal, .card');
        criticalElements.forEach(element => {
            element.addEventListener('touchstart', (e) => {
                if (e.touches.length > 1) {
                    e.preventDefault();
                }
            });
        });
    }
    
    setupDoubleTap() {
        // Double tap to zoom functionality
        let lastTap = 0;
        
        document.addEventListener('touchend', (e) => {
            const currentTime = new Date().getTime();
            const tapLength = currentTime - lastTap;
            
            if (tapLength < 500 && tapLength > 0) {
                // Double tap detected
                this.handleDoubleTap(e);
            }
            
            lastTap = currentTime;
        });
    }
    
    handleDoubleTap(e) {
        // Implement double tap action
        console.log('Double tap detected');
    }
    
    optimizeTouchTargets() {
        // Ensure all interactive elements meet touch target guidelines (44px minimum)
        const interactiveElements = document.querySelectorAll('a, button, input, select, textarea, [role="button"]');
        
        interactiveElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            
            if (rect.width < 44 || rect.height < 44) {
                element.style.minWidth = '44px';
                element.style.minHeight = '44px';
                element.style.display = 'inline-flex';
                element.style.alignItems = 'center';
                element.style.justifyContent = 'center';
            }
        });
    }
    
    optimizePerformance() {
        // Performance optimizations for mobile
        this.lazyLoadImages();
        this.optimizeScrollPerformance();
        this.reduceAnimations();
    }
    
    lazyLoadImages() {
        // Implement lazy loading for images
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        }
    }
    
    optimizeScrollPerformance() {
        // Optimize scroll performance
        let ticking = false;
        
        const updateScrollPosition = () => {
            // Throttled scroll handling
            ticking = false;
        };
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateScrollPosition);
                ticking = true;
            }
        });
    }
    
    reduceAnimations() {
        // Reduce animations on mobile for better performance
        if (this.isMobile) {
            const style = document.createElement('style');
            style.textContent = `
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    setupResponsiveHandlers() {
        // Handle viewport changes
        window.addEventListener('resize', this.debounce(() => {
            this.handleViewportChange();
        }, 250));
        
        // Handle orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleOrientationChange();
            }, 100);
        });
    }
    
    handleViewportChange() {
        const newViewport = this.getViewport();
        
        if (newViewport !== this.viewport) {
            this.viewport = newViewport;
            
            // Remove old viewport class
            document.body.classList.remove(`device-${this.viewport}`);
            
            // Add new viewport class
            document.body.classList.add(`device-${newViewport}`);
            
            // Trigger responsive adjustments
            this.optimizeForDevice();
        }
    }
    
    handleOrientationChange() {
        console.log('Orientation changed');
        
        // Recalculate layout
        this.viewport = this.getViewport();
        this.optimizeForDevice();
        
        // Trigger custom orientation change event
        window.dispatchEvent(new CustomEvent('orientationChanged', {
            detail: { viewport: this.viewport }
        }));
    }
    
    // Utility methods
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
    }
    
    // Public API methods
    isMobileDevice() {
        return this.isMobile;
    }
    
    isTouchDevice() {
        return this.isTouch;
    }
    
    getCurrentViewport() {
        return this.viewport;
    }
    
    refresh() {
        this.viewport = this.getViewport();
        this.optimizeForDevice();
    }
}

// Mobile-specific utility functions
class MobileUtils {
    static showMobileNotification(message, type = 'info') {
        // Create mobile-optimized notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} mobile-notification`;
        notification.style.cssText = `
            position: fixed;
            top: 70px;
            left: 10px;
            right: 10px;
            z-index: 9999;
            font-size: 0.875rem;
            padding: 0.75rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    static showMobileLoading(message = 'Loading...') {
        // Create mobile-optimized loading indicator
        const loading = document.createElement('div');
        loading.className = 'mobile-loading';
        loading.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 1rem 2rem;
            border-radius: 0.5rem;
            z-index: 9999;
            text-align: center;
        `;
        loading.innerHTML = `
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            ${message}
        `;
        
        document.body.appendChild(loading);
        return loading;
    }
    
    static hideMobileLoading(loading) {
        if (loading && loading.parentNode) {
            loading.remove();
        }
    }
    
    static vibrate(pattern = [100]) {
        // Haptic feedback for mobile devices
        if ('vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    }
    
    static shareContent(data) {
        // Web Share API for mobile devices
        if (navigator.share) {
            return navigator.share(data);
        } else {
            // Fallback to clipboard
            return navigator.clipboard.writeText(data.text || data.url);
        }
    }
}

// Initialize mobile optimization when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.mobileOptimizer = new MobileOptimizer();
    window.mobileUtils = MobileUtils;
    
    console.log('Mobile optimization system initialized');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MobileOptimizer, MobileUtils };
}
