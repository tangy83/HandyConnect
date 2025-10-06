"""
Workflow Service for HandyConnect
Automated case workflow management and status transitions
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowAction(Enum):
    """Workflow action types"""
    STATUS_CHANGE = "status_change"
    ASSIGNMENT = "assignment"
    ESCALATION = "escalation"
    NOTIFICATION = "notification"
    EMAIL_RESPONSE = "email_response"
    FOLLOW_UP = "follow_up"
    AUTO_RESOLVE = "auto_resolve"


class WorkflowTrigger(Enum):
    """Workflow trigger types"""
    CASE_CREATED = "case_created"
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    TIME_ELAPSED = "time_elapsed"
    SLA_BREACHED = "sla_breached"
    SLA_AT_RISK = "sla_at_risk"
    NO_ACTIVITY = "no_activity"
    CUSTOMER_REPLY = "customer_reply"


@dataclass
class WorkflowRule:
    """Workflow rule definition"""
    id: str
    name: str
    description: str
    trigger: WorkflowTrigger
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkflowExecution:
    """Workflow execution record"""
    id: str
    rule_id: str
    case_id: str
    trigger: WorkflowTrigger
    executed_at: datetime
    status: str  # success, failed, skipped
    actions_executed: List[str]
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowService:
    """Service for managing case workflows"""
    
    def __init__(self):
        self.rules_file = 'data/workflow_rules.json'
        self.executions_file = 'data/workflow_executions.json'
        self._ensure_data_directory()
        self._load_default_rules()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        import os
        os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
    
    def _load_default_rules(self):
        """Load default workflow rules"""
        if not self._file_exists(self.rules_file):
            default_rules = [
                # Auto-assign high priority cases
                WorkflowRule(
                    id="auto_assign_high_priority",
                    name="Auto-assign High Priority Cases",
                    description="Automatically assign high priority cases to available agents",
                    trigger=WorkflowTrigger.CASE_CREATED,
                    conditions={
                        "priority": ["High", "Urgent", "Critical"],
                        "assigned_to": None
                    },
                    actions=[
                        {"type": "assignment", "assign_to": "auto", "reason": "High priority case auto-assignment"}
                    ]
                ),
                
                # Escalate breached cases
                WorkflowRule(
                    id="escalate_breached_cases",
                    name="Escalate Breached Cases",
                    description="Escalate cases that have breached SLA",
                    trigger=WorkflowTrigger.SLA_BREACHED,
                    conditions={
                        "sla_status": "Breached",
                        "escalated": False
                    },
                    actions=[
                        {"type": "escalation", "escalate_to": "supervisor", "reason": "SLA breach"},
                        {"type": "notification", "notify": ["supervisor", "manager"], "message": "Case has breached SLA"}
                    ]
                ),
                
                # Follow up on at-risk cases
                WorkflowRule(
                    id="follow_up_at_risk",
                    name="Follow up on At-Risk Cases",
                    description="Send follow-up notifications for cases at risk of breaching SLA",
                    trigger=WorkflowTrigger.SLA_AT_RISK,
                    conditions={
                        "sla_status": "At Risk",
                        "notified_at_risk": False
                    },
                    actions=[
                        {"type": "notification", "notify": ["assigned_agent"], "message": "Case is at risk of breaching SLA"},
                        {"type": "status_change", "status": "In Progress", "reason": "SLA risk follow-up"}
                    ]
                ),
                
                # Auto-resolve inactive cases
                WorkflowRule(
                    id="auto_resolve_inactive",
                    name="Auto-resolve Inactive Cases",
                    description="Auto-resolve cases with no activity for extended period",
                    trigger=WorkflowTrigger.NO_ACTIVITY,
                    conditions={
                        "days_since_activity": 7,
                        "status": "Awaiting Customer"
                    },
                    actions=[
                        {"type": "status_change", "status": "Resolved", "reason": "No customer activity for 7 days"},
                        {"type": "notification", "notify": ["customer"], "message": "Case resolved due to inactivity"}
                    ]
                ),
                
                # Update status on customer reply
                WorkflowRule(
                    id="update_status_on_reply",
                    name="Update Status on Customer Reply",
                    description="Update case status when customer replies",
                    trigger=WorkflowTrigger.CUSTOMER_REPLY,
                    conditions={
                        "status": "Awaiting Customer"
                    },
                    actions=[
                        {"type": "status_change", "status": "In Progress", "reason": "Customer replied"},
                        {"type": "notification", "notify": ["assigned_agent"], "message": "Customer has replied to the case"}
                    ]
                )
            ]
            
            self.save_rules(default_rules)
    
    def _file_exists(self, filepath: str) -> bool:
        """Check if file exists"""
        import os
        return os.path.exists(filepath)
    
    def save_rules(self, rules: List[WorkflowRule]):
        """Save workflow rules to file"""
        try:
            rules_dict = []
            for rule in rules:
                rules_dict.append({
                    'id': rule.id,
                    'name': rule.name,
                    'description': rule.description,
                    'trigger': rule.trigger.value,
                    'conditions': rule.conditions,
                    'actions': rule.actions,
                    'enabled': rule.enabled,
                    'created_at': rule.created_at.isoformat(),
                    'updated_at': rule.updated_at.isoformat()
                })
            
            with open(self.rules_file, 'w') as f:
                json.dump(rules_dict, f, indent=2)
            
            logger.info(f"Saved {len(rules)} workflow rules")
        except Exception as e:
            logger.error(f"Error saving workflow rules: {e}")
            raise
    
    def load_rules(self) -> List[WorkflowRule]:
        """Load workflow rules from file"""
        try:
            if not self._file_exists(self.rules_file):
                return []
            
            with open(self.rules_file, 'r') as f:
                rules_dict = json.load(f)
            
            rules = []
            for rule_dict in rules_dict:
                rules.append(WorkflowRule(
                    id=rule_dict['id'],
                    name=rule_dict['name'],
                    description=rule_dict['description'],
                    trigger=WorkflowTrigger(rule_dict['trigger']),
                    conditions=rule_dict['conditions'],
                    actions=rule_dict['actions'],
                    enabled=rule_dict.get('enabled', True),
                    created_at=datetime.fromisoformat(rule_dict.get('created_at', datetime.utcnow().isoformat())),
                    updated_at=datetime.fromisoformat(rule_dict.get('updated_at', datetime.utcnow().isoformat()))
                ))
            
            logger.info(f"Loaded {len(rules)} workflow rules")
            return rules
        except Exception as e:
            logger.error(f"Error loading workflow rules: {e}")
            return []
    
    def save_execution(self, execution: WorkflowExecution):
        """Save workflow execution record"""
        try:
            executions = self.load_executions()
            executions.append(execution)
            
            executions_dict = []
            for exec_record in executions:
                executions_dict.append({
                    'id': exec_record.id,
                    'rule_id': exec_record.rule_id,
                    'case_id': exec_record.case_id,
                    'trigger': exec_record.trigger.value,
                    'executed_at': exec_record.executed_at.isoformat(),
                    'status': exec_record.status,
                    'actions_executed': exec_record.actions_executed,
                    'error_message': exec_record.error_message,
                    'metadata': exec_record.metadata
                })
            
            with open(self.executions_file, 'w') as f:
                json.dump(executions_dict, f, indent=2)
            
            logger.info(f"Saved workflow execution record: {execution.id}")
        except Exception as e:
            logger.error(f"Error saving workflow execution: {e}")
    
    def load_executions(self) -> List[WorkflowExecution]:
        """Load workflow execution records"""
        try:
            if not self._file_exists(self.executions_file):
                return []
            
            with open(self.executions_file, 'r') as f:
                executions_dict = json.load(f)
            
            executions = []
            for exec_dict in executions_dict:
                executions.append(WorkflowExecution(
                    id=exec_dict['id'],
                    rule_id=exec_dict['rule_id'],
                    case_id=exec_dict['case_id'],
                    trigger=WorkflowTrigger(exec_dict['trigger']),
                    executed_at=datetime.fromisoformat(exec_dict['executed_at']),
                    status=exec_dict['status'],
                    actions_executed=exec_dict['actions_executed'],
                    error_message=exec_dict.get('error_message'),
                    metadata=exec_dict.get('metadata', {})
                ))
            
            return executions
        except Exception as e:
            logger.error(f"Error loading workflow executions: {e}")
            return []
    
    def evaluate_conditions(self, case: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """Evaluate workflow conditions against a case"""
        try:
            for condition_key, condition_value in conditions.items():
                case_value = case.get(condition_key)
                
                if condition_key == "priority":
                    if case_value not in condition_value:
                        return False
                elif condition_key == "assigned_to":
                    if condition_value is None and case_value is not None:
                        return False
                    if condition_value is not None and case_value is None:
                        return False
                elif condition_key == "sla_status":
                    if case_value != condition_value:
                        return False
                elif condition_key == "escalated":
                    if case_value != condition_value:
                        return False
                elif condition_key == "status":
                    if case_value != condition_value:
                        return False
                elif condition_key == "days_since_activity":
                    if case_value is None:
                        return False
                    if not isinstance(case_value, (int, float)):
                        return False
                    if case_value < condition_value:
                        return False
                elif condition_key == "notified_at_risk":
                    if case_value != condition_value:
                        return False
                
            return True
        except Exception as e:
            logger.error(f"Error evaluating conditions: {e}")
            return False
    
    def execute_workflow(self, case: Dict[str, Any], trigger: WorkflowTrigger, 
                        sla_status: Optional[str] = None) -> List[WorkflowExecution]:
        """Execute workflows for a case based on trigger"""
        try:
            executions = []
            rules = self.load_rules()
            
            # Filter rules by trigger and enabled status
            applicable_rules = [
                rule for rule in rules 
                if rule.trigger == trigger and rule.enabled
            ]
            
            for rule in applicable_rules:
                # Prepare case data for condition evaluation
                evaluation_case = case.copy()
                
                # Add SLA status if provided
                if sla_status:
                    evaluation_case['sla_status'] = sla_status
                
                # Add calculated fields
                evaluation_case['days_since_activity'] = self._calculate_days_since_activity(case)
                evaluation_case['notified_at_risk'] = case.get('notified_at_risk', False)
                
                # Evaluate conditions
                if self.evaluate_conditions(evaluation_case, rule.conditions):
                    # Execute workflow
                    execution = self._execute_rule(case, rule, trigger)
                    if execution:
                        executions.append(execution)
                        self.save_execution(execution)
            
            return executions
        except Exception as e:
            logger.error(f"Error executing workflow for case {case.get('case_id', 'unknown')}: {e}")
            return []
    
    def _calculate_days_since_activity(self, case: Dict[str, Any]) -> float:
        """Calculate days since last activity"""
        try:
            last_activity = case.get('case_metadata', {}).get('last_activity_date')
            if not last_activity:
                last_activity = case.get('updated_at')
            
            if last_activity:
                last_activity_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                now = datetime.utcnow()
                return (now - last_activity_date).total_seconds() / 86400  # Convert to days
            
            return 0
        except Exception as e:
            logger.error(f"Error calculating days since activity: {e}")
            return 0
    
    def _execute_rule(self, case: Dict[str, Any], rule: WorkflowRule, trigger: WorkflowTrigger) -> Optional[WorkflowExecution]:
        """Execute a specific workflow rule"""
        try:
            import uuid
            
            execution_id = str(uuid.uuid4())
            actions_executed = []
            error_message = None
            
            for action in rule.actions:
                try:
                    action_type = action.get('type')
                    
                    if action_type == 'assignment':
                        success = self._execute_assignment_action(case, action)
                        if success:
                            actions_executed.append(f"assignment_to_{action.get('assign_to', 'auto')}")
                    
                    elif action_type == 'status_change':
                        success = self._execute_status_change_action(case, action)
                        if success:
                            actions_executed.append(f"status_change_to_{action.get('status')}")
                    
                    elif action_type == 'escalation':
                        success = self._execute_escalation_action(case, action)
                        if success:
                            actions_executed.append(f"escalation_to_{action.get('escalate_to')}")
                    
                    elif action_type == 'notification':
                        success = self._execute_notification_action(case, action)
                        if success:
                            actions_executed.append(f"notification_to_{action.get('notify', 'unknown')}")
                    
                    elif action_type == 'auto_resolve':
                        success = self._execute_auto_resolve_action(case, action)
                        if success:
                            actions_executed.append("auto_resolve")
                    
                except Exception as e:
                    logger.error(f"Error executing action {action_type}: {e}")
                    error_message = f"Action {action_type} failed: {str(e)}"
                    break
            
            status = "success" if not error_message else "failed"
            
            return WorkflowExecution(
                id=execution_id,
                rule_id=rule.id,
                case_id=case['case_id'],
                trigger=trigger,
                executed_at=datetime.utcnow(),
                status=status,
                actions_executed=actions_executed,
                error_message=error_message,
                metadata={
                    'rule_name': rule.name,
                    'case_number': case.get('case_number'),
                    'trigger_data': {'sla_status': case.get('sla_status')}
                }
            )
            
        except Exception as e:
            logger.error(f"Error executing rule {rule.id}: {e}")
            return None
    
    def _execute_assignment_action(self, case: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """Execute assignment action"""
        try:
            assign_to = action.get('assign_to', 'auto')
            reason = action.get('reason', 'Workflow assignment')
            
            # For now, implement basic auto-assignment logic
            # In a real implementation, this would integrate with agent management
            if assign_to == 'auto':
                # Simple round-robin or availability-based assignment
                available_agents = ['agent1', 'agent2', 'agent3']  # This would come from agent service
                assigned_agent = available_agents[0]  # Simple assignment
            else:
                assigned_agent = assign_to
            
            # Update case assignment
            case['assigned_to'] = assigned_agent
            case['updated_at'] = datetime.utcnow().isoformat()
            
            # Add timeline event
            if 'timeline' not in case:
                case['timeline'] = []
            
            case['timeline'].append({
                'event_id': f"workflow_assignment_{datetime.utcnow().timestamp()}",
                'event_type': 'assigned',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': 'workflow_system',
                'description': f"Auto-assigned to {assigned_agent} ({reason})",
                'metadata': {
                    'assignment_reason': reason,
                    'workflow_triggered': True
                }
            })
            
            logger.info(f"Case {case.get('case_number')} assigned to {assigned_agent} via workflow")
            return True
            
        except Exception as e:
            logger.error(f"Error executing assignment action: {e}")
            return False
    
    def _execute_status_change_action(self, case: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """Execute status change action"""
        try:
            new_status = action.get('status')
            reason = action.get('reason', 'Workflow status change')
            
            old_status = case.get('status')
            case['status'] = new_status
            case['updated_at'] = datetime.utcnow().isoformat()
            
            # Add timeline event
            if 'timeline' not in case:
                case['timeline'] = []
            
            case['timeline'].append({
                'event_id': f"workflow_status_change_{datetime.utcnow().timestamp()}",
                'event_type': 'status_changed',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': 'workflow_system',
                'description': f"Status changed from {old_status} to {new_status} ({reason})",
                'metadata': {
                    'old_status': old_status,
                    'new_status': new_status,
                    'change_reason': reason,
                    'workflow_triggered': True
                }
            })
            
            logger.info(f"Case {case.get('case_number')} status changed to {new_status} via workflow")
            return True
            
        except Exception as e:
            logger.error(f"Error executing status change action: {e}")
            return False
    
    def _execute_escalation_action(self, case: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """Execute escalation action"""
        try:
            escalate_to = action.get('escalate_to', 'supervisor')
            reason = action.get('reason', 'Workflow escalation')
            
            case['escalated'] = True
            case['escalation_date'] = datetime.utcnow().isoformat()
            case['escalated_to'] = escalate_to
            case['updated_at'] = datetime.utcnow().isoformat()
            
            # Add timeline event
            if 'timeline' not in case:
                case['timeline'] = []
            
            case['timeline'].append({
                'event_id': f"workflow_escalation_{datetime.utcnow().timestamp()}",
                'event_type': 'escalated',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': 'workflow_system',
                'description': f"Escalated to {escalate_to} ({reason})",
                'metadata': {
                    'escalation_reason': reason,
                    'escalated_to': escalate_to,
                    'workflow_triggered': True
                }
            })
            
            logger.info(f"Case {case.get('case_number')} escalated to {escalate_to} via workflow")
            return True
            
        except Exception as e:
            logger.error(f"Error executing escalation action: {e}")
            return False
    
    def _execute_notification_action(self, case: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """Execute notification action"""
        try:
            notify_to = action.get('notify', [])
            message = action.get('message', 'Workflow notification')
            
            # For now, just log the notification
            # In a real implementation, this would integrate with notification service
            logger.info(f"Notification for case {case.get('case_number')}: {message} to {notify_to}")
            
            # Add timeline event
            if 'timeline' not in case:
                case['timeline'] = []
            
            case['timeline'].append({
                'event_id': f"workflow_notification_{datetime.utcnow().timestamp()}",
                'event_type': 'notification_sent',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': 'workflow_system',
                'description': f"Notification sent: {message}",
                'metadata': {
                    'notification_recipients': notify_to,
                    'notification_message': message,
                    'workflow_triggered': True
                }
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing notification action: {e}")
            return False
    
    def _execute_auto_resolve_action(self, case: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """Execute auto-resolve action"""
        try:
            reason = action.get('reason', 'Workflow auto-resolution')
            
            case['status'] = 'Resolved'
            case['resolved_at'] = datetime.utcnow().isoformat()
            case['resolution_reason'] = reason
            case['updated_at'] = datetime.utcnow().isoformat()
            
            # Add timeline event
            if 'timeline' not in case:
                case['timeline'] = []
            
            case['timeline'].append({
                'event_id': f"workflow_auto_resolve_{datetime.utcnow().timestamp()}",
                'event_type': 'auto_resolved',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': 'workflow_system',
                'description': f"Case auto-resolved ({reason})",
                'metadata': {
                    'resolution_reason': reason,
                    'workflow_triggered': True
                }
            })
            
            logger.info(f"Case {case.get('case_number')} auto-resolved via workflow")
            return True
            
        except Exception as e:
            logger.error(f"Error executing auto-resolve action: {e}")
            return False
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        try:
            executions = self.load_executions()
            rules = self.load_rules()
            
            total_executions = len(executions)
            successful_executions = len([e for e in executions if e.status == 'success'])
            failed_executions = len([e for e in executions if e.status == 'failed'])
            
            # Group by rule
            rule_stats = {}
            for rule in rules:
                rule_executions = [e for e in executions if e.rule_id == rule.id]
                rule_stats[rule.name] = {
                    'total_executions': len(rule_executions),
                    'successful_executions': len([e for e in rule_executions if e.status == 'success']),
                    'failed_executions': len([e for e in rule_executions if e.status == 'failed']),
                    'enabled': rule.enabled
                }
            
            return {
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'success_rate': round((successful_executions / total_executions * 100) if total_executions > 0 else 0, 2),
                'total_rules': len(rules),
                'enabled_rules': len([r for r in rules if r.enabled]),
                'rule_statistics': rule_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow statistics: {e}")
            return {}
