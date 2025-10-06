"""
Case Management Module for HandyConnect
Handles case-related API endpoints and functionality
"""

from .case_api import case_bp
from .case_analytics import case_analytics_bp

__all__ = ['case_bp', 'case_analytics_bp']
