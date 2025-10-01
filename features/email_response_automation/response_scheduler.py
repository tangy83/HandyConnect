#!/usr/bin/env python3
"""
Email Response Scheduler for HandyConnect Phase 12
Advanced scheduling and queue management for automated email responses
"""

import json
import logging
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from queue import PriorityQueue, Empty
import uuid

from .response_generator import EmailResponse

logger = logging.getLogger(__name__)

@dataclass
class ScheduledResponse:
    """Scheduled email response data"""
    id: str
    response: EmailResponse
    scheduled_at: datetime
    priority: int  # Lower number = higher priority
    retry_count: int = 0
    max_retries: int = 3
    status: str = "scheduled"  # scheduled, processing, sent, failed, cancelled
    created_at: datetime = None
    metadata: Dict[str, Any] = None

@dataclass
class SendingRule:
    """Business rule for email sending"""
    id: str
    name: str
    condition_type: str  # time_based, priority_based, volume_based, customer_based
    condition_params: Dict[str, Any]
    action: str  # send_immediately, delay, batch, escalate
    action_params: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = None

class ResponseScheduler:
    """Advanced email response scheduler with business rules"""
    
    def __init__(self):
        self.scheduled_responses = PriorityQueue()
        self.sending_rules = self._load_default_rules()
        self.processing_queue = []
        self.sent_responses = []
        self.failed_responses = []
        
        self.is_running = False
        self.scheduler_thread = None
        self.stats = {
            'total_scheduled': 0,
            'total_sent': 0,
            'total_failed': 0,
            'current_queue_size': 0
        }
        
        logger.info("Response scheduler initialized")
    
    def _load_default_rules(self) -> Dict[str, SendingRule]:
        """Load default business rules for email sending"""
        rules = {}
        
        # Time-based rules
        rules['business_hours'] = SendingRule(
            id='business_hours',
            name='Business Hours Only',
            condition_type='time_based',
            condition_params={
                'start_hour': 9,
                'end_hour': 17,
                'timezone': 'UTC',
                'weekdays_only': True
            },
            action='delay',
            action_params={
                'delay_until': 'next_business_hour',
                'max_delay_hours': 16
            },
            created_at=datetime.now(timezone.utc)
        )
        
        # Priority-based rules
        rules['urgent_priority'] = SendingRule(
            id='urgent_priority',
            name='Urgent Priority Immediate',
            condition_type='priority_based',
            condition_params={
                'priority': 'Urgent'
            },
            action='send_immediately',
            action_params={},
            created_at=datetime.now(timezone.utc)
        )
        
        # Volume-based rules
        rules['rate_limiting'] = SendingRule(
            id='rate_limiting',
            name='Rate Limiting',
            condition_type='volume_based',
            condition_params={
                'max_emails_per_hour': 100,
                'max_emails_per_recipient_per_day': 5
            },
            action='batch',
            action_params={
                'batch_size': 10,
                'batch_interval_minutes': 5
            },
            created_at=datetime.now(timezone.utc)
        )
        
        # Customer-based rules
        rules['vip_customers'] = SendingRule(
            id='vip_customers',
            name='VIP Customer Priority',
            condition_type='customer_based',
            condition_params={
                'customer_tier': 'VIP',
                'priority_boost': 2
            },
            action='send_immediately',
            action_params={},
            created_at=datetime.now(timezone.utc)
        )
        
        return rules
    
    def schedule_response(self, response: EmailResponse, send_immediately: bool = False) -> str:
        """Schedule an email response for sending"""
        try:
            # Apply business rules to determine scheduling
            scheduled_time = self._apply_sending_rules(response, send_immediately)
            
            # Calculate priority
            priority = self._calculate_priority(response)
            
            # Create scheduled response
            scheduled_response = ScheduledResponse(
                id=f"sched_{uuid.uuid4().hex[:8]}",
                response=response,
                scheduled_at=scheduled_time,
                priority=priority,
                created_at=datetime.now(timezone.utc),
                metadata={
                    'original_task_id': response.task_id,
                    'rule_applied': self._get_applied_rule(response),
                    'estimated_send_time': scheduled_time.isoformat()
                }
            )
            
            # Add to queue
            self.scheduled_responses.put((priority, scheduled_response))
            self.stats['total_scheduled'] += 1
            self.stats['current_queue_size'] = self.scheduled_responses.qsize()
            
            logger.info(f"Scheduled response {scheduled_response.id} for {scheduled_time}")
            
            # Start scheduler if not running
            if not self.is_running:
                self.start_scheduler()
            
            return scheduled_response.id
            
        except Exception as e:
            logger.error(f"Error scheduling response: {e}")
            raise
    
    def _apply_sending_rules(self, response: EmailResponse, send_immediately: bool) -> datetime:
        """Apply business rules to determine when to send the email"""
        if send_immediately:
            return datetime.now(timezone.utc)
        
        base_time = datetime.now(timezone.utc)
        
        # Apply time-based rules
        if self._is_business_hours_rule_applicable(response):
            business_hour_rule = self.sending_rules['business_hours']
            if not self._is_business_hours():
                base_time = self._get_next_business_hour()
        
        # Apply priority-based rules
        if self._is_urgent_priority(response):
            urgent_rule = self.sending_rules['urgent_priority']
            return datetime.now(timezone.utc)  # Send immediately
        
        # Apply volume-based rules (rate limiting)
        if self._is_rate_limited():
            rate_limit_rule = self.sending_rules['rate_limiting']
            batch_interval = rate_limit_rule.action_params.get('batch_interval_minutes', 5)
            base_time += timedelta(minutes=batch_interval)
        
        # Apply customer-based rules
        if self._is_vip_customer(response):
            vip_rule = self.sending_rules['vip_customers']
            return datetime.now(timezone.utc)  # Send immediately
        
        return base_time
    
    def _calculate_priority(self, response: EmailResponse) -> int:
        """Calculate priority score for scheduling (lower = higher priority)"""
        base_priority = 100
        
        # Priority mapping
        priority_weights = {
            'Urgent': 10,
            'High': 25,
            'Medium': 50,
            'Low': 100
        }
        
        base_priority = priority_weights.get(response.priority, 50)
        
        # Adjust for response type
        response_type_weights = {
            'escalation': -20,
            'resolution': -10,
            'acknowledgment': 0,
            'information_request': 5,
            'follow_up': 10,
            'closure': 15
        }
        
        base_priority += response_type_weights.get(response.response_type, 0)
        
        # Adjust for customer tier (if available)
        # This would be enhanced with actual customer data
        if response.metadata and response.metadata.get('customer_tier') == 'VIP':
            base_priority -= 30
        
        return max(1, base_priority)  # Ensure positive priority
    
    def _is_business_hours_rule_applicable(self, response: EmailResponse) -> bool:
        """Check if business hours rule applies to this response"""
        # Skip business hours for urgent responses
        if response.priority == 'Urgent':
            return False
        
        # Skip for escalation responses
        if response.response_type == 'escalation':
            return False
        
        return True
    
    def _is_business_hours(self) -> bool:
        """Check if current time is within business hours"""
        now = datetime.now(timezone.utc)
        business_rule = self.sending_rules['business_hours']
        
        start_hour = business_rule.condition_params.get('start_hour', 9)
        end_hour = business_rule.condition_params.get('end_hour', 17)
        weekdays_only = business_rule.condition_params.get('weekdays_only', True)
        
        # Check weekday constraint
        if weekdays_only and now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check hour constraint
        return start_hour <= now.hour < end_hour
    
    def _get_next_business_hour(self) -> datetime:
        """Get the next business hour"""
        now = datetime.now(timezone.utc)
        business_rule = self.sending_rules['business_hours']
        start_hour = business_rule.condition_params.get('start_hour', 9)
        
        # If it's weekend, move to next Monday
        if now.weekday() >= 5:  # Weekend
            days_ahead = 7 - now.weekday()  # Days until Monday
            next_business_day = now + timedelta(days=days_ahead)
            return next_business_day.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        
        # If it's after business hours, move to next day
        if now.hour >= 17:
            next_day = now + timedelta(days=1)
            return next_day.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        
        # If it's before business hours, move to today's start
        return now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    
    def _is_urgent_priority(self, response: EmailResponse) -> bool:
        """Check if response has urgent priority"""
        return response.priority == 'Urgent'
    
    def _is_rate_limited(self) -> bool:
        """Check if we're currently rate limited"""
        # This would be enhanced with actual rate limiting logic
        # For now, return False (no rate limiting)
        return False
    
    def _is_vip_customer(self, response: EmailResponse) -> bool:
        """Check if customer is VIP"""
        # This would be enhanced with actual customer data
        # For now, return False (no VIP customers)
        return False
    
    def _get_applied_rule(self, response: EmailResponse) -> str:
        """Get the name of the rule applied to this response"""
        if self._is_urgent_priority(response):
            return 'urgent_priority'
        elif self._is_business_hours_rule_applicable(response) and not self._is_business_hours():
            return 'business_hours'
        elif self._is_rate_limited():
            return 'rate_limiting'
        elif self._is_vip_customer(response):
            return 'vip_customers'
        else:
            return 'default'
    
    def start_scheduler(self):
        """Start the response scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
        self.scheduler_thread.start()
        logger.info("Response scheduler started")
    
    def stop_scheduler(self):
        """Stop the response scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Response scheduler stopped")
    
    def _scheduler_worker(self):
        """Background worker for processing scheduled responses"""
        while self.is_running:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Check for responses ready to send
                ready_responses = []
                
                # Process priority queue
                temp_queue = PriorityQueue()
                while not self.scheduled_responses.empty():
                    try:
                        priority, scheduled_response = self.scheduled_responses.get_nowait()
                        
                        if scheduled_response.scheduled_at <= current_time:
                            ready_responses.append(scheduled_response)
                        else:
                            temp_queue.put((priority, scheduled_response))
                    
                    except Empty:
                        break
                
                # Put remaining responses back
                while not temp_queue.empty():
                    priority, scheduled_response = temp_queue.get_nowait()
                    self.scheduled_responses.put((priority, scheduled_response))
                
                # Process ready responses
                for scheduled_response in ready_responses:
                    self._process_scheduled_response(scheduled_response)
                
                # Update stats
                self.stats['current_queue_size'] = self.scheduled_responses.qsize()
                
                # Sleep for a short interval
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in scheduler worker: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _process_scheduled_response(self, scheduled_response: ScheduledResponse):
        """Process a scheduled response for sending"""
        try:
            scheduled_response.status = 'processing'
            
            # Simulate email sending (in real implementation, this would call email service)
            success = self._send_email(scheduled_response.response)
            
            if success:
                scheduled_response.status = 'sent'
                scheduled_response.response.sent_at = datetime.now(timezone.utc)
                self.sent_responses.append(scheduled_response)
                self.stats['total_sent'] += 1
                logger.info(f"Successfully sent response {scheduled_response.id}")
            else:
                # Handle retry logic
                scheduled_response.retry_count += 1
                
                if scheduled_response.retry_count < scheduled_response.max_retries:
                    # Reschedule with exponential backoff
                    delay_minutes = 2 ** scheduled_response.retry_count
                    scheduled_response.scheduled_at = datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)
                    scheduled_response.status = 'scheduled'
                    
                    # Add back to queue
                    self.scheduled_responses.put((scheduled_response.priority, scheduled_response))
                    logger.warning(f"Rescheduling response {scheduled_response.id} (retry {scheduled_response.retry_count})")
                else:
                    # Max retries exceeded
                    scheduled_response.status = 'failed'
                    self.failed_responses.append(scheduled_response)
                    self.stats['total_failed'] += 1
                    logger.error(f"Failed to send response {scheduled_response.id} after {scheduled_response.max_retries} retries")
        
        except Exception as e:
            logger.error(f"Error processing scheduled response {scheduled_response.id}: {e}")
            scheduled_response.status = 'failed'
            self.failed_responses.append(scheduled_response)
            self.stats['total_failed'] += 1
    
    def _send_email(self, response: EmailResponse) -> bool:
        """Simulate sending an email (placeholder for actual email service)"""
        try:
            # In a real implementation, this would:
            # 1. Validate email content
            # 2. Connect to email service (SMTP, SendGrid, etc.)
            # 3. Send the email
            # 4. Handle delivery confirmations
            # 5. Update tracking information
            
            logger.info(f"Simulating email send to {response.recipient_email}")
            logger.info(f"Subject: {response.subject}")
            logger.info(f"Body preview: {response.body[:100]}...")
            
            # Simulate success (90% success rate)
            import random
            return random.random() < 0.9
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def get_scheduled_responses(self, status: str = None) -> List[ScheduledResponse]:
        """Get scheduled responses by status"""
        responses = []
        
        # Get from queue (current scheduled)
        temp_queue = PriorityQueue()
        while not self.scheduled_responses.empty():
            try:
                priority, scheduled_response = self.scheduled_responses.get_nowait()
                if not status or scheduled_response.status == status:
                    responses.append(scheduled_response)
                temp_queue.put((priority, scheduled_response))
            except Empty:
                break
        
        # Put responses back
        while not temp_queue.empty():
            priority, scheduled_response = temp_queue.get_nowait()
            self.scheduled_responses.put((priority, scheduled_response))
        
        # Add from other lists
        for response in self.sent_responses + self.failed_responses + self.processing_queue:
            if not status or response.status == status:
                responses.append(response)
        
        return responses
    
    def cancel_response(self, scheduled_id: str) -> bool:
        """Cancel a scheduled response"""
        try:
            # Check in current queue
            temp_queue = PriorityQueue()
            found = False
            
            while not self.scheduled_responses.empty():
                try:
                    priority, scheduled_response = self.scheduled_responses.get_nowait()
                    
                    if scheduled_response.id == scheduled_id:
                        scheduled_response.status = 'cancelled'
                        found = True
                    else:
                        temp_queue.put((priority, scheduled_response))
                except Empty:
                    break
            
            # Put responses back
            while not temp_queue.empty():
                priority, scheduled_response = temp_queue.get_nowait()
                self.scheduled_responses.put((priority, scheduled_response))
            
            if found:
                logger.info(f"Cancelled scheduled response {scheduled_id}")
                return True
            else:
                logger.warning(f"Scheduled response {scheduled_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling response {scheduled_id}: {e}")
            return False
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        return {
            'is_running': self.is_running,
            'stats': self.stats.copy(),
            'queue_size': self.scheduled_responses.qsize(),
            'active_rules': len([rule for rule in self.sending_rules.values() if rule.is_active]),
            'total_rules': len(self.sending_rules)
        }
    
    def add_sending_rule(self, rule: SendingRule) -> bool:
        """Add a new sending rule"""
        try:
            rule.created_at = datetime.now(timezone.utc)
            self.sending_rules[rule.id] = rule
            logger.info(f"Added sending rule: {rule.id}")
            return True
        except Exception as e:
            logger.error(f"Error adding sending rule: {e}")
            return False
    
    def update_sending_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing sending rule"""
        try:
            if rule_id in self.sending_rules:
                rule = self.sending_rules[rule_id]
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                logger.info(f"Updated sending rule: {rule_id}")
                return True
            else:
                logger.warning(f"Sending rule {rule_id} not found")
                return False
        except Exception as e:
            logger.error(f"Error updating sending rule: {e}")
            return False
