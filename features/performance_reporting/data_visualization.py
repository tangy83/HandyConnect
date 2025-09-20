"""
Data Visualization Library Integration
Interactive charts and graphs for analytics dashboard.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from dataclasses import dataclass
from enum import Enum

from ..task_structure_metadata.task_schema import TaskSchema, TaskStatus, TaskPriority, TaskCategory


class ChartType(Enum):
    """Types of charts available"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"


@dataclass
class ChartData:
    """Chart data structure"""
    chart_type: ChartType
    title: str
    data: Dict[str, Any]
    options: Dict[str, Any] = None
    metadata: Dict[str, Any] = None


class DataVisualizer:
    """Creates interactive charts and visualizations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_task_status_chart(self, tasks: List[TaskSchema]) -> ChartData:
        """Create a pie chart for task status distribution"""
        status_counts = {}
        for task in tasks:
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Define colors for each status
        status_colors = {
            'New': '#3498db',
            'In Progress': '#f39c12',
            'Pending': '#e74c3c',
            'Completed': '#27ae60',
            'Cancelled': '#95a5a6',
            'On Hold': '#9b59b6'
        }
        
        labels = list(status_counts.keys())
        data = list(status_counts.values())
        background_colors = [status_colors.get(status, '#95a5a6') for status in labels]
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': background_colors,
                'borderWidth': 2,
                'borderColor': '#ffffff'
            }]
        }
        
        options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'position': 'bottom',
                    'labels': {
                        'padding': 20,
                        'usePointStyle': True
                    }
                },
                'tooltip': {
                    'callbacks': {
                        'label': 'function(context) { return context.label + ": " + context.parsed + " tasks"; }'
                    }
                }
            }
        }
        
        return ChartData(
            chart_type=ChartType.PIE,
            title="Task Status Distribution",
            data=chart_data,
            options=options,
            metadata={'total_tasks': len(tasks)}
        )
    
    def create_priority_chart(self, tasks: List[TaskSchema]) -> ChartData:
        """Create a horizontal bar chart for priority distribution"""
        priority_counts = {}
        for task in tasks:
            priority = task.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Define colors for each priority
        priority_colors = {
            'Low': '#27ae60',
            'Medium': '#f39c12',
            'High': '#e67e22',
            'Urgent': '#e74c3c',
            'Critical': '#8e44ad'
        }
        
        # Sort by priority order
        priority_order = ['Low', 'Medium', 'High', 'Urgent', 'Critical']
        sorted_priorities = [p for p in priority_order if p in priority_counts]
        
        labels = sorted_priorities
        data = [priority_counts[p] for p in sorted_priorities]
        background_colors = [priority_colors.get(p, '#95a5a6') for p in sorted_priorities]
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': 'Number of Tasks',
                'data': data,
                'backgroundColor': background_colors,
                'borderWidth': 1,
                'borderColor': '#ffffff'
            }]
        }
        
        options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'indexAxis': 'y',
            'plugins': {
                'legend': {
                    'display': False
                },
                'tooltip': {
                    'callbacks': {
                        'label': 'function(context) { return context.parsed.x + " tasks"; }'
                    }
                }
            },
            'scales': {
                'x': {
                    'beginAtZero': True,
                    'ticks': {
                        'stepSize': 1
                    }
                }
            }
        }
        
        return ChartData(
            chart_type=ChartType.BAR,
            title="Task Priority Distribution",
            data=chart_data,
            options=options
        )
    
    def create_category_chart(self, tasks: List[TaskSchema]) -> ChartData:
        """Create a doughnut chart for category distribution"""
        category_counts = {}
        for task in tasks:
            category = task.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Define colors for categories
        category_colors = [
            '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
            '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#f1c40f'
        ]
        
        labels = list(category_counts.keys())
        data = list(category_counts.values())
        background_colors = category_colors[:len(labels)]
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': background_colors,
                'borderWidth': 2,
                'borderColor': '#ffffff'
            }]
        }
        
        options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'cutout': '50%',
            'plugins': {
                'legend': {
                    'position': 'right',
                    'labels': {
                        'padding': 15,
                        'usePointStyle': True
                    }
                },
                'tooltip': {
                    'callbacks': {
                        'label': 'function(context) { return context.label + ": " + context.parsed + " tasks"; }'
                    }
                }
            }
        }
        
        return ChartData(
            chart_type=ChartType.DOUGHNUT,
            title="Task Category Distribution",
            data=chart_data,
            options=options
        )
    
    def create_resolution_time_chart(self, tasks: List[TaskSchema]) -> ChartData:
        """Create a line chart for resolution time trends"""
        completed_tasks = [task for task in tasks if task.status == TaskStatus.COMPLETED and task.resolved_at]
        
        if not completed_tasks:
            return self._create_empty_chart("Resolution Time Trends", "No completed tasks available")
        
        # Group by day
        daily_data = {}
        for task in completed_tasks:
            if task.metadata.created_at and task.resolved_at:
                day = task.metadata.created_at.date()
                resolution_hours = (task.resolved_at - task.metadata.created_at).total_seconds() / 3600
                
                if day not in daily_data:
                    daily_data[day] = []
                daily_data[day].append(resolution_hours)
        
        # Calculate average resolution time per day
        sorted_days = sorted(daily_data.keys())
        labels = [day.strftime('%Y-%m-%d') for day in sorted_days]
        avg_resolution_times = [sum(times) / len(times) for times in [daily_data[day] for day in sorted_days]]
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': 'Average Resolution Time (hours)',
                'data': avg_resolution_times,
                'borderColor': '#3498db',
                'backgroundColor': 'rgba(52, 152, 219, 0.1)',
                'borderWidth': 2,
                'fill': True,
                'tension': 0.4
            }]
        }
        
        options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top'
                },
                'tooltip': {
                    'callbacks': {
                        'label': 'function(context) { return "Avg Resolution: " + context.parsed.y.toFixed(2) + " hours"; }'
                    }
                }
            },
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'title': {
                        'display': True,
                        'text': 'Hours'
                    }
                },
                'x': {
                    'title': {
                        'display': True,
                        'text': 'Date'
                    }
                }
            }
        }
        
        return ChartData(
            chart_type=ChartType.LINE,
            title="Resolution Time Trends",
            data=chart_data,
            options=options
        )
    
    def create_sla_compliance_gauge(self, tasks: List[TaskSchema]) -> ChartData:
        """Create a gauge chart for SLA compliance"""
        sla_tasks = [task for task in tasks if task.sla_deadline]
        
        if not sla_tasks:
            return self._create_empty_chart("SLA Compliance", "No SLA tasks available")
        
        sla_compliant = 0
        for task in sla_tasks:
            if task.status == TaskStatus.COMPLETED and task.resolved_at:
                if task.resolved_at <= task.sla_deadline:
                    sla_compliant += 1
            elif task.status != TaskStatus.COMPLETED:
                if datetime.utcnow() <= task.sla_deadline:
                    sla_compliant += 1
        
        compliance_rate = (sla_compliant / len(sla_tasks)) * 100
        
        chart_data = {
            'labels': ['SLA Compliance'],
            'datasets': [{
                'data': [compliance_rate],
                'backgroundColor': ['#27ae60' if compliance_rate >= 95 else '#f39c12' if compliance_rate >= 80 else '#e74c3c'],
                'borderWidth': 0
            }]
        }
        
        options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'cutout': '75%',
            'plugins': {
                'legend': {
                    'display': False
                },
                'tooltip': {
                    'callbacks': {
                        'label': f'function(context) {{ return "SLA Compliance: " + {compliance_rate:.1f} + "%"; }}'
                    }
                }
            }
        }
        
        return ChartData(
            chart_type=ChartType.GAUGE,
            title="SLA Compliance Rate",
            data=chart_data,
            options=options,
            metadata={'compliance_rate': compliance_rate, 'total_sla_tasks': len(sla_tasks)}
        )
    
    def create_trend_chart(self, tasks: List[TaskSchema], days: int = 7) -> ChartData:
        """Create a line chart for task creation and completion trends"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Initialize daily data
        daily_data = {}
        current_date = start_date
        while current_date <= end_date:
            daily_data[current_date] = {'created': 0, 'completed': 0}
            current_date += timedelta(days=1)
        
        # Count created tasks
        for task in tasks:
            if task.metadata.created_at:
                task_date = task.metadata.created_at.date()
                if start_date <= task_date <= end_date:
                    daily_data[task_date]['created'] += 1
        
        # Count completed tasks
        for task in tasks:
            if task.resolved_at:
                task_date = task.resolved_at.date()
                if start_date <= task_date <= end_date:
                    daily_data[task_date]['completed'] += 1
        
        # Prepare chart data
        sorted_dates = sorted(daily_data.keys())
        labels = [date.strftime('%m/%d') for date in sorted_dates]
        created_data = [daily_data[date]['created'] for date in sorted_dates]
        completed_data = [daily_data[date]['completed'] for date in sorted_dates]
        
        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Tasks Created',
                    'data': created_data,
                    'borderColor': '#3498db',
                    'backgroundColor': 'rgba(52, 152, 219, 0.1)',
                    'borderWidth': 2,
                    'fill': False,
                    'tension': 0.4
                },
                {
                    'label': 'Tasks Completed',
                    'data': completed_data,
                    'borderColor': '#27ae60',
                    'backgroundColor': 'rgba(39, 174, 96, 0.1)',
                    'borderWidth': 2,
                    'fill': False,
                    'tension': 0.4
                }
            ]
        }
        
        options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top'
                },
                'tooltip': {
                    'mode': 'index',
                    'intersect': False
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
                        'text': 'Date'
                    }
                }
            },
            'interaction': {
                'mode': 'nearest',
                'axis': 'x',
                'intersect': False
            }
        }
        
        return ChartData(
            chart_type=ChartType.LINE,
            title=f"Task Trends ({days} days)",
            data=chart_data,
            options=options
        )
    
    def create_heatmap_chart(self, tasks: List[TaskSchema]) -> ChartData:
        """Create a heatmap for task activity by hour and day"""
        # Initialize heatmap data (7 days x 24 hours)
        heatmap_data = []
        for day in range(7):
            day_data = []
            for hour in range(24):
                day_data.append(0)
            heatmap_data.append(day_data)
        
        # Count tasks by hour and day of week
        for task in tasks:
            if task.metadata.created_at:
                day_of_week = task.metadata.created_at.weekday()  # 0 = Monday
                hour = task.metadata.created_at.hour
                heatmap_data[day_of_week][hour] += 1
        
        # Prepare data for Chart.js heatmap
        data_points = []
        for day in range(7):
            for hour in range(24):
                data_points.append({
                    'x': hour,
                    'y': day,
                    'v': heatmap_data[day][hour]
                })
        
        chart_data = {
            'datasets': [{
                'label': 'Task Activity',
                'data': data_points,
                'backgroundColor': 'rgba(52, 152, 219, 0.8)',
                'borderColor': '#3498db',
                'borderWidth': 1
            }]
        }
        
        options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'display': False
                },
                'tooltip': {
                    'callbacks': {
                        'title': 'function(context) { return "Day " + (context[0].parsed.y + 1) + ", Hour " + context[0].parsed.x; }',
                        'label': 'function(context) { return "Tasks: " + context.parsed.v; }'
                    }
                }
            },
            'scales': {
                'x': {
                    'type': 'linear',
                    'position': 'bottom',
                    'title': {
                        'display': True,
                        'text': 'Hour of Day'
                    },
                    'min': 0,
                    'max': 23,
                    'ticks': {
                        'stepSize': 1
                    }
                },
                'y': {
                    'type': 'linear',
                    'title': {
                        'display': True,
                        'text': 'Day of Week'
                    },
                    'min': 0,
                    'max': 6,
                    'ticks': {
                        'stepSize': 1,
                        'callback': 'function(value) { return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][value]; }'
                    }
                }
            }
        }
        
        return ChartData(
            chart_type=ChartType.HEATMAP,
            title="Task Activity Heatmap",
            data=chart_data,
            options=options
        )
    
    def _create_empty_chart(self, title: str, message: str) -> ChartData:
        """Create an empty chart with a message"""
        chart_data = {
            'labels': ['No Data'],
            'datasets': [{
                'data': [1],
                'backgroundColor': ['#ecf0f1'],
                'borderWidth': 0
            }]
        }
        
        options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'display': False
                },
                'tooltip': {
                    'enabled': False
                }
            }
        }
        
        return ChartData(
            chart_type=ChartType.PIE,
            title=title,
            data=chart_data,
            options=options,
            metadata={'message': message}
        )
    
    def generate_dashboard_charts(self, tasks: List[TaskSchema]) -> Dict[str, ChartData]:
        """Generate all dashboard charts"""
        return {
            'task_status': self.create_task_status_chart(tasks),
            'priority_distribution': self.create_priority_chart(tasks),
            'category_distribution': self.create_category_chart(tasks),
            'resolution_time_trends': self.create_resolution_time_chart(tasks),
            'sla_compliance': self.create_sla_compliance_gauge(tasks),
            'task_trends': self.create_trend_chart(tasks),
            'activity_heatmap': self.create_heatmap_chart(tasks)
        }
    
    def export_chart_data(self, chart_data: ChartData, format: str = 'json') -> str:
        """Export chart data in specified format"""
        if format == 'json':
            return json.dumps({
                'type': chart_data.chart_type.value,
                'title': chart_data.title,
                'data': chart_data.data,
                'options': chart_data.options,
                'metadata': chart_data.metadata
            }, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Export main classes
__all__ = ['DataVisualizer', 'ChartData', 'ChartType']





