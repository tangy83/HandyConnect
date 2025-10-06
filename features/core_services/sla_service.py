"""
SLA Service for HandyConnect
Service Level Agreement management and monitoring
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SLAPriority(Enum):
    """SLA priority levels with time limits (in hours)"""
    CRITICAL = 2
    URGENT = 4
    HIGH = 8
    MEDIUM = 24
    LOW = 72


class SLAStatus(Enum):
    """SLA status enumeration"""
    ON_TIME = "On Time"
    AT_RISK = "At Risk"
    BREACHED = "Breached"
    N_A = "N/A"


@dataclass
class SLAConfiguration:
    """SLA configuration for different case types and priorities"""
    case_type: str
    priority: str
    response_time_hours: int
    resolution_time_hours: int
    escalation_time_hours: Optional[int] = None
    auto_escalate: bool = False
    notify_on_risk: bool = True
    notify_on_breach: bool = True


@dataclass
class SLAMetrics:
    """SLA metrics for a case"""
    case_id: str
    priority: str
    case_type: str
    response_time_hours: int
    resolution_time_hours: int
    response_due_date: datetime
    resolution_due_date: datetime
    response_status: SLAStatus
    resolution_status: SLAStatus
    response_time_remaining_hours: float
    resolution_time_remaining_hours: float
    escalation_triggered: bool = False
    last_escalation_date: Optional[datetime] = None


class SLAService:
    """Service for managing SLAs"""
    
    def __init__(self):
        self.data_file = 'data/sla_configurations.json'
        self.metrics_file = 'data/sla_metrics.json'
        self._ensure_data_directory()
        self._load_default_configurations()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def _load_default_configurations(self):
        """Load default SLA configurations"""
        if not os.path.exists(self.data_file):
            default_configs = [
                # Critical cases
                SLAConfiguration("Security", "Critical", 1, 4, 2, True, True, True),
                SLAConfiguration("General", "Critical", 1, 4, 2, True, True, True),
                
                # Urgent cases
                SLAConfiguration("Complaint", "Urgent", 2, 8, 4, True, True, True),
                SLAConfiguration("Billing", "Urgent", 2, 8, 4, True, True, True),
                SLAConfiguration("General", "Urgent", 2, 8, 4, True, True, True),
                
                # High priority cases
                SLAConfiguration("Complaint", "High", 4, 24, 12, True, True, True),
                SLAConfiguration("Request", "High", 4, 24, 12, True, True, True),
                SLAConfiguration("General", "High", 4, 24, 12, True, True, True),
                
                # Medium priority cases
                SLAConfiguration("Complaint", "Medium", 8, 48, 24, False, True, True),
                SLAConfiguration("Request", "Medium", 8, 48, 24, False, True, True),
                SLAConfiguration("Query", "Medium", 8, 48, 24, False, True, True),
                SLAConfiguration("General", "Medium", 8, 48, 24, False, True, True),
                
                # Low priority cases
                SLAConfiguration("Feedback", "Low", 24, 168, 72, False, False, True),
                SLAConfiguration("Suggestion", "Low", 24, 168, 72, False, False, True),
                SLAConfiguration("General", "Low", 24, 168, 72, False, False, True),
            ]
            
            self.save_configurations(default_configs)
    
    def save_configurations(self, configurations: List[SLAConfiguration]):
        """Save SLA configurations to file"""
        try:
            configs_dict = []
            for config in configurations:
                configs_dict.append({
                    'case_type': config.case_type,
                    'priority': config.priority,
                    'response_time_hours': config.response_time_hours,
                    'resolution_time_hours': config.resolution_time_hours,
                    'escalation_time_hours': config.escalation_time_hours,
                    'auto_escalate': config.auto_escalate,
                    'notify_on_risk': config.notify_on_risk,
                    'notify_on_breach': config.notify_on_breach
                })
            
            with open(self.data_file, 'w') as f:
                json.dump(configs_dict, f, indent=2)
            
            logger.info(f"Saved {len(configurations)} SLA configurations")
        except Exception as e:
            logger.error(f"Error saving SLA configurations: {e}")
            raise
    
    def load_configurations(self) -> List[SLAConfiguration]:
        """Load SLA configurations from file"""
        try:
            if not os.path.exists(self.data_file):
                return []
            
            with open(self.data_file, 'r') as f:
                configs_dict = json.load(f)
            
            configurations = []
            for config_dict in configs_dict:
                configurations.append(SLAConfiguration(
                    case_type=config_dict['case_type'],
                    priority=config_dict['priority'],
                    response_time_hours=config_dict['response_time_hours'],
                    resolution_time_hours=config_dict['resolution_time_hours'],
                    escalation_time_hours=config_dict.get('escalation_time_hours'),
                    auto_escalate=config_dict.get('auto_escalate', False),
                    notify_on_risk=config_dict.get('notify_on_risk', True),
                    notify_on_breach=config_dict.get('notify_on_breach', True)
                ))
            
            logger.info(f"Loaded {len(configurations)} SLA configurations")
            return configurations
        except Exception as e:
            logger.error(f"Error loading SLA configurations: {e}")
            return []
    
    def get_sla_configuration(self, case_type: str, priority: str) -> Optional[SLAConfiguration]:
        """Get SLA configuration for specific case type and priority"""
        configurations = self.load_configurations()
        
        # First try exact match
        for config in configurations:
            if config.case_type == case_type and config.priority == priority:
                return config
        
        # Fallback to General case type
        for config in configurations:
            if config.case_type == "General" and config.priority == priority:
                return config
        
        # Final fallback to Medium priority
        for config in configurations:
            if config.case_type == case_type and config.priority == "Medium":
                return config
        
        # Ultimate fallback to General Medium
        for config in configurations:
            if config.case_type == "General" and config.priority == "Medium":
                return config
        
        return None
    
    def calculate_sla_metrics(self, case: Dict[str, Any]) -> Optional[SLAMetrics]:
        """Calculate SLA metrics for a case"""
        try:
            case_type = case.get('case_type', 'General')
            priority = case.get('priority', 'Medium')
            created_at = datetime.fromisoformat(case.get('created_at', datetime.utcnow().isoformat()))
            updated_at = datetime.fromisoformat(case.get('updated_at', datetime.utcnow().isoformat()))
            
            # Get SLA configuration
            config = self.get_sla_configuration(case_type, priority)
            if not config:
                logger.warning(f"No SLA configuration found for {case_type}/{priority}")
                return None
            
            # Calculate due dates
            response_due_date = created_at + timedelta(hours=config.response_time_hours)
            resolution_due_date = created_at + timedelta(hours=config.resolution_time_hours)
            
            # Calculate time remaining
            now = datetime.utcnow()
            response_time_remaining = (response_due_date - now).total_seconds() / 3600
            resolution_time_remaining = (resolution_due_date - now).total_seconds() / 3600
            
            # Determine SLA status
            response_status = self._determine_sla_status(response_time_remaining, config.response_time_hours)
            resolution_status = self._determine_sla_status(resolution_time_remaining, config.resolution_time_hours)
            
            # Check if escalation should be triggered
            escalation_triggered = False
            last_escalation_date = None
            
            if config.escalation_time_hours:
                escalation_due_date = created_at + timedelta(hours=config.escalation_time_hours)
                if now > escalation_due_date and not case.get('escalated', False):
                    escalation_triggered = True
                    last_escalation_date = now
            
            return SLAMetrics(
                case_id=case['case_id'],
                priority=priority,
                case_type=case_type,
                response_time_hours=config.response_time_hours,
                resolution_time_hours=config.resolution_time_hours,
                response_due_date=response_due_date,
                resolution_due_date=resolution_due_date,
                response_status=response_status,
                resolution_status=resolution_status,
                response_time_remaining_hours=response_time_remaining,
                resolution_time_remaining_hours=resolution_time_remaining,
                escalation_triggered=escalation_triggered,
                last_escalation_date=last_escalation_date
            )
            
        except Exception as e:
            logger.error(f"Error calculating SLA metrics for case {case.get('case_id', 'unknown')}: {e}")
            return None
    
    def _determine_sla_status(self, time_remaining_hours: float, total_time_hours: int) -> SLAStatus:
        """Determine SLA status based on time remaining"""
        if time_remaining_hours < 0:
            return SLAStatus.BREACHED
        elif time_remaining_hours < (total_time_hours * 0.25):  # Less than 25% time remaining
            return SLAStatus.AT_RISK
        else:
            return SLAStatus.ON_TIME
    
    def update_case_sla_status(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Update case with current SLA status"""
        try:
            metrics = self.calculate_sla_metrics(case)
            if not metrics:
                return case
            
            # Update case with SLA information
            case['sla_metrics'] = {
                'response_due_date': metrics.response_due_date.isoformat(),
                'resolution_due_date': metrics.resolution_due_date.isoformat(),
                'response_status': metrics.response_status.value,
                'resolution_status': metrics.resolution_status.value,
                'response_time_remaining_hours': metrics.response_time_remaining_hours,
                'resolution_time_remaining_hours': metrics.resolution_time_remaining_hours
            }
            
            # Update overall SLA status (use resolution status as primary)
            case['sla_status'] = metrics.resolution_status.value
            
            # Handle escalation
            if metrics.escalation_triggered:
                case['escalated'] = True
                case['escalation_date'] = metrics.last_escalation_date.isoformat()
                
                # Add timeline event
                if 'timeline' not in case:
                    case['timeline'] = []
                
                case['timeline'].append({
                    'event_id': f"escalation_{datetime.utcnow().timestamp()}",
                    'event_type': 'escalated',
                    'timestamp': metrics.last_escalation_date.isoformat(),
                    'actor': 'system',
                    'description': f"Case escalated due to SLA breach ({metrics.priority} priority)",
                    'metadata': {
                        'escalation_reason': 'sla_breach',
                        'priority': metrics.priority,
                        'case_type': metrics.case_type
                    }
                })
            
            return case
            
        except Exception as e:
            logger.error(f"Error updating case SLA status: {e}")
            return case
    
    def get_sla_compliance_report(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate SLA compliance report"""
        try:
            total_cases = len(cases)
            if total_cases == 0:
                return {
                    'total_cases': 0,
                    'compliance_rate': 0,
                    'breached_cases': 0,
                    'at_risk_cases': 0,
                    'on_time_cases': 0,
                    'escalated_cases': 0
                }
            
            breached_cases = 0
            at_risk_cases = 0
            on_time_cases = 0
            escalated_cases = 0
            
            for case in cases:
                sla_status = case.get('sla_status', 'N/A')
                if sla_status == 'Breached':
                    breached_cases += 1
                elif sla_status == 'At Risk':
                    at_risk_cases += 1
                elif sla_status == 'On Time':
                    on_time_cases += 1
                
                if case.get('escalated', False):
                    escalated_cases += 1
            
            compliance_rate = round((on_time_cases / total_cases) * 100, 2)
            
            return {
                'total_cases': total_cases,
                'compliance_rate': compliance_rate,
                'breached_cases': breached_cases,
                'at_risk_cases': at_risk_cases,
                'on_time_cases': on_time_cases,
                'escalated_cases': escalated_cases,
                'breach_rate': round((breached_cases / total_cases) * 100, 2),
                'risk_rate': round((at_risk_cases / total_cases) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Error generating SLA compliance report: {e}")
            return {}
    
    def get_sla_trends(self, cases: List[Dict[str, Any]], days: int = 30) -> Dict[str, Any]:
        """Get SLA trends over time"""
        try:
            # Group cases by date
            daily_metrics = {}
            
            for case in cases:
                try:
                    created_at = datetime.fromisoformat(case.get('created_at', ''))
                    date_key = created_at.strftime('%Y-%m-%d')
                    
                    if date_key not in daily_metrics:
                        daily_metrics[date_key] = {
                            'total_cases': 0,
                            'breached_cases': 0,
                            'at_risk_cases': 0,
                            'on_time_cases': 0,
                            'escalated_cases': 0
                        }
                    
                    daily_metrics[date_key]['total_cases'] += 1
                    
                    sla_status = case.get('sla_status', 'N/A')
                    if sla_status == 'Breached':
                        daily_metrics[date_key]['breached_cases'] += 1
                    elif sla_status == 'At Risk':
                        daily_metrics[date_key]['at_risk_cases'] += 1
                    elif sla_status == 'On Time':
                        daily_metrics[date_key]['on_time_cases'] += 1
                    
                    if case.get('escalated', False):
                        daily_metrics[date_key]['escalated_cases'] += 1
                        
                except Exception as e:
                    logger.warning(f"Error processing case for SLA trends: {e}")
                    continue
            
            # Create trend data for the specified period
            trend_data = []
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
                metrics = daily_metrics.get(date, {
                    'total_cases': 0,
                    'breached_cases': 0,
                    'at_risk_cases': 0,
                    'on_time_cases': 0,
                    'escalated_cases': 0
                })
                
                compliance_rate = 0
                if metrics['total_cases'] > 0:
                    compliance_rate = round((metrics['on_time_cases'] / metrics['total_cases']) * 100, 2)
                
                trend_data.append({
                    'date': date,
                    'total_cases': metrics['total_cases'],
                    'breached_cases': metrics['breached_cases'],
                    'at_risk_cases': metrics['at_risk_cases'],
                    'on_time_cases': metrics['on_time_cases'],
                    'escalated_cases': metrics['escalated_cases'],
                    'compliance_rate': compliance_rate
                })
            
            # Reverse to show chronologically
            trend_data.reverse()
            
            return {
                'period_days': days,
                'trend_data': trend_data,
                'summary': {
                    'total_cases': sum(d['total_cases'] for d in trend_data),
                    'avg_compliance_rate': round(sum(d['compliance_rate'] for d in trend_data) / len(trend_data), 2) if trend_data else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting SLA trends: {e}")
            return {}
    
    def get_cases_at_risk(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get cases that are at risk of breaching SLA"""
        try:
            at_risk_cases = []
            
            for case in cases:
                sla_status = case.get('sla_status', 'N/A')
                if sla_status == 'At Risk':
                    at_risk_cases.append(case)
            
            # Sort by priority and time remaining
            def sort_key(case):
                priority_order = {'Critical': 5, 'Urgent': 4, 'High': 3, 'Medium': 2, 'Low': 1}
                priority = case.get('priority', 'Medium')
                time_remaining = case.get('sla_metrics', {}).get('resolution_time_remaining_hours', 0)
                return (-priority_order.get(priority, 0), time_remaining)
            
            at_risk_cases.sort(key=sort_key)
            return at_risk_cases
            
        except Exception as e:
            logger.error(f"Error getting cases at risk: {e}")
            return []
    
    def get_cases_breached(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get cases that have breached SLA"""
        try:
            breached_cases = []
            
            for case in cases:
                sla_status = case.get('sla_status', 'N/A')
                if sla_status == 'Breached':
                    breached_cases.append(case)
            
            # Sort by breach time (most recent first)
            def sort_key(case):
                breach_time = case.get('sla_metrics', {}).get('resolution_due_date', '')
                try:
                    return datetime.fromisoformat(breach_time)
                except:
                    return datetime.min
            
            breached_cases.sort(key=sort_key, reverse=True)
            return breached_cases
            
        except Exception as e:
            logger.error(f"Error getting cases breached: {e}")
            return []
