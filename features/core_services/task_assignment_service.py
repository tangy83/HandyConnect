"""
Task Assignment Service
Handles assignment of tasks to internal team or external contractors
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from .email_service import EmailService
from .case_service import CaseService
from .task_service import TaskService

logger = logging.getLogger(__name__)


class TaskAssignmentService:
    """Service for assigning tasks and notifying assignees"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.case_service = CaseService()
        self.task_service = TaskService()
    
    def assign_and_notify(self, task_id: int, assignee_name: str, 
                         assignee_email: str, assignee_role: str,
                         case_id: str) -> bool:
        """
        Assign task and send notification email
        
        Args:
            task_id: Task ID
            assignee_name: Full name of assignee
            assignee_email: Email address
            assignee_role: "Internal" or "External"
            case_id: Case UUID
        
        Returns:
            bool: True if assignment and notification successful
        """
        try:
            # Assign the task
            task = self.task_service.assign_task(
                task_id, assignee_name, assignee_email, assignee_role
            )
            
            if not task:
                logger.error(f"Failed to assign task {task_id}")
                return False
            
            # Get case details
            case = self.case_service.get_case_by_id(case_id)
            if not case:
                logger.error(f"Case not found: {case_id}")
                return False
            
            # Build assignment email
            subject, body = self._build_assignment_email(task, case)
            
            # Send email to assignee
            email_sent = self.email_service.send_email_response(
                case_id=case_id,
                response_text=body,
                recipient_email=assignee_email,
                subject=subject,
                include_case_details=False
            )
            
            if email_sent:
                # Log email to case threads
                thread_data = {
                    'direction': 'Outbound',
                    'sender_name': 'HandyConnect System',
                    'sender_email': 'handymyjob@outlook.com',
                    'subject': subject,
                    'body': body,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                self.case_service.add_thread_to_case(case_id, thread_data)
                
                logger.info(f"✉️ Task assignment notification sent to {assignee_name}")
                return True
            else:
                logger.error(f"Failed to send assignment email to {assignee_email}")
                return False
                
        except Exception as e:
            logger.error(f"Error in assign_and_notify: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _build_assignment_email(self, task: Dict, case: Dict) -> tuple:
        """Build assignment email subject and body"""
        
        customer_info = case.get('customer_info', {})
        property_number = customer_info.get('property_number', 'N/A')
        block_number = customer_info.get('block_number', 'N/A')
        property_ref = f"Property {property_number}, Block {block_number}" if property_number != 'N/A' else "the property"
        
        priority_emoji = {
            'Urgent': '🔴',
            'High': '🟠',
            'Medium': '🟡',
            'Low': '🟢'
        }.get(case.get('priority', 'Medium'), '🟡')
        
        subject = f"Task Assignment - Case #{case.get('case_number')} - {task.get('subject', 'New Task')}"
        
        body = f"""
Dear {task.get('assigned_to', 'Team Member')},

You have been assigned a new task by HandyConnect Property Management.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 TASK ASSIGNMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{priority_emoji} Priority: {case.get('priority', 'Medium')}
📝 Task: {task.get('subject', 'Task Assignment')}

Description:
{task.get('description', task.get('content', 'No description provided'))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏠 PROPERTY DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Case Number: {case.get('case_number', 'N/A')}
{property_ref}
Property Address: {customer_info.get('property_address', 'N/A')}

Customer: {customer_info.get('name', 'N/A')}
Contact: {customer_info.get('email', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Review the task details above
2. Contact the customer if needed
3. Complete the assigned work
4. Reply to this email when task is completed

If you have questions, reply to this email or contact our support team.

Thank you,
HandyConnect Property Management Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Case ID: {case_id} | Task ID: {task.get('id')}
This is an automated notification from HandyConnect.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return subject, body

