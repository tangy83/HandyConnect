"""
Case Service for HandyConnect
Core business logic for case management
"""

import json
import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from ..models.case_models import (
    Case, CaseStatus, CaseType, CasePriority, CustomerInfo, 
    CaseMetadata, TimelineEvent, SLAPriority
)
from .email_notification_service import EmailNotificationService

logger = logging.getLogger(__name__)


class CaseService:
    """Service for managing cases"""
    
    def __init__(self):
        self.data_file = 'data/cases.json'
        self.counter_file = 'data/case_counter.json'
        self._ensure_data_directory()
        
        # Initialize advanced services
        try:
            from .sla_service import SLAService
            from .workflow_service import WorkflowService, WorkflowTrigger
            from .notification_service import NotificationService
            from .cache_service import get_case_cache, invalidate_case_cache
            from .performance_monitor import get_performance_monitor, performance_timer
            
            self.sla_service = SLAService()
            self.workflow_service = WorkflowService()
            self.notification_service = NotificationService()
            self.email_notification_service = EmailNotificationService()
            self.cache = get_case_cache()
            self.performance_monitor = get_performance_monitor()
            logger.info("Advanced case services initialized successfully")
        except Exception as e:
            logger.warning(f"Advanced services not available: {e}")
            self.sla_service = None
            self.workflow_service = None
            self.notification_service = None
            self.email_notification_service = None
            self.cache = None
            self.performance_monitor = None
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def _get_next_case_number(self) -> str:
        """Generate next case number in format YYMMDDNNNN"""
        try:
            # Get today's date in YYMMDD format
            today = datetime.now().strftime('%y%m%d')  # e.g., '251006' for Oct 6, 2025
            
            # Load counter data
            if os.path.exists(self.counter_file):
                with open(self.counter_file, 'r') as f:
                    counter_data = json.load(f)
            else:
                counter_data = {
                    'current_date': today,
                    'counter': 0,
                    'daily_counters': {}
                }
            
            # Reset counter if it's a new day
            if counter_data.get('current_date') != today:
                logger.info(f"New day detected. Resetting counter. Previous date: {counter_data.get('current_date')}, New date: {today}")
                counter_data['current_date'] = today
                counter_data['counter'] = 0
            
            # Increment counter for today
            counter_data['counter'] += 1
            
            # Validate counter doesn't exceed daily limit
            if counter_data['counter'] > 9999:
                logger.error(f"Daily case limit exceeded (9999) for date {today}")
                raise ValueError(f"Daily case limit exceeded for {today}")
            
            # Track daily counters for history
            if 'daily_counters' not in counter_data:
                counter_data['daily_counters'] = {}
            counter_data['daily_counters'][today] = counter_data['counter']
            
            # Save updated counter
            with open(self.counter_file, 'w') as f:
                json.dump(counter_data, f, indent=2)
            
            # Format: YYMMDDNNNN (10 digits)
            # Example: 2510060005 = Oct 6, 2025, 5th case
            case_number = f"{today}{counter_data['counter']:04d}"
            
            logger.info(f"Generated case number: {case_number} (Date: {today}, Serial: {counter_data['counter']})")
            return case_number
            
        except Exception as e:
            logger.error(f"Error generating case number: {e}")
            # Fallback to date-based ID with timestamp
            today = datetime.now().strftime('%y%m%d')
            timestamp = int(datetime.now().timestamp())
            fallback_number = f"{today}{timestamp % 10000:04d}"
            logger.warning(f"Using fallback case number: {fallback_number}")
            return fallback_number
    
    def load_cases(self) -> List[Dict]:
        """Load cases from JSON file with caching and performance monitoring"""
        import time
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = "all_cases"
            if self.cache:
                cached_cases = self.cache.get(cache_key)
                if cached_cases is not None:
                    duration_ms = (time.time() - start_time) * 1000
                    if self.performance_monitor:
                        self.performance_monitor.record_metric(
                            "case_service", "load_cases", duration_ms, 
                            success=True, metadata={'source': 'cache'}
                        )
                    logger.debug(f"Loaded {len(cached_cases)} cases from cache")
                    return cached_cases
            
            # Load from file
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    cases_data = json.load(f)
                    logger.info(f"Loaded {len(cases_data)} cases from {self.data_file}")
                    
                    # Cache the results
                    if self.cache:
                        self.cache.set(cache_key, cases_data, ttl=300)  # 5 minutes
                    
                    # Record performance metric
                    duration_ms = (time.time() - start_time) * 1000
                    if self.performance_monitor:
                        self.performance_monitor.record_metric(
                            "case_service", "load_cases", duration_ms, 
                            success=True, metadata={'source': 'file', 'count': len(cases_data)}
                        )
                    
                    return cases_data
            logger.info("No cases file found, returning empty list")
            return []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            duration_ms = (time.time() - start_time) * 1000
            if self.performance_monitor:
                self.performance_monitor.record_metric(
                    "case_service", "load_cases", duration_ms, 
                    success=False, metadata={'error': str(e)}
                )
            logger.error(f"Error loading cases: {e}")
            return []
    
    def save_cases(self, cases: List[Dict]):
        """Save cases to JSON file and update cache"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(cases, f, indent=2, default=str)
            logger.info(f"Saved {len(cases)} cases to {self.data_file}")
            
            # Update cache
            if self.cache:
                self.cache.set("all_cases", cases, ttl=300)  # 5 minutes
                
        except Exception as e:
            logger.error(f"Error saving cases: {e}")
            raise
    
    def get_next_case_number(self) -> str:
        """Generate next case number"""
        cases = self.load_cases()
        
        # Find highest case number
        sequence_numbers = []
        for case in cases:
            try:
                case_number = case.get('case_number', '')
                if case_number.startswith('C-'):
                    seq = int(case_number.split('-')[-1])
                    sequence_numbers.append(seq)
            except (ValueError, IndexError):
                continue
        
        next_seq = max(sequence_numbers) + 1 if sequence_numbers else 1
        return f"C-{next_seq:04d}"
    
    def create_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new case"""
        try:
            cases = self.load_cases()
            
            # Generate case ID and number
            case_id = str(uuid.uuid4())
            case_number = self._get_next_case_number()
            
            # Create new case
            new_case = {
                'case_id': case_id,
                'case_number': case_number,
                'case_title': case_data.get('case_title', 'New Case'),
                'case_type': case_data.get('case_type', 'General'),
                'status': 'New',
                'priority': case_data.get('priority', 'Medium'),
                'sentiment': case_data.get('sentiment', 'Neutral'),
                'sla_due_date': self._calculate_sla_due_date(case_data.get('priority', 'Medium')),
                'sla_status': 'On Time',
                'assigned_to': None,
                'assigned_team': 'support',
                'customer_info': case_data.get('customer_info', {
                    'name': 'Unknown',
                    'email': 'unknown@example.com',
                    'property_number': case_data.get('property_number'),
                    'block_number': case_data.get('block_number'),
                    'property_address': case_data.get('property_address')
                }),
                'case_metadata': {
                    'description': case_data.get('description', ''),
                    'tags': case_data.get('tags', []),
                    'last_activity_date': datetime.utcnow().isoformat()
                },
                'threads': case_data.get('threads', []),
                'tasks': case_data.get('tasks', []),
                'timeline': [],
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'created_by': case_data.get('created_by', 'system'),
                'updated_by': case_data.get('updated_by', 'system')
            }
            
            # Add initial timeline event
            new_case['timeline'].append({
                'event_id': str(uuid.uuid4()),
                'event_type': 'case_created',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': new_case['created_by'],
                'description': 'Case created',
                'metadata': {'case_type': new_case['case_type'], 'priority': new_case['priority']}
            })
            
            # Update with advanced features
            new_case = self.update_case_with_advanced_features(new_case)
            
            # Add to cases list
            cases.append(new_case)
            self.save_cases(cases)
            
            logger.info(f"Created new case: {case_number}")
            return new_case
            
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            raise
    
    def create_case_from_email(self, email: Dict, thread_id: str, llm_result: Dict) -> Dict:
        """Create a new case from email processing"""
        try:
            case_id = str(uuid.uuid4())
            case_number = self._get_next_case_number()
            
            # Determine case type from LLM analysis
            case_type = self._determine_case_type(llm_result)
            
            # Create customer info
            customer_info = {
                'name': email.get('sender', {}).get('name', 'Unknown'),
                'email': email.get('sender', {}).get('email', 'unknown@example.com'),
                'customer_type': 'tenant',
                'property_number': llm_result.get('property_number'),
                'block_number': llm_result.get('block_number'),
                'property_address': llm_result.get('property_address')
            }
            
            # Create case metadata
            case_metadata = {
                'source': 'email',
                'channel': 'outlook',
                'first_contact_date': datetime.utcnow().isoformat(),
                'last_activity_date': datetime.utcnow().isoformat(),
                'escalation_count': 0,
                'tags': [llm_result.get('category', 'General')]
            }
            
            # Create timeline event
            timeline_event = {
                'event_id': str(uuid.uuid4()),
                'event_type': 'case_created',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': 'system',
                'description': f"Case created from email: {email.get('subject', 'No subject')}",
                'metadata': {}
            }
            
            # Create initial thread entry for the inbound email
            initial_thread = {
                'thread_id': str(uuid.uuid4()),
                'timestamp': email.get('received_time', datetime.utcnow().isoformat()),
                'direction': 'Inbound',
                'sender_name': email.get('sender', {}).get('name', 'Unknown'),
                'sender_email': email.get('sender', {}).get('email', ''),
                'subject': email.get('subject', 'No subject'),
                'body': email.get('body', ''),
                'message_id': email.get('id', '')
            }
            
            # Create case
            case = {
                'case_id': case_id,
                'case_number': case_number,
                'case_title': email.get('subject', 'Untitled Case'),
                'case_type': case_type,
                'status': 'New',
                'priority': llm_result.get('priority', 'Medium'),
                'sentiment': llm_result.get('sentiment', 'Neutral'),
                'sla_due_date': self._calculate_sla_due_date(llm_result.get('priority', 'Medium')),
                'sla_status': 'On Time',
                'assigned_to': None,
                'assigned_team': 'support',
                'customer_info': customer_info,
                'case_metadata': case_metadata,
                'threads': [initial_thread],  # Store thread objects, not IDs
                'tasks': [],
                'timeline': [timeline_event],
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'created_by': 'system'
            }
            
            # Save case
            cases = self.load_cases()
            cases.append(case)
            self.save_cases(cases)
            
            # Send automated acknowledgment email to customer
            customer_email = customer_info.get('email')
            if customer_email:
                try:
                    from .acknowledgment_service import AcknowledgmentService
                    acknowledgment_service = AcknowledgmentService()
                    
                    success = acknowledgment_service.send_acknowledgment(
                        case_id=case_id,
                        customer_email=customer_email,
                        original_email=email,
                        case_data=case
                    )
                    
                    if success:
                        logger.info(f"✉️ Acknowledgment email sent to {customer_email} for case {case_number}")
                    else:
                        logger.warning(f"⚠️ Failed to send acknowledgment email to {customer_email}")
                        # Optionally retry in background
                        # acknowledgment_service.retry_failed_acknowledgment(case_id)
                except Exception as e:
                    logger.error(f"Error sending acknowledgment email: {e}")
            
            logger.info(f"Created new case {case_number} for email {email.get('id', 'unknown')}")
            return case
            
        except Exception as e:
            logger.error(f"Error creating case from email: {e}")
            raise
    
    def find_case_by_thread(self, thread_id: str) -> Optional[Dict]:
        """Find existing case by thread ID"""
        cases = self.load_cases()
        for case in cases:
            if thread_id in case.get('threads', []):
                return case
        return None
    
    def find_case_by_customer_email(self, email: str) -> Optional[Dict]:
        """Find open case by customer email"""
        cases = self.load_cases()
        open_statuses = ['New', 'In Progress', 'Awaiting Customer', 'Awaiting Vendor']
        
        for case in cases:
            if (case.get('customer_info', {}).get('email') == email and 
                case.get('status') in open_statuses):
                return case
        return None
    
    def get_case_by_id(self, case_id: str) -> Optional[Dict]:
        """Get case by ID"""
        cases = self.load_cases()
        return next((c for c in cases if c.get('case_id') == case_id), None)
    
    def get_case_by_number(self, case_number: str) -> Optional[Dict]:
        """Get case by case number"""
        cases = self.load_cases()
        return next((c for c in cases if c.get('case_number') == case_number), None)
    
    def generate_case_summary(self, case: Dict) -> str:
        """Generate AI-powered case summary with actionable points"""
        try:
            from .llm_service import LLMService
            llm_service = LLMService()
            
            # Get related tasks for progress tracking
            related_tasks = self.get_related_tasks(case.get('case_id', ''))
            completed_tasks = len([task for task in related_tasks if task.get('status') in ['Completed', 'Resolved']])
            total_tasks = len(related_tasks)
            
            # Get email content from related tasks to extract actionable points
            email_contents = []
            for task in related_tasks[:3]:  # Get first 3 tasks for context
                if task.get('content'):
                    email_contents.append(task.get('content', '')[:500])  # Limit to 500 chars per email
            
            emails_text = "\n\nCustomer Email Content:\n" + "\n---\n".join(email_contents) if email_contents else ""
            
            # Build context for summary
            customer_info = case.get('customer_info', {})
            case_metadata = case.get('case_metadata', {})
            description = case_metadata.get('description', case.get('case_description', 'N/A'))
            
            context = f"""
            Case Details:
            - Title: {case.get('case_title', 'N/A')}
            - Type: {case.get('case_type', 'N/A')}
            - Priority: {case.get('priority', 'N/A')}
            - Status: {case.get('status', 'N/A')}
            - Customer: {customer_info.get('name', 'N/A')}
            - Property Number: {customer_info.get('property_number', 'N/A')}
            - Block Number: {customer_info.get('block_number', 'N/A')}
            - Description: {description}
            - Created: {case.get('created_at', 'N/A')}
            - Completed Tasks: {completed_tasks}
            - Total Tasks: {total_tasks}
            - Progress: {completed_tasks}/{total_tasks} tasks completed
            {emails_text}
            """
            
            # Generate summary
            summary = llm_service.generate_case_summary(context)
            return summary
            
        except Exception as e:
            logger.error(f"Error generating case summary: {e}")
            return "Summary generation unavailable"
    
    def regenerate_summary_for_case(self, case_id: str) -> bool:
        """
        Regenerate AI summary for a case and save it to the case data
        Called when new emails arrive or case is updated
        """
        try:
            cases = self.load_cases()
            case = next((c for c in cases if c['case_id'] == case_id), None)
            
            if not case:
                logger.error(f"Case not found for summary regeneration: {case_id}")
                return False
            
            # Generate new summary
            summary = self.generate_case_summary(case)
            
            # Create preview (first 150 chars)
            summary_preview = summary[:150] + '...' if len(summary) > 150 else summary
            
            # Update case with summary and metadata
            case['ai_summary'] = summary
            case['ai_summary_preview'] = summary_preview
            case['ai_summary_generated_at'] = datetime.utcnow().isoformat()
            case['updated_at'] = datetime.utcnow().isoformat()
            
            # Save updated cases
            self.save_cases(cases)
            
            logger.info(f"✅ Regenerated AI summary for case {case.get('case_number', case_id)}")
            return True
            
        except Exception as e:
            logger.error(f"Error regenerating summary for case {case_id}: {e}")
            return False
    
    def get_related_tasks(self, case_id: str) -> List[Dict]:
        """Get tasks related to a case"""
        try:
            from .task_service import TaskService
            task_service = TaskService()
            
            # Load all tasks
            tasks = task_service.load_tasks()
            
            # Filter tasks related to this case
            related_tasks = []
            for task in tasks:
                if task.get('case_id') == case_id:
                    related_tasks.append(task)
            
            return related_tasks
            
        except Exception as e:
            logger.error(f"Error getting related tasks for case {case_id}: {e}")
            return []
    
    def update_case(self, case_id: str, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Update case with general data"""
        try:
            cases = self.load_cases()
            case = next((c for c in cases if c.get('case_id') == case_id), None)
            
            if not case:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if key not in ['case_id', 'created_at']:  # Don't allow updating these
                    case[key] = value
            
            case['updated_at'] = datetime.utcnow().isoformat()
            case['updated_by'] = update_data.get('updated_by', 'api')
            
            # Add timeline event for general updates
            if 'timeline' not in case:
                case['timeline'] = []
            
            timeline_event = {
                'event_id': str(uuid.uuid4()),
                'event_type': 'case_updated',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': update_data.get('updated_by', 'api'),
                'description': f"Case updated: {', '.join(update_data.keys())}",
                'metadata': {
                    'updated_fields': list(update_data.keys())
                }
            }
            case['timeline'].append(timeline_event)
            
            # Save changes
            self.save_cases(cases)
            
            logger.info(f"Updated case {case_id}: {list(update_data.keys())}")
            return case
            
        except Exception as e:
            logger.error(f"Error updating case {case_id}: {e}")
            return None

    def update_case_status(self, case_id: str, status: str, actor: str = "system") -> Optional[Dict]:
        """Update case status"""
        cases = self.load_cases()
        case = next((c for c in cases if c.get('case_id') == case_id), None)
        
        if case:
            old_status = case.get('status')
            case['status'] = status
            case['updated_at'] = datetime.utcnow().isoformat()
            case['updated_by'] = actor
            
            # Add timeline event
            timeline_event = {
                'event_id': str(uuid.uuid4()),
                'event_type': 'status_changed',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': actor,
                'description': f"Status changed from {old_status} to {status}",
                'metadata': {'old_status': old_status, 'new_status': status}
            }
            
            case['timeline'].append(timeline_event)
            case['case_metadata']['last_activity_date'] = datetime.utcnow().isoformat()
            
            self.save_cases(cases)
            logger.info(f"Updated case {case.get('case_number')} status to {status}")
            return case
        
        return None
    
    def assign_case(self, case_id: str, assignee: str, actor: str = "system") -> Optional[Dict]:
        """Assign case to agent"""
        cases = self.load_cases()
        case = next((c for c in cases if c.get('case_id') == case_id), None)
        
        if case:
            old_assignee = case.get('assigned_to')
            case['assigned_to'] = assignee
            case['updated_at'] = datetime.utcnow().isoformat()
            case['updated_by'] = actor
            
            # Add timeline event
            timeline_event = {
                'event_id': str(uuid.uuid4()),
                'event_type': 'assigned',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': actor,
                'description': f"Case assigned to {assignee}",
                'metadata': {'old_assignee': old_assignee, 'new_assignee': assignee}
            }
            
            case['timeline'].append(timeline_event)
            case['case_metadata']['last_activity_date'] = datetime.utcnow().isoformat()
            
            self.save_cases(cases)
            logger.info(f"Assigned case {case.get('case_number')} to {assignee}")
            return case
        
        return None
    
    def add_task_to_case(self, case_id: str, task_id: int) -> Optional[Dict]:
        """Add task to case"""
        cases = self.load_cases()
        case = next((c for c in cases if c.get('case_id') == case_id), None)
        
        if case:
            if task_id not in case.get('tasks', []):
                case['tasks'].append(task_id)
                case['updated_at'] = datetime.utcnow().isoformat()
                
                # Add timeline event
                timeline_event = {
                    'event_id': str(uuid.uuid4()),
                    'event_type': 'task_added',
                    'timestamp': datetime.utcnow().isoformat(),
                    'actor': 'system',
                    'description': f"Task {task_id} added to case",
                    'metadata': {'task_id': task_id}
                }
                
                case['timeline'].append(timeline_event)
                case['case_metadata']['last_activity_date'] = datetime.utcnow().isoformat()
                
                self.save_cases(cases)
                logger.info(f"Added task {task_id} to case {case.get('case_number')}")
                return case
        
        return None
    
    def add_thread_to_case(self, case_id: str, thread_id: str) -> Optional[Dict]:
        """Add thread to case"""
        cases = self.load_cases()
        case = next((c for c in cases if c.get('case_id') == case_id), None)
        
        if case:
            if thread_id not in case.get('threads', []):
                case['threads'].append(thread_id)
                case['updated_at'] = datetime.utcnow().isoformat()
                
                # Add timeline event
                timeline_event = {
                    'event_id': str(uuid.uuid4()),
                    'event_type': 'thread_added',
                    'timestamp': datetime.utcnow().isoformat(),
                    'actor': 'system',
                    'description': f"Thread {thread_id} added to case",
                    'metadata': {'thread_id': thread_id}
                }
                
                case['timeline'].append(timeline_event)
                case['case_metadata']['last_activity_date'] = datetime.utcnow().isoformat()
                
                self.save_cases(cases)
                logger.info(f"Added thread {thread_id} to case {case.get('case_number')}")
                return case
        
        return None
    
    def get_case_stats(self) -> Dict[str, Any]:
        """Get case statistics for dashboard with caching"""
        try:
            # Check cache first
            cache_key = "case_stats"
            if self.cache:
                cached_stats = self.cache.get(cache_key)
                if cached_stats is not None:
                    logger.debug("Retrieved case statistics from cache")
                    return cached_stats
            
            cases = self.load_cases()
            
            total_cases = len(cases)
            new_cases = len([c for c in cases if c.get('status') == 'New'])
            in_progress_cases = len([c for c in cases if c.get('status') == 'In Progress'])
            resolved_cases = len([c for c in cases if c.get('status') == 'Resolved'])
            closed_cases = len([c for c in cases if c.get('status') == 'Closed'])
            
            # Priority breakdown
            high_priority = len([c for c in cases if c.get('priority') == 'High'])
            urgent_priority = len([c for c in cases if c.get('priority') == 'Urgent'])
            critical_priority = len([c for c in cases if c.get('priority') == 'Critical'])
            
            # Type breakdown
            case_types = {}
            for case in cases:
                case_type = case.get('case_type', 'General')
                case_types[case_type] = case_types.get(case_type, 0) + 1
            
            # SLA status
            on_time_cases = len([c for c in cases if c.get('sla_status') == 'On Time'])
            at_risk_cases = len([c for c in cases if c.get('sla_status') == 'At Risk'])
            breached_cases = len([c for c in cases if c.get('sla_status') == 'Breached'])
            
            stats = {
                'total_cases': total_cases,
                'new': new_cases,
                'in_progress': in_progress_cases,
                'resolved': resolved_cases,
                'closed': closed_cases,
                'high_priority': high_priority,
                'urgent_priority': urgent_priority,
                'critical_priority': critical_priority,
                'case_types': case_types,
                'sla_status': {
                    'on_time': on_time_cases,
                    'at_risk': at_risk_cases,
                    'breached': breached_cases
                }
            }
            
            # Cache the results
            if self.cache:
                self.cache.set(cache_key, stats, ttl=60)  # 1 minute
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting case statistics: {e}")
            return {}
    
    def get_cases_by_filter(self, status: str = None, priority: str = None, 
                          case_type: str = None, assigned_to: str = None) -> List[Dict]:
        """Get cases with filters"""
        cases = self.load_cases()
        filtered_cases = []
        
        for case in cases:
            if status and case.get('status') != status:
                continue
            if priority and case.get('priority') != priority:
                continue
            if case_type and case.get('case_type') != case_type:
                continue
            if assigned_to and case.get('assigned_to') != assigned_to:
                continue
            filtered_cases.append(case)
        
        # Sort by created_at descending
        filtered_cases.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return filtered_cases
    
    def _determine_case_type(self, llm_result: Dict) -> str:
        """Determine case type from LLM analysis"""
        category = llm_result.get('category', '').lower()
        summary = llm_result.get('summary', '').lower()
        
        # Map categories to case types
        if any(word in category for word in ['complaint', 'issue', 'problem', 'fault']):
            return 'Complaint'
        elif any(word in category for word in ['request', 'need', 'require', 'want']):
            return 'Request'
        elif any(word in category for word in ['question', 'inquiry', 'ask', 'wonder']):
            return 'Query'
        elif any(word in category for word in ['feedback', 'comment', 'suggestion']):
            return 'Feedback'
        elif any(word in summary for word in ['maintenance', 'repair', 'fix']):
            return 'Maintenance'
        elif any(word in summary for word in ['billing', 'payment', 'invoice', 'charge']):
            return 'Billing'
        elif any(word in summary for word in ['security', 'break', 'unauthorized', 'access']):
            return 'Security'
        else:
            return 'General'
    
    def _calculate_sla_due_date(self, priority: str) -> str:
        """Calculate SLA due date based on priority"""
        try:
            sla_hours = SLAPriority[priority.upper()].value
        except KeyError:
            sla_hours = SLAPriority.MEDIUM.value
        
        due_date = datetime.utcnow() + timedelta(hours=sla_hours)
        return due_date.isoformat()
    
    def check_sla_status(self, case: Dict) -> str:
        """Check SLA status for a case"""
        # Use advanced SLA service if available
        if self.sla_service:
            case_with_sla = self.sla_service.update_case_sla_status(case)
            return case_with_sla.get('sla_status', 'N/A')
        
        # Fallback to basic SLA check
        sla_due_date = case.get('sla_due_date')
        if not sla_due_date:
            return 'N/A'
        
        try:
            due_date = datetime.fromisoformat(sla_due_date)
            now = datetime.utcnow()
            
            if now > due_date:
                return 'Breached'
            elif (due_date - now).total_seconds() < 3600:  # Less than 1 hour
                return 'At Risk'
            else:
                return 'On Time'
        except (ValueError, TypeError):
            return 'N/A'
    
    def update_case_with_advanced_features(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Update case with advanced features (SLA, workflow, notifications)"""
        try:
            updated_case = case.copy()
            
            # Update SLA status
            if self.sla_service:
                sla_metrics = self.sla_service.calculate_sla_metrics(updated_case)
                if sla_metrics:
                    updated_case = self.sla_service.update_case_sla_status(updated_case)
                    
                    # Check for SLA breaches and send notifications
                    if sla_metrics.resolution_status.value == 'Breached' and not updated_case.get('escalated', False):
                        if self.notification_service:
                            self.notification_service.notify_sla_breach(updated_case, {
                                'resolution_due_date': sla_metrics.resolution_due_date.isoformat()
                            })
                    
                    # Check for SLA at risk and send notifications
                    elif sla_metrics.resolution_status.value == 'At Risk' and not updated_case.get('notified_at_risk', False):
                        if self.notification_service:
                            self.notification_service.notify_sla_at_risk(updated_case, {
                                'resolution_time_remaining_hours': sla_metrics.resolution_time_remaining_hours
                            })
            
            # Execute workflows
            if self.workflow_service:
                from .workflow_service import WorkflowTrigger
                
                # Execute workflows based on current case state
                sla_status = updated_case.get('sla_status', 'N/A')
                
                if sla_status == 'Breached':
                    self.workflow_service.execute_workflow(
                        updated_case, WorkflowTrigger.SLA_BREACHED, sla_status
                    )
                elif sla_status == 'At Risk':
                    self.workflow_service.execute_workflow(
                        updated_case, WorkflowTrigger.SLA_AT_RISK, sla_status
                    )
            
            return updated_case
            
        except Exception as e:
            logger.error(f"Error updating case with advanced features: {e}")
            return case
    
    def assign_case(self, case_id: str, assigned_to: str, actor: str = "system") -> Optional[Dict[str, Any]]:
        """Assign case to an agent with notifications"""
        try:
            cases = self.load_cases()
            case = next((c for c in cases if c['case_id'] == case_id), None)
            
            if not case:
                return None
            
            old_assigned_to = case.get('assigned_to')
            case['assigned_to'] = assigned_to
            case['updated_at'] = datetime.utcnow().isoformat()
            
            # Add timeline event
            if 'timeline' not in case:
                case['timeline'] = []
            
            case['timeline'].append({
                'event_id': f"assignment_{datetime.utcnow().timestamp()}",
                'event_type': 'assigned',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': actor,
                'description': f"Case assigned to {assigned_to}",
                'metadata': {
                    'old_assigned_to': old_assigned_to,
                    'new_assigned_to': assigned_to
                }
            })
            
            # Send assignment notification
            if self.notification_service:
                self.notification_service.notify_case_assignment(case, assigned_to)
            
            # Execute assignment workflow
            if self.workflow_service:
                from .workflow_service import WorkflowTrigger
                self.workflow_service.execute_workflow(case, WorkflowTrigger.STATUS_CHANGED)
            
            # Update case with advanced features
            case = self.update_case_with_advanced_features(case)
            
            # Save updated case
            self.save_cases(cases)
            
            logger.info(f"Case {case['case_number']} assigned to {assigned_to}")
            return case
            
        except Exception as e:
            logger.error(f"Error assigning case: {e}")
            return None
    
    def update_case_status(self, case_id: str, new_status: str, actor: str = "system", reason: str = "Status updated") -> Optional[Dict[str, Any]]:
        """Update case status with notifications and workflows"""
        try:
            cases = self.load_cases()
            case = next((c for c in cases if c['case_id'] == case_id), None)
            
            if not case:
                return None
            
            old_status = case.get('status')
            case['status'] = new_status
            case['updated_at'] = datetime.utcnow().isoformat()
            
            # Add timeline event
            if 'timeline' not in case:
                case['timeline'] = []
            
            case['timeline'].append({
                'event_id': f"status_change_{datetime.utcnow().timestamp()}",
                'event_type': 'status_changed',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': actor,
                'description': f"Status changed from {old_status} to {new_status}",
                'metadata': {
                    'old_status': old_status,
                    'new_status': new_status,
                    'reason': reason
                }
            })
            
            # Send status change notification
            if self.notification_service:
                self.notification_service.notify_status_change(
                    case, old_status, new_status, actor, reason
                )
            
            # Execute status change workflow
            if self.workflow_service:
                from .workflow_service import WorkflowTrigger
                self.workflow_service.execute_workflow(case, WorkflowTrigger.STATUS_CHANGED)
            
            # Update case with advanced features
            case = self.update_case_with_advanced_features(case)
            
            # Save updated case
            self.save_cases(cases)
            
            logger.info(f"Case {case['case_number']} status changed to {new_status}")
            return case
            
        except Exception as e:
            logger.error(f"Error updating case status: {e}")
            return None
    
    def get_advanced_case_analytics(self) -> Dict[str, Any]:
        """Get advanced case analytics including SLA and workflow metrics"""
        try:
            cases = self.load_cases()
            
            # Basic case analytics
            basic_analytics = self.get_case_stats()
            
            # SLA analytics
            sla_analytics = {}
            if self.sla_service:
                sla_analytics = {
                    'compliance_report': self.sla_service.get_sla_compliance_report(cases),
                    'trends': self.sla_service.get_sla_trends(cases),
                    'cases_at_risk': len(self.sla_service.get_cases_at_risk(cases)),
                    'cases_breached': len(self.sla_service.get_cases_breached(cases))
                }
            
            # Workflow analytics
            workflow_analytics = {}
            if self.workflow_service:
                workflow_analytics = self.workflow_service.get_workflow_statistics()
            
            # Notification analytics
            notification_analytics = {}
            if self.notification_service:
                notification_analytics = self.notification_service.get_notification_statistics()
            
            return {
                'basic_analytics': basic_analytics,
                'sla_analytics': sla_analytics,
                'workflow_analytics': workflow_analytics,
                'notification_analytics': notification_analytics,
                'advanced_features_enabled': {
                    'sla_service': self.sla_service is not None,
                    'workflow_service': self.workflow_service is not None,
                    'notification_service': self.notification_service is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting advanced case analytics: {e}")
            return {}
    
    def update_sla_statuses(self):
        """Update SLA statuses for all cases"""
        cases = self.load_cases()
        updated = False
        
        for case in cases:
            new_sla_status = self.check_sla_status(case)
            if case.get('sla_status') != new_sla_status:
                case['sla_status'] = new_sla_status
                case['updated_at'] = datetime.utcnow().isoformat()
                
                # Add timeline event for SLA status change
                if new_sla_status in ['At Risk', 'Breached']:
                    timeline_event = {
                        'event_id': str(uuid.uuid4()),
                        'event_type': 'sla_status_changed',
                        'timestamp': datetime.utcnow().isoformat(),
                        'actor': 'system',
                        'description': f"SLA status changed to {new_sla_status}",
                        'metadata': {'new_sla_status': new_sla_status}
                    }
                    case['timeline'].append(timeline_event)
                
                updated = True
        
        if updated:
            self.save_cases(cases)
            logger.info("Updated SLA statuses for all cases")
    
    def add_thread_to_case(self, case_id: str, thread_data: dict) -> bool:
        """
        Add a communication thread entry to a case
        
        Args:
            case_id: Case UUID
            thread_data: {
                'direction': 'Inbound' | 'Outbound',
                'sender_name': str,
                'sender_email': str,
                'subject': str,
                'body': str,
                'timestamp': ISO datetime (optional),
                'message_id': str (optional)
            }
        
        Returns:
            bool: True if thread added successfully
        """
        try:
            cases = self.load_cases()
            case = next((c for c in cases if c['case_id'] == case_id), None)
            
            if not case:
                logger.error(f"Case not found: {case_id}")
                return False
            
            # Initialize threads array if it doesn't exist
            if 'threads' not in case:
                case['threads'] = []
            
            # Create thread entry
            thread_entry = {
                'thread_id': str(uuid.uuid4()),
                'timestamp': thread_data.get('timestamp', datetime.utcnow().isoformat()),
                'direction': thread_data['direction'],
                'sender_name': thread_data['sender_name'],
                'sender_email': thread_data['sender_email'],
                'subject': thread_data['subject'],
                'body': thread_data['body'],
                'message_id': thread_data.get('message_id', '')
            }
            
            case['threads'].append(thread_entry)
            case['updated_at'] = datetime.utcnow().isoformat()
            
            # Add timeline event
            if 'timeline' not in case:
                case['timeline'] = []
            
            timeline_event = {
                'event_id': str(uuid.uuid4()),
                'event_type': 'email_' + thread_data['direction'].lower(),
                'timestamp': datetime.utcnow().isoformat(),
                'actor': thread_data['sender_name'],
                'description': f"{thread_data['direction']} email: {thread_data['subject']}",
                'metadata': {
                    'sender': thread_data['sender_email'],
                    'subject': thread_data['subject']
                }
            }
            case['timeline'].append(timeline_event)
            
            self.save_cases(cases)
            logger.info(f"✉️ Added {thread_data['direction']} thread to case {case.get('case_number', case_id)}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding thread to case: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_case_threads(self, case_id: str) -> list:
        """
        Get all communication threads for a case
        
        Returns:
            List of thread dicts sorted by timestamp (newest first)
        """
        try:
            case = self.get_case_by_id(case_id)
            if not case:
                return []
            
            threads = case.get('threads', [])
            
            # Sort by timestamp descending (newest first)
            threads.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return threads
            
        except Exception as e:
            logger.error(f"Error getting case threads: {e}")
            return []
