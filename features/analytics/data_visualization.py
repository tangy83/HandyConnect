"""
Data Analytics Foundation - Data Visualization Library Integration
Author: Sunayana
Phase 9: Data Analytics Foundation

This module provides data visualization capabilities using Chart.js
and other visualization libraries for the HandyConnect analytics dashboard.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import statistics
from collections import defaultdict

from .data_schema import TaskAnalytics, ThreadAnalytics, PerformanceMetric, SystemHealth
from .data_persistence import AnalyticsDataPersistence
from .analytics_framework import DataAggregator

logger = logging.getLogger(__name__)

@dataclass
class ChartConfig:
    """Chart configuration"""
    type: str  # 'line', 'bar', 'pie', 'doughnut', 'radar', 'scatter'
    title: str
    x_axis_label: str = ""
    y_axis_label: str = ""
    colors: List[str] = None
    responsive: bool = True
    maintain_aspect_ratio: bool = False
    height: int = 400

class DataVisualization:
    """Data visualization generator"""
    
    def __init__(self, persistence: AnalyticsDataPersistence):
        self.persistence = persistence
        self.aggregator = DataAggregator(persistence)
        
        # Default color palettes
        self.color_palettes = {
            'primary': ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#20c997', '#fd7e14', '#6c757d'],
            'pastel': ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0', '#ffb3e6', '#c4e17f'],
            'monochrome': ['#2c3e50', '#34495e', '#7f8c8d', '#95a5a6', '#bdc3c7', '#ecf0f1', '#d5dbdb', '#f8f9fa']
        }
        
        logger.info("Data visualization initialized")
    
    def generate_task_status_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate task status distribution chart"""
        try:
            task_metrics = self.aggregator.aggregate_task_metrics(start_date, end_date)
            status_distribution = task_metrics.get('status_distribution', {})
            
            if not status_distribution:
                return self._empty_chart("Task Status Distribution")
            
            # Prepare data for doughnut chart
            labels = list(status_distribution.keys())
            data = list(status_distribution.values())
            
            # Define colors for each status
            status_colors = {
                'New': '#ffc107',
                'In Progress': '#17a2b8',
                'Completed': '#28a745',
                'On Hold': '#dc3545'
            }
            
            colors = [status_colors.get(status, '#6c757d') for status in labels]
            
            chart_config = {
                'type': 'doughnut',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': data,
                        'backgroundColor': colors,
                        'borderWidth': 2,
                        'borderColor': '#ffffff'
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Task Status Distribution',
                            'font': {'size': 16, 'weight': 'bold'}
                        },
                        'legend': {
                            'position': 'bottom',
                            'labels': {
                                'padding': 20,
                                'usePointStyle': True
                            }
                        }
                    }
                }
            }
            
            return chart_config
            
        except Exception as e:
            logger.error(f"Error generating task status chart: {e}")
            return self._error_chart("Task Status Distribution", str(e))
    
    def generate_priority_distribution_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate task priority distribution chart"""
        try:
            task_metrics = self.aggregator.aggregate_task_metrics(start_date, end_date)
            priority_distribution = task_metrics.get('priority_distribution', {})
            
            if not priority_distribution:
                return self._empty_chart("Task Priority Distribution")
            
            # Prepare data for bar chart
            labels = list(priority_distribution.keys())
            data = list(priority_distribution.values())
            
            # Define colors for each priority
            priority_colors = {
                'Low': '#28a745',
                'Medium': '#ffc107',
                'High': '#fd7e14',
                'Urgent': '#dc3545'
            }
            
            colors = [priority_colors.get(priority, '#6c757d') for priority in labels]
            
            chart_config = {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Number of Tasks',
                        'data': data,
                        'backgroundColor': colors,
                        'borderColor': colors,
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Task Priority Distribution',
                            'font': {'size': 16, 'weight': 'bold'}
                        },
                        'legend': {
                            'display': False
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'title': {
                                'display': True,
                                'text': 'Number of Tasks'
                            }
                        },
                        'x': {
                            'title': {
                                'display': True,
                                'text': 'Priority Level'
                            }
                        }
                    }
                }
            }
            
            return chart_config
            
        except Exception as e:
            logger.error(f"Error generating priority distribution chart: {e}")
            return self._error_chart("Task Priority Distribution", str(e))
    
    def generate_response_time_trend_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate response time trend chart"""
        try:
            # Get daily metrics for the period
            daily_metrics = self._get_daily_metrics(start_date, end_date)
            
            if not daily_metrics:
                return self._empty_chart("Response Time Trend")
            
            # Prepare data for line chart
            dates = list(daily_metrics.keys())
            response_times = [daily_metrics[date].get('avg_response_time_minutes', 0) for date in dates]
            resolution_times = [daily_metrics[date].get('avg_resolution_time_minutes', 0) for date in dates]
            
            chart_config = {
                'type': 'line',
                'data': {
                    'labels': [datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d') for date in dates],
                    'datasets': [
                        {
                            'label': 'Response Time (minutes)',
                            'data': response_times,
                            'borderColor': '#007bff',
                            'backgroundColor': 'rgba(0, 123, 255, 0.1)',
                            'tension': 0.4,
                            'fill': True
                        },
                        {
                            'label': 'Resolution Time (minutes)',
                            'data': resolution_times,
                            'borderColor': '#28a745',
                            'backgroundColor': 'rgba(40, 167, 69, 0.1)',
                            'tension': 0.4,
                            'fill': True
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Response Time Trend',
                            'font': {'size': 16, 'weight': 'bold'}
                        },
                        'legend': {
                            'position': 'top',
                            'labels': {
                                'usePointStyle': True
                            }
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'title': {
                                'display': True,
                                'text': 'Time (minutes)'
                            }
                        },
                        'x': {
                            'title': {
                                'display': True,
                                'text': 'Date'
                            }
                        }
                    },
                    'interaction': {
                        'intersect': False,
                        'mode': 'index'
                    }
                }
            }
            
            return chart_config
            
        except Exception as e:
            logger.error(f"Error generating response time trend chart: {e}")
            return self._error_chart("Response Time Trend", str(e))
    
    def generate_performance_metrics_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate performance metrics chart"""
        try:
            performance_metrics = self.aggregator.aggregate_performance_metrics(start_date, end_date)
            metrics_data = performance_metrics.get('metrics', {})
            
            if not metrics_data:
                return self._empty_chart("Performance Metrics")
            
            # Prepare data for radar chart
            metric_types = list(metrics_data.keys())
            avg_values = [metrics_data[metric_type].get('avg', 0) for metric_type in metric_types]
            
            # Normalize values for radar chart (0-100 scale)
            max_value = max(avg_values) if avg_values else 1
            normalized_values = [(value / max_value) * 100 for value in avg_values]
            
            chart_config = {
                'type': 'radar',
                'data': {
                    'labels': [self._format_metric_label(label) for label in metric_types],
                    'datasets': [{
                        'label': 'Performance Score',
                        'data': normalized_values,
                        'borderColor': '#007bff',
                        'backgroundColor': 'rgba(0, 123, 255, 0.2)',
                        'pointBackgroundColor': '#007bff',
                        'pointBorderColor': '#ffffff',
                        'pointHoverBackgroundColor': '#ffffff',
                        'pointHoverBorderColor': '#007bff'
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Performance Metrics Overview',
                            'font': {'size': 16, 'weight': 'bold'}
                        },
                        'legend': {
                            'display': False
                        }
                    },
                    'scales': {
                        'r': {
                            'beginAtZero': True,
                            'max': 100,
                            'ticks': {
                                'stepSize': 20
                            }
                        }
                    }
                }
            }
            
            return chart_config
            
        except Exception as e:
            logger.error(f"Error generating performance metrics chart: {e}")
            return self._error_chart("Performance Metrics", str(e))
    
    def generate_system_health_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate system health chart"""
        try:
            system_health = self.aggregator.aggregate_system_health(start_date, end_date)
            services_data = system_health.get('services', {})
            
            if not services_data:
                return self._empty_chart("System Health")
            
            # Prepare data for bar chart
            services = list(services_data.keys())
            uptime_values = [services_data[service].get('uptime_percent', 0) for service in services]
            cpu_values = [services_data[service].get('avg_cpu_usage', 0) for service in services]
            memory_values = [services_data[service].get('avg_memory_usage', 0) for service in services]
            
            chart_config = {
                'type': 'bar',
                'data': {
                    'labels': services,
                    'datasets': [
                        {
                            'label': 'Uptime %',
                            'data': uptime_values,
                            'backgroundColor': '#28a745',
                            'borderColor': '#28a745',
                            'borderWidth': 1
                        },
                        {
                            'label': 'CPU Usage %',
                            'data': cpu_values,
                            'backgroundColor': '#ffc107',
                            'borderColor': '#ffc107',
                            'borderWidth': 1
                        },
                        {
                            'label': 'Memory Usage %',
                            'data': memory_values,
                            'backgroundColor': '#dc3545',
                            'borderColor': '#dc3545',
                            'borderWidth': 1
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'System Health Overview',
                            'font': {'size': 16, 'weight': 'bold'}
                        },
                        'legend': {
                            'position': 'top',
                            'labels': {
                                'usePointStyle': True
                            }
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'max': 100,
                            'title': {
                                'display': True,
                                'text': 'Percentage (%)'
                            }
                        },
                        'x': {
                            'title': {
                                'display': True,
                                'text': 'Services'
                            }
                        }
                    }
                }
            }
            
            return chart_config
            
        except Exception as e:
            logger.error(f"Error generating system health chart: {e}")
            return self._error_chart("System Health", str(e))
    
    def generate_category_breakdown_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate task category breakdown chart"""
        try:
            task_metrics = self.aggregator.aggregate_task_metrics(start_date, end_date)
            category_distribution = task_metrics.get('category_distribution', {})
            
            if not category_distribution:
                return self._empty_chart("Task Category Breakdown")
            
            # Sort by count (descending) and take top 10
            sorted_categories = sorted(category_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
            
            labels = [item[0] for item in sorted_categories]
            data = [item[1] for item in sorted_categories]
            
            chart_config = {
                'type': 'horizontalBar',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Number of Tasks',
                        'data': data,
                        'backgroundColor': self.color_palettes['primary'][:len(labels)],
                        'borderColor': self.color_palettes['primary'][:len(labels)],
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'indexAxis': 'y',
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Task Category Breakdown (Top 10)',
                            'font': {'size': 16, 'weight': 'bold'}
                        },
                        'legend': {
                            'display': False
                        }
                    },
                    'scales': {
                        'x': {
                            'beginAtZero': True,
                            'title': {
                                'display': True,
                                'text': 'Number of Tasks'
                            }
                        },
                        'y': {
                            'title': {
                                'display': True,
                                'text': 'Categories'
                            }
                        }
                    }
                }
            }
            
            return chart_config
            
        except Exception as e:
            logger.error(f"Error generating category breakdown chart: {e}")
            return self._error_chart("Task Category Breakdown", str(e))
    
    def generate_escalation_trend_chart(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate escalation trend chart"""
        try:
            # Get daily metrics for the period
            daily_metrics = self._get_daily_metrics(start_date, end_date)
            
            if not daily_metrics:
                return self._empty_chart("Escalation Trend")
            
            # Prepare data for line chart
            dates = list(daily_metrics.keys())
            escalation_rates = [daily_metrics[date].get('escalation_rate_percent', 0) for date in dates]
            
            chart_config = {
                'type': 'line',
                'data': {
                    'labels': [datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d') for date in dates],
                    'datasets': [{
                        'label': 'Escalation Rate (%)',
                        'data': escalation_rates,
                        'borderColor': '#dc3545',
                        'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                        'tension': 0.4,
                        'fill': True,
                        'pointBackgroundColor': '#dc3545',
                        'pointBorderColor': '#ffffff',
                        'pointBorderWidth': 2
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Escalation Rate Trend',
                            'font': {'size': 16, 'weight': 'bold'}
                        },
                        'legend': {
                            'display': False
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'max': 100,
                            'title': {
                                'display': True,
                                'text': 'Escalation Rate (%)'
                            }
                        },
                        'x': {
                            'title': {
                                'display': True,
                                'text': 'Date'
                            }
                        }
                    },
                    'elements': {
                        'point': {
                            'radius': 5,
                            'hoverRadius': 8
                        }
                    }
                }
            }
            
            return chart_config
            
        except Exception as e:
            logger.error(f"Error generating escalation trend chart: {e}")
            return self._error_chart("Escalation Trend", str(e))
    
    def _get_daily_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Dict[str, Any]]:
        """Get daily aggregated metrics"""
        try:
            daily_metrics = {}
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                date_str = current_date.strftime('%Y-%m-%d')
                day_start = datetime.combine(current_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                day_end = datetime.combine(current_date, datetime.max.time()).replace(tzinfo=timezone.utc)
                
                # Get metrics for this day
                task_metrics = self.aggregator.aggregate_task_metrics(day_start, day_end)
                daily_metrics[date_str] = task_metrics
                
                current_date += timedelta(days=1)
            
            return daily_metrics
            
        except Exception as e:
            logger.error(f"Error getting daily metrics: {e}")
            return {}
    
    def _format_metric_label(self, metric_type: str) -> str:
        """Format metric type for display"""
        return metric_type.replace('_', ' ').title()
    
    def _empty_chart(self, title: str) -> Dict[str, Any]:
        """Return empty chart configuration"""
        return {
            'type': 'doughnut',
            'data': {
                'labels': ['No Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6c757d'],
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'{title} - No Data Available',
                        'font': {'size': 16, 'weight': 'bold'}
                    },
                    'legend': {
                        'display': False
                    }
                }
            }
        }
    
    def _error_chart(self, title: str, error_message: str) -> Dict[str, Any]:
        """Return error chart configuration"""
        return {
            'type': 'doughnut',
            'data': {
                'labels': ['Error'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#dc3545'],
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'{title} - Error: {error_message}',
                        'font': {'size': 16, 'weight': 'bold'}
                    },
                    'legend': {
                        'display': False
                    }
                }
            }
        }
    
    def generate_dashboard_charts(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate all dashboard charts"""
        try:
            charts = {
                'task_status': self.generate_task_status_chart(start_date, end_date),
                'priority_distribution': self.generate_priority_distribution_chart(start_date, end_date),
                'response_time_trend': self.generate_response_time_trend_chart(start_date, end_date),
                'performance_metrics': self.generate_performance_metrics_chart(start_date, end_date),
                'system_health': self.generate_system_health_chart(start_date, end_date),
                'category_breakdown': self.generate_category_breakdown_chart(start_date, end_date),
                'escalation_trend': self.generate_escalation_trend_chart(start_date, end_date)
            }
            
            return {
                'charts': charts,
                'generated_at': get_current_timestamp(),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard charts: {e}")
            return {'error': str(e)}
