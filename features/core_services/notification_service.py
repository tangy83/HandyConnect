"""
Notification Service for HandyConnect
Handles notifications for case updates, SLA alerts, and workflow events
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification types"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationStatus(Enum):
    """Notification status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class NotificationTemplate:
    """Notification template definition"""
    id: str
    name: str
    type: NotificationType
    subject_template: str
    body_template: str
    variables: List[str]
    priority: NotificationPriority = NotificationPriority.MEDIUM
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Notification:
    """Notification instance"""
    id: str
    type: NotificationType
    recipient: str
    subject: str
    body: str
    priority: NotificationPriority
    status: NotificationStatus
    template_id: Optional[str] = None
    case_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self):
        self.templates_file = 'data/notification_templates.json'
        self.notifications_file = 'data/notifications.json'
        self._ensure_data_directory()
        self._load_default_templates()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        import os
        os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
    
    def _load_default_templates(self):
        """Load default notification templates"""
        if not self._file_exists(self.templates_file):
            default_templates = [
                # SLA breach notification
                NotificationTemplate(
                    id="sla_breach",
                    name="SLA Breach Alert",
                    type=NotificationType.EMAIL,
                    subject_template="🚨 SLA BREACH: Case {case_number} has exceeded SLA",
                    body_template="""
                    <h2>🚨 SLA Breach Alert</h2>
                    <p>Case <strong>{case_number}</strong> has breached its SLA.</p>
                    
                    <h3>Case Details:</h3>
                    <ul>
                        <li><strong>Case Number:</strong> {case_number}</li>
                        <li><strong>Title:</strong> {case_title}</li>
                        <li><strong>Priority:</strong> {priority}</li>
                        <li><strong>Type:</strong> {case_type}</li>
                        <li><strong>Assigned To:</strong> {assigned_to}</li>
                        <li><strong>Customer:</strong> {customer_name} ({customer_email})</li>
                        <li><strong>Created:</strong> {created_at}</li>
                        <li><strong>SLA Due:</strong> {sla_due_date}</li>
                    </ul>
                    
                    <p><strong>Action Required:</strong> Please review and update this case immediately.</p>
                    
                    <p>View case: <a href="{case_url}">{case_url}</a></p>
                    """,
                    variables=[
                        "case_number", "case_title", "priority", "case_type", 
                        "assigned_to", "customer_name", "customer_email", 
                        "created_at", "sla_due_date", "case_url"
                    ],
                    priority=NotificationPriority.CRITICAL
                ),
                
                # SLA at risk notification
                NotificationTemplate(
                    id="sla_at_risk",
                    name="SLA At Risk Alert",
                    type=NotificationType.EMAIL,
                    subject_template="⚠️ SLA At Risk: Case {case_number} is approaching SLA deadline",
                    body_template="""
                    <h2>⚠️ SLA At Risk Alert</h2>
                    <p>Case <strong>{case_number}</strong> is at risk of breaching its SLA.</p>
                    
                    <h3>Case Details:</h3>
                    <ul>
                        <li><strong>Case Number:</strong> {case_number}</li>
                        <li><strong>Title:</strong> {case_title}</li>
                        <li><strong>Priority:</strong> {priority}</li>
                        <li><strong>Time Remaining:</strong> {time_remaining_hours} hours</li>
                        <li><strong>Assigned To:</strong> {assigned_to}</li>
                    </ul>
                    
                    <p><strong>Action Required:</strong> Please prioritize this case to avoid SLA breach.</p>
                    
                    <p>View case: <a href="{case_url}">{case_url}</a></p>
                    """,
                    variables=[
                        "case_number", "case_title", "priority", "time_remaining_hours",
                        "assigned_to", "case_url"
                    ],
                    priority=NotificationPriority.HIGH
                ),
                
                # Case assignment notification
                NotificationTemplate(
                    id="case_assigned",
                    name="Case Assignment Notification",
                    type=NotificationType.EMAIL,
                    subject_template="📋 New Case Assignment: {case_number}",
                    body_template="""
                    <h2>📋 New Case Assignment</h2>
                    <p>You have been assigned to case <strong>{case_number}</strong>.</p>
                    
                    <h3>Case Details:</h3>
                    <ul>
                        <li><strong>Case Number:</strong> {case_number}</li>
                        <li><strong>Title:</strong> {case_title}</li>
                        <li><strong>Priority:</strong> {priority}</li>
                        <li><strong>Type:</strong> {case_type}</li>
                        <li><strong>Customer:</strong> {customer_name} ({customer_email})</li>
                        <li><strong>Created:</strong> {created_at}</li>
                        <li><strong>SLA Due:</strong> {sla_due_date}</li>
                    </ul>
                    
                    <p>Please review and update the case status as needed.</p>
                    
                    <p>View case: <a href="{case_url}">{case_url}</a></p>
                    """,
                    variables=[
                        "case_number", "case_title", "priority", "case_type",
                        "customer_name", "customer_email", "created_at", 
                        "sla_due_date", "case_url"
                    ],
                    priority=NotificationPriority.MEDIUM
                ),
                
                # Case status change notification
                NotificationTemplate(
                    id="case_status_change",
                    name="Case Status Change Notification",
                    type=NotificationType.EMAIL,
                    subject_template="🔄 Case Status Update: {case_number} - {new_status}",
                    body_template="""
                    <h2>🔄 Case Status Update</h2>
                    <p>Case <strong>{case_number}</strong> status has been updated.</p>
                    
                    <h3>Status Change:</h3>
                    <ul>
                        <li><strong>Previous Status:</strong> {old_status}</li>
                        <li><strong>New Status:</strong> {new_status}</li>
                        <li><strong>Updated By:</strong> {updated_by}</li>
                        <li><strong>Updated At:</strong> {updated_at}</li>
                        <li><strong>Reason:</strong> {reason}</li>
                    </ul>
                    
                    <p>View case: <a href="{case_url}">{case_url}</a></p>
                    """,
                    variables=[
                        "case_number", "old_status", "new_status", "updated_by",
                        "updated_at", "reason", "case_url"
                    ],
                    priority=NotificationPriority.LOW
                ),
                
                # Customer response notification
                NotificationTemplate(
                    id="customer_response",
                    name="Customer Response Notification",
                    type=NotificationType.EMAIL,
                    subject_template="💬 Customer Response: {case_number}",
                    body_template="""
                    <h2>💬 Customer Response Received</h2>
                    <p>Customer has responded to case <strong>{case_number}</strong>.</p>
                    
                    <h3>Response Details:</h3>
                    <ul>
                        <li><strong>Case Number:</strong> {case_number}</li>
                        <li><strong>Customer:</strong> {customer_name} ({customer_email})</li>
                        <li><strong>Response Time:</strong> {response_time}</li>
                        <li><strong>Assigned To:</strong> {assigned_to}</li>
                    </ul>
                    
                    <p>Please review the customer's response and update the case accordingly.</p>
                    
                    <p>View case: <a href="{case_url}">{case_url}</a></p>
                    """,
                    variables=[
                        "case_number", "customer_name", "customer_email",
                        "response_time", "assigned_to", "case_url"
                    ],
                    priority=NotificationPriority.MEDIUM
                )
            ]
            
            self.save_templates(default_templates)
    
    def _file_exists(self, filepath: str) -> bool:
        """Check if file exists"""
        import os
        return os.path.exists(filepath)
    
    def save_templates(self, templates: List[NotificationTemplate]):
        """Save notification templates to file"""
        try:
            templates_dict = []
            for template in templates:
                templates_dict.append({
                    'id': template.id,
                    'name': template.name,
                    'type': template.type.value,
                    'subject_template': template.subject_template,
                    'body_template': template.body_template,
                    'variables': template.variables,
                    'priority': template.priority.value,
                    'enabled': template.enabled,
                    'created_at': template.created_at.isoformat()
                })
            
            with open(self.templates_file, 'w') as f:
                json.dump(templates_dict, f, indent=2)
            
            logger.info(f"Saved {len(templates)} notification templates")
        except Exception as e:
            logger.error(f"Error saving notification templates: {e}")
            raise
    
    def load_templates(self) -> List[NotificationTemplate]:
        """Load notification templates from file"""
        try:
            if not self._file_exists(self.templates_file):
                return []
            
            with open(self.templates_file, 'r') as f:
                templates_dict = json.load(f)
            
            templates = []
            for template_dict in templates_dict:
                templates.append(NotificationTemplate(
                    id=template_dict['id'],
                    name=template_dict['name'],
                    type=NotificationType(template_dict['type']),
                    subject_template=template_dict['subject_template'],
                    body_template=template_dict['body_template'],
                    variables=template_dict['variables'],
                    priority=NotificationPriority(template_dict['priority']),
                    enabled=template_dict.get('enabled', True),
                    created_at=datetime.fromisoformat(template_dict.get('created_at', datetime.utcnow().isoformat()))
                ))
            
            logger.info(f"Loaded {len(templates)} notification templates")
            return templates
        except Exception as e:
            logger.error(f"Error loading notification templates: {e}")
            return []
    
    def save_notifications(self, notifications: List[Notification]):
        """Save notifications to file"""
        try:
            notifications_dict = []
            for notification in notifications:
                notifications_dict.append({
                    'id': notification.id,
                    'type': notification.type.value,
                    'recipient': notification.recipient,
                    'subject': notification.subject,
                    'body': notification.body,
                    'priority': notification.priority.value,
                    'status': notification.status.value,
                    'template_id': notification.template_id,
                    'case_id': notification.case_id,
                    'sent_at': notification.sent_at.isoformat() if notification.sent_at else None,
                    'delivered_at': notification.delivered_at.isoformat() if notification.delivered_at else None,
                    'error_message': notification.error_message,
                    'metadata': notification.metadata,
                    'created_at': notification.created_at.isoformat()
                })
            
            with open(self.notifications_file, 'w') as f:
                json.dump(notifications_dict, f, indent=2)
            
            logger.info(f"Saved {len(notifications)} notifications")
        except Exception as e:
            logger.error(f"Error saving notifications: {e}")
            raise
    
    def load_notifications(self) -> List[Notification]:
        """Load notifications from file"""
        try:
            if not self._file_exists(self.notifications_file):
                return []
            
            with open(self.notifications_file, 'r') as f:
                notifications_dict = json.load(f)
            
            notifications = []
            for notification_dict in notifications_dict:
                notifications.append(Notification(
                    id=notification_dict['id'],
                    type=NotificationType(notification_dict['type']),
                    recipient=notification_dict['recipient'],
                    subject=notification_dict['subject'],
                    body=notification_dict['body'],
                    priority=NotificationPriority(notification_dict['priority']),
                    status=NotificationStatus(notification_dict['status']),
                    template_id=notification_dict.get('template_id'),
                    case_id=notification_dict.get('case_id'),
                    sent_at=datetime.fromisoformat(notification_dict['sent_at']) if notification_dict.get('sent_at') else None,
                    delivered_at=datetime.fromisoformat(notification_dict['delivered_at']) if notification_dict.get('delivered_at') else None,
                    error_message=notification_dict.get('error_message'),
                    metadata=notification_dict.get('metadata', {}),
                    created_at=datetime.fromisoformat(notification_dict.get('created_at', datetime.utcnow().isoformat()))
                ))
            
            logger.info(f"Loaded {len(notifications)} notifications")
            return notifications
        except Exception as e:
            logger.error(f"Error loading notifications: {e}")
            return []
    
    def send_notification(self, template_id: str, recipient: str, variables: Dict[str, Any], 
                         case_id: Optional[str] = None, priority: Optional[NotificationPriority] = None) -> Optional[Notification]:
        """Send a notification using a template"""
        try:
            import uuid
            
            # Load template
            templates = self.load_templates()
            template = next((t for t in templates if t.id == template_id), None)
            
            if not template:
                logger.error(f"Notification template not found: {template_id}")
                return None
            
            if not template.enabled:
                logger.warning(f"Notification template is disabled: {template_id}")
                return None
            
            # Replace variables in template
            subject = self._replace_variables(template.subject_template, variables)
            body = self._replace_variables(template.body_template, variables)
            
            # Create notification
            notification = Notification(
                id=str(uuid.uuid4()),
                type=template.type,
                recipient=recipient,
                subject=subject,
                body=body,
                priority=priority or template.priority,
                status=NotificationStatus.PENDING,
                template_id=template_id,
                case_id=case_id,
                metadata={'variables': variables}
            )
            
            # Send notification based on type
            if template.type == NotificationType.EMAIL:
                success = self._send_email_notification(notification)
            elif template.type == NotificationType.IN_APP:
                success = self._send_in_app_notification(notification)
            elif template.type == NotificationType.WEBHOOK:
                success = self._send_webhook_notification(notification)
            else:
                logger.warning(f"Unsupported notification type: {template.type}")
                success = False
            
            # Update notification status
            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
            else:
                notification.status = NotificationStatus.FAILED
                notification.error_message = "Failed to send notification"
            
            # Save notification
            notifications = self.load_notifications()
            notifications.append(notification)
            self.save_notifications(notifications)
            
            logger.info(f"Notification {notification.id} {'sent' if success else 'failed'} to {recipient}")
            return notification
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return None
    
    def _replace_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Replace variables in template string"""
        try:
            result = template
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                result = result.replace(placeholder, str(value) if value is not None else "")
            return result
        except Exception as e:
            logger.error(f"Error replacing variables in template: {e}")
            return template
    
    def _send_email_notification(self, notification: Notification) -> bool:
        """Send email notification"""
        try:
            # For now, just log the email notification
            # In a real implementation, this would integrate with email service
            logger.info(f"📧 EMAIL NOTIFICATION")
            logger.info(f"   To: {notification.recipient}")
            logger.info(f"   Subject: {notification.subject}")
            logger.info(f"   Priority: {notification.priority.value}")
            logger.info(f"   Case ID: {notification.case_id}")
            logger.info(f"   Body Preview: {notification.body[:200]}...")
            
            # Simulate email sending
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    def _send_in_app_notification(self, notification: Notification) -> bool:
        """Send in-app notification"""
        try:
            # For now, just log the in-app notification
            # In a real implementation, this would integrate with WebSocket or similar
            logger.info(f"🔔 IN-APP NOTIFICATION")
            logger.info(f"   To: {notification.recipient}")
            logger.info(f"   Subject: {notification.subject}")
            logger.info(f"   Priority: {notification.priority.value}")
            logger.info(f"   Case ID: {notification.case_id}")
            
            # Simulate in-app notification
            return True
            
        except Exception as e:
            logger.error(f"Error sending in-app notification: {e}")
            return False
    
    def _send_webhook_notification(self, notification: Notification) -> bool:
        """Send webhook notification"""
        try:
            # For now, just log the webhook notification
            # In a real implementation, this would make HTTP requests to webhook URLs
            logger.info(f"🔗 WEBHOOK NOTIFICATION")
            logger.info(f"   To: {notification.recipient}")
            logger.info(f"   Subject: {notification.subject}")
            logger.info(f"   Priority: {notification.priority.value}")
            logger.info(f"   Case ID: {notification.case_id}")
            
            # Simulate webhook notification
            return True
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
            return False
    
    def notify_sla_breach(self, case: Dict[str, Any], sla_metrics: Dict[str, Any]) -> List[Notification]:
        """Send SLA breach notifications"""
        try:
            notifications = []
            
            # Prepare variables for template
            variables = {
                'case_number': case.get('case_number'),
                'case_title': case.get('case_title'),
                'priority': case.get('priority'),
                'case_type': case.get('case_type'),
                'assigned_to': case.get('assigned_to', 'Unassigned'),
                'customer_name': case.get('customer_info', {}).get('name', 'Unknown'),
                'customer_email': case.get('customer_info', {}).get('email', 'unknown@example.com'),
                'created_at': case.get('created_at'),
                'sla_due_date': sla_metrics.get('resolution_due_date'),
                'case_url': f"http://localhost:5001/cases/{case.get('case_id')}"
            }
            
            # Notify assigned agent
            if case.get('assigned_to'):
                notification = self.send_notification(
                    template_id="sla_breach",
                    recipient=case['assigned_to'],
                    variables=variables,
                    case_id=case['case_id'],
                    priority=NotificationPriority.CRITICAL
                )
                if notification:
                    notifications.append(notification)
            
            # Notify supervisor/manager
            supervisor_email = "supervisor@company.com"  # This would come from config
            notification = self.send_notification(
                template_id="sla_breach",
                recipient=supervisor_email,
                variables=variables,
                case_id=case['case_id'],
                priority=NotificationPriority.CRITICAL
            )
            if notification:
                notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error sending SLA breach notifications: {e}")
            return []
    
    def notify_sla_at_risk(self, case: Dict[str, Any], sla_metrics: Dict[str, Any]) -> List[Notification]:
        """Send SLA at risk notifications"""
        try:
            notifications = []
            
            # Prepare variables for template
            variables = {
                'case_number': case.get('case_number'),
                'case_title': case.get('case_title'),
                'priority': case.get('priority'),
                'time_remaining_hours': round(sla_metrics.get('resolution_time_remaining_hours', 0), 1),
                'assigned_to': case.get('assigned_to', 'Unassigned'),
                'case_url': f"http://localhost:5001/cases/{case.get('case_id')}"
            }
            
            # Notify assigned agent
            if case.get('assigned_to'):
                notification = self.send_notification(
                    template_id="sla_at_risk",
                    recipient=case['assigned_to'],
                    variables=variables,
                    case_id=case['case_id'],
                    priority=NotificationPriority.HIGH
                )
                if notification:
                    notifications.append(notification)
                    # Mark case as notified at risk
                    case['notified_at_risk'] = True
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error sending SLA at risk notifications: {e}")
            return []
    
    def notify_case_assignment(self, case: Dict[str, Any], assigned_to: str) -> Optional[Notification]:
        """Send case assignment notification"""
        try:
            # Prepare variables for template
            variables = {
                'case_number': case.get('case_number'),
                'case_title': case.get('case_title'),
                'priority': case.get('priority'),
                'case_type': case.get('case_type'),
                'customer_name': case.get('customer_info', {}).get('name', 'Unknown'),
                'customer_email': case.get('customer_info', {}).get('email', 'unknown@example.com'),
                'created_at': case.get('created_at'),
                'sla_due_date': case.get('sla_metrics', {}).get('resolution_due_date'),
                'case_url': f"http://localhost:5001/cases/{case.get('case_id')}"
            }
            
            # Send notification to assigned agent
            notification = self.send_notification(
                template_id="case_assigned",
                recipient=assigned_to,
                variables=variables,
                case_id=case['case_id'],
                priority=NotificationPriority.MEDIUM
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending case assignment notification: {e}")
            return None
    
    def notify_status_change(self, case: Dict[str, Any], old_status: str, new_status: str, 
                           updated_by: str, reason: str = "Status updated") -> Optional[Notification]:
        """Send case status change notification"""
        try:
            # Prepare variables for template
            variables = {
                'case_number': case.get('case_number'),
                'old_status': old_status,
                'new_status': new_status,
                'updated_by': updated_by,
                'updated_at': datetime.utcnow().isoformat(),
                'reason': reason,
                'case_url': f"http://localhost:5001/cases/{case.get('case_id')}"
            }
            
            # Send notification to assigned agent
            if case.get('assigned_to'):
                notification = self.send_notification(
                    template_id="case_status_change",
                    recipient=case['assigned_to'],
                    variables=variables,
                    case_id=case['case_id'],
                    priority=NotificationPriority.LOW
                )
                return notification
            
            return None
            
        except Exception as e:
            logger.error(f"Error sending status change notification: {e}")
            return None
    
    def get_notification_statistics(self) -> Dict[str, Any]:
        """Get notification statistics"""
        try:
            notifications = self.load_notifications()
            
            total_notifications = len(notifications)
            sent_notifications = len([n for n in notifications if n.status == NotificationStatus.SENT])
            failed_notifications = len([n for n in notifications if n.status == NotificationStatus.FAILED])
            pending_notifications = len([n for n in notifications if n.status == NotificationStatus.PENDING])
            
            # Group by type
            type_stats = {}
            for notification in notifications:
                notification_type = notification.type.value
                if notification_type not in type_stats:
                    type_stats[notification_type] = {
                        'total': 0,
                        'sent': 0,
                        'failed': 0,
                        'pending': 0
                    }
                
                type_stats[notification_type]['total'] += 1
                if notification.status == NotificationStatus.SENT:
                    type_stats[notification_type]['sent'] += 1
                elif notification.status == NotificationStatus.FAILED:
                    type_stats[notification_type]['failed'] += 1
                elif notification.status == NotificationStatus.PENDING:
                    type_stats[notification_type]['pending'] += 1
            
            # Group by priority
            priority_stats = {}
            for notification in notifications:
                priority = notification.priority.value
                if priority not in priority_stats:
                    priority_stats[priority] = 0
                priority_stats[priority] += 1
            
            return {
                'total_notifications': total_notifications,
                'sent_notifications': sent_notifications,
                'failed_notifications': failed_notifications,
                'pending_notifications': pending_notifications,
                'success_rate': round((sent_notifications / total_notifications * 100) if total_notifications > 0 else 0, 2),
                'type_statistics': type_stats,
                'priority_statistics': priority_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting notification statistics: {e}")
            return {}
