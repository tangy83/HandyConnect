"""
Lightweight UI Options Module

This module provides lightweight, efficient UI components and interfaces.
Features:
- Minimal UI components
- Progressive web app capabilities
- Offline functionality
- Mobile-optimized interfaces
- Performance-focused design
"""

from .ui_components import UIComponents
from .mobile_interface import MobileInterface
from .offline_manager import OfflineManager
from ...utilities.performance_optimizer import PerformanceOptimizer

__all__ = [
    'UIComponents',
    'MobileInterface',
    'OfflineManager',
    'PerformanceOptimizer'
]






