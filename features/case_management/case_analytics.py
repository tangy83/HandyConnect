"""
Case Analytics API for HandyConnect
Analytics and reporting endpoints for case management
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..core_services.case_service import CaseService
from ..core_services.task_service import TaskService

logger = logging.getLogger(__name__)

# Create blueprint
case_analytics_bp = Blueprint('case_analytics', __name__, url_prefix='/api/cases/analytics')

# Initialize services
case_service = CaseService()
task_service = TaskService()

def success_response(data=None, message="Success", status_code=200):
    """Standard success response format"""
    response = {"status": "success", "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def error_response(message="Error", status_code=400, error_details=None):
    """Standard error response format"""
    response = {"status": "error", "message": message}
    if error_details:
        response["error"] = error_details
    return jsonify(response), status_code

@case_analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_metrics():
    """Get dashboard metrics for case management"""
    try:
        # Use advanced analytics if available
        advanced_analytics = case_service.get_advanced_case_analytics()
        
        if advanced_analytics.get('advanced_features_enabled', {}).get('sla_service'):
            # Return advanced analytics
            return success_response(advanced_analytics, "Advanced dashboard metrics retrieved successfully")
        
        # Fallback to basic analytics
        cases = case_service.load_cases()
        tasks = task_service.load_tasks()
        
        # Basic metrics
        total_cases = len(cases)
        open_cases = len([c for c in cases if c.get('status') not in ['Resolved', 'Closed']])
        resolved_cases = len([c for c in cases if c.get('status') == 'Resolved'])
        closed_cases = len([c for c in cases if c.get('status') == 'Closed'])
        
        # Priority breakdown
        priority_breakdown = {}
        for case in cases:
            priority = case.get('priority', 'Unknown')
            priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
        
        # Status breakdown
        status_breakdown = {}
        for case in cases:
            status = case.get('status', 'Unknown')
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        # SLA metrics
        sla_on_time = len([c for c in cases if c.get('sla_status') == 'On Time'])
        sla_at_risk = len([c for c in cases if c.get('sla_status') == 'At Risk'])
        sla_breached = len([c for c in cases if c.get('sla_status') == 'Breached'])
        
        # Recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_cases = []
        for case in cases:
            created_at = case.get('created_at', '')
            if created_at:
                try:
                    case_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if case_date >= seven_days_ago:
                        recent_cases.append(case)
                except:
                    continue
        
        # Case resolution time (for resolved cases)
        resolution_times = []
        for case in cases:
            if case.get('status') in ['Resolved', 'Closed']:
                try:
                    created_at = datetime.fromisoformat(case.get('created_at', '').replace('Z', '+00:00'))
                    updated_at = datetime.fromisoformat(case.get('updated_at', '').replace('Z', '+00:00'))
                    resolution_time = (updated_at - created_at).total_seconds() / 3600  # hours
                    resolution_times.append(resolution_time)
                except:
                    continue
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Task metrics
        total_tasks = len(tasks)
        tasks_with_cases = len([t for t in tasks if t.get('case_id')])
        
        dashboard_data = {
            "overview": {
                "total_cases": total_cases,
                "open_cases": open_cases,
                "resolved_cases": resolved_cases,
                "closed_cases": closed_cases,
                "total_tasks": total_tasks,
                "tasks_with_cases": tasks_with_cases
            },
            "priority_breakdown": priority_breakdown,
            "status_breakdown": status_breakdown,
            "sla_metrics": {
                "on_time": sla_on_time,
                "at_risk": sla_at_risk,
                "breached": sla_breached,
                "compliance_rate": round((sla_on_time / total_cases * 100) if total_cases > 0 else 0, 2)
            },
            "performance_metrics": {
                "avg_resolution_time_hours": round(avg_resolution_time, 2),
                "recent_cases_7_days": len(recent_cases),
                "resolution_rate": round((resolved_cases / total_cases * 100) if total_cases > 0 else 0, 2)
            }
        }
        
        return success_response(dashboard_data, "Retrieved dashboard metrics")
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        return error_response("Failed to retrieve dashboard metrics", 500, str(e))

@case_analytics_bp.route('/trends', methods=['GET'])
def get_case_trends():
    """Get case trends over time"""
    try:
        days = request.args.get('days', 30, type=int)
        cases = case_service.load_cases()
        
        # Group cases by date
        daily_cases = {}
        daily_resolved = {}
        
        for case in cases:
            try:
                created_at = datetime.fromisoformat(case.get('created_at', '').replace('Z', '+00:00'))
                updated_at = datetime.fromisoformat(case.get('updated_at', '').replace('Z', '+00:00'))
                
                # Only include cases from the specified period
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                if created_at >= cutoff_date:
                    date_key = created_at.strftime('%Y-%m-%d')
                    daily_cases[date_key] = daily_cases.get(date_key, 0) + 1
                
                # Track resolved cases
                if case.get('status') in ['Resolved', 'Closed'] and updated_at >= cutoff_date:
                    date_key = updated_at.strftime('%Y-%m-%d')
                    daily_resolved[date_key] = daily_resolved.get(date_key, 0) + 1
                    
            except:
                continue
        
        # Create trend data
        trend_data = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            trend_data.append({
                'date': date,
                'cases_created': daily_cases.get(date, 0),
                'cases_resolved': daily_resolved.get(date, 0)
            })
        
        # Reverse to show chronologically
        trend_data.reverse()
        
        # Calculate totals
        total_created = sum(daily_cases.values())
        total_resolved = sum(daily_resolved.values())
        
        response_data = {
            "period_days": days,
            "trend_data": trend_data,
            "totals": {
                "cases_created": total_created,
                "cases_resolved": total_resolved,
                "net_cases": total_created - total_resolved
            }
        }
        
        return success_response(response_data, f"Retrieved {days}-day case trends")
        
    except Exception as e:
        logger.error(f"Error getting case trends: {e}")
        return error_response("Failed to retrieve case trends", 500, str(e))

@case_analytics_bp.route('/performance', methods=['GET'])
def get_performance_metrics():
    """Get case performance metrics"""
    try:
        cases = case_service.load_cases()
        
        # Resolution time analysis
        resolution_times = []
        sla_compliance = []
        
        for case in cases:
            try:
                created_at = datetime.fromisoformat(case.get('created_at', '').replace('Z', '+00:00'))
                updated_at = datetime.fromisoformat(case.get('updated_at', '').replace('Z', '+00:00'))
                
                # Calculate resolution time
                resolution_time = (updated_at - created_at).total_seconds() / 3600  # hours
                resolution_times.append(resolution_time)
                
                # SLA compliance
                sla_status = case.get('sla_status', 'Unknown')
                sla_compliance.append(sla_status == 'On Time')
                
            except:
                continue
        
        # Calculate metrics
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        sla_compliance_rate = sum(sla_compliance) / len(sla_compliance) * 100 if sla_compliance else 0
        
        # Priority performance
        priority_performance = {}
        for priority in ['Low', 'Medium', 'High', 'Urgent', 'Critical']:
            priority_cases = [c for c in cases if c.get('priority') == priority]
            if priority_cases:
                priority_resolution_times = []
                for case in priority_cases:
                    try:
                        created_at = datetime.fromisoformat(case.get('created_at', '').replace('Z', '+00:00'))
                        updated_at = datetime.fromisoformat(case.get('updated_at', '').replace('Z', '+00:00'))
                        resolution_time = (updated_at - created_at).total_seconds() / 3600
                        priority_resolution_times.append(resolution_time)
                    except:
                        continue
                
                avg_priority_time = sum(priority_resolution_times) / len(priority_resolution_times) if priority_resolution_times else 0
                priority_performance[priority] = {
                    'case_count': len(priority_cases),
                    'avg_resolution_time_hours': round(avg_priority_time, 2)
                }
        
        response_data = {
            "overall_performance": {
                "avg_resolution_time_hours": round(avg_resolution_time, 2),
                "sla_compliance_rate": round(sla_compliance_rate, 2),
                "total_cases_analyzed": len(resolution_times)
            },
            "priority_performance": priority_performance
        }
        
        return success_response(response_data, "Retrieved performance metrics")
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return error_response("Failed to retrieve performance metrics", 500, str(e))

@case_analytics_bp.route('/reports', methods=['GET'])
def generate_case_report():
    """Generate comprehensive case report"""
    try:
        report_type = request.args.get('type', 'summary')  # summary, detailed, export
        cases = case_service.load_cases()
        tasks = task_service.load_tasks()
        
        # Get advanced analytics if available
        advanced_analytics = case_service.get_advanced_case_analytics()
        
        # Basic report data
        report_data = {
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_cases": len(cases),
                "total_tasks": len(tasks),
                "tasks_with_cases": len([t for t in tasks if t.get('case_id')])
            },
            "advanced_features": advanced_analytics.get('advanced_features_enabled', {})
        }
        
        if report_type == 'summary':
            # Summary report
            status_breakdown = {}
            priority_breakdown = {}
            type_breakdown = {}
            
            for case in cases:
                # Status breakdown
                status = case.get('status', 'Unknown')
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
                
                # Priority breakdown
                priority = case.get('priority', 'Unknown')
                priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
                
                # Type breakdown
                case_type = case.get('case_type', 'Unknown')
                type_breakdown[case_type] = type_breakdown.get(case_type, 0) + 1
            
            report_data["breakdowns"] = {
                "status": status_breakdown,
                "priority": priority_breakdown,
                "type": type_breakdown
            }
            
            # Add advanced metrics if available
            if advanced_analytics.get('sla_analytics'):
                report_data["sla_metrics"] = advanced_analytics['sla_analytics']
            if advanced_analytics.get('workflow_analytics'):
                report_data["workflow_metrics"] = advanced_analytics['workflow_analytics']
            if advanced_analytics.get('notification_analytics'):
                report_data["notification_metrics"] = advanced_analytics['notification_analytics']
            
        elif report_type == 'detailed':
            # Detailed report with all case data
            report_data["cases"] = cases
            report_data["tasks"] = tasks
            
            # Add advanced analytics
            if advanced_analytics:
                report_data["advanced_analytics"] = advanced_analytics
            
        elif report_type == 'export':
            # Export-ready format
            export_data = []
            for case in cases:
                export_data.append({
                    "case_number": case.get('case_number'),
                    "case_title": case.get('case_title'),
                    "status": case.get('status'),
                    "priority": case.get('priority'),
                    "case_type": case.get('case_type'),
                    "customer_name": case.get('customer_info', {}).get('name'),
                    "customer_email": case.get('customer_info', {}).get('email'),
                    "assigned_to": case.get('assigned_to'),
                    "created_at": case.get('created_at'),
                    "updated_at": case.get('updated_at'),
                    "sla_status": case.get('sla_status'),
                    "escalated": case.get('escalated', False),
                    "sla_metrics": case.get('sla_metrics', {})
                })
            
            report_data["export_data"] = export_data
        
        return success_response(report_data, f"Generated {report_type} case report")
        
    except Exception as e:
        logger.error(f"Error generating case report: {e}")
        return error_response("Failed to generate case report", 500, str(e))
