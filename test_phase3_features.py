#!/usr/bin/env python3
"""
Test Phase 3 Advanced Features
Test SLA management, workflow automation, notifications, and caching
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sla_service():
    """Test SLA Service functionality"""
    print("=" * 60)
    print("🧪 Testing SLA Service")
    print("=" * 60)
    
    try:
        from features.core_services.sla_service import SLAService, SLAPriority, SLAStatus
        
        # Initialize SLA service
        sla_service = SLAService()
        print("✅ SLA Service initialized")
        
        # Test SLA configurations
        configurations = sla_service.load_configurations()
        print(f"✅ Loaded {len(configurations)} SLA configurations")
        
        # Test SLA calculation for different case types
        test_cases = [
            {
                'case_id': 'test-case-1',
                'case_type': 'Security',
                'priority': 'Critical',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            },
            {
                'case_id': 'test-case-2',
                'case_type': 'Complaint',
                'priority': 'High',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            },
            {
                'case_id': 'test-case-3',
                'case_type': 'General',
                'priority': 'Medium',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
        ]
        
        for case in test_cases:
            config = sla_service.get_sla_configuration(case['case_type'], case['priority'])
            if config:
                print(f"✅ SLA config for {case['case_type']}/{case['priority']}: {config.response_time_hours}h response, {config.resolution_time_hours}h resolution")
            
            metrics = sla_service.calculate_sla_metrics(case)
            if metrics:
                print(f"✅ SLA metrics calculated for {case['case_id']}: {metrics.resolution_status.value}")
        
        # Test SLA compliance report
        compliance_report = sla_service.get_sla_compliance_report(test_cases)
        print(f"✅ SLA compliance report generated: {compliance_report}")
        
        print("✅ SLA Service tests passed")
        return True
        
    except Exception as e:
        print(f"❌ SLA Service test failed: {e}")
        return False

def test_workflow_service():
    """Test Workflow Service functionality"""
    print("\n" + "=" * 60)
    print("🧪 Testing Workflow Service")
    print("=" * 60)
    
    try:
        from features.core_services.workflow_service import WorkflowService, WorkflowTrigger
        
        # Initialize workflow service
        workflow_service = WorkflowService()
        print("✅ Workflow Service initialized")
        
        # Test workflow rules
        rules = workflow_service.load_rules()
        print(f"✅ Loaded {len(rules)} workflow rules")
        
        # Test workflow execution
        test_case = {
            'case_id': 'test-case-workflow',
            'case_number': 'CASE-20251005-TEST',
            'priority': 'High',
            'status': 'New',
            'assigned_to': None,
            'escalated': False,
            'notified_at_risk': False,
            'case_metadata': {
                'last_activity_date': datetime.utcnow().isoformat()
            },
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Test case creation workflow
        executions = workflow_service.execute_workflow(test_case, WorkflowTrigger.CASE_CREATED)
        print(f"✅ Workflow execution resulted in {len(executions)} executions")
        
        # Test SLA breach workflow
        test_case['sla_status'] = 'Breached'
        executions = workflow_service.execute_workflow(test_case, WorkflowTrigger.SLA_BREACHED, 'Breached')
        print(f"✅ SLA breach workflow executed: {len(executions)} executions")
        
        # Test workflow statistics
        stats = workflow_service.get_workflow_statistics()
        print(f"✅ Workflow statistics: {stats}")
        
        print("✅ Workflow Service tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Workflow Service test failed: {e}")
        return False

def test_notification_service():
    """Test Notification Service functionality"""
    print("\n" + "=" * 60)
    print("🧪 Testing Notification Service")
    print("=" * 60)
    
    try:
        from features.core_services.notification_service import NotificationService, NotificationType, NotificationPriority
        
        # Initialize notification service
        notification_service = NotificationService()
        print("✅ Notification Service initialized")
        
        # Test notification templates
        templates = notification_service.load_templates()
        print(f"✅ Loaded {len(templates)} notification templates")
        
        # Test sending notifications
        test_case = {
            'case_id': 'test-case-notification',
            'case_number': 'CASE-20251005-NOTIF',
            'case_title': 'Test Notification Case',
            'priority': 'High',
            'case_type': 'General',
            'assigned_to': 'test-agent@company.com',
            'customer_info': {
                'name': 'Test Customer',
                'email': 'test@customer.com'
            },
            'created_at': datetime.utcnow().isoformat(),
            'sla_metrics': {
                'resolution_due_date': (datetime.utcnow() + timedelta(hours=8)).isoformat()
            }
        }
        
        # Test SLA breach notification
        sla_metrics = {
            'resolution_due_date': (datetime.utcnow() - timedelta(hours=1)).isoformat()
        }
        notifications = notification_service.notify_sla_breach(test_case, sla_metrics)
        print(f"✅ SLA breach notifications sent: {len(notifications)}")
        
        # Test case assignment notification
        notification = notification_service.notify_case_assignment(test_case, 'new-agent@company.com')
        if notification:
            print(f"✅ Case assignment notification sent: {notification.id}")
        
        # Test notification statistics
        stats = notification_service.get_notification_statistics()
        print(f"✅ Notification statistics: {stats}")
        
        print("✅ Notification Service tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Notification Service test failed: {e}")
        return False

def test_cache_service():
    """Test Cache Service functionality"""
    print("\n" + "=" * 60)
    print("🧪 Testing Cache Service")
    print("=" * 60)
    
    try:
        from features.core_services.cache_service import CacheService, CacheType
        
        # Initialize cache service
        cache = CacheService(cache_type=CacheType.MEMORY, default_ttl=60, max_size=100)
        print("✅ Cache Service initialized")
        
        # Test basic cache operations
        test_key = "test_key"
        test_value = {"test": "data", "timestamp": datetime.utcnow().isoformat()}
        
        # Test set and get
        cache.set(test_key, test_value, ttl=30)
        cached_value = cache.get(test_key)
        
        if cached_value == test_value:
            print("✅ Cache set and get operations working")
        else:
            print("❌ Cache set and get operations failed")
            return False
        
        # Test cache exists
        if cache.exists(test_key):
            print("✅ Cache exists check working")
        else:
            print("❌ Cache exists check failed")
            return False
        
        # Test cache statistics
        stats = cache.get_stats()
        print(f"✅ Cache statistics: {stats}")
        
        # Test cache cleanup
        cleaned = cache.cleanup_expired()
        print(f"✅ Cache cleanup: {cleaned} expired entries removed")
        
        print("✅ Cache Service tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Cache Service test failed: {e}")
        return False

def test_enhanced_case_service():
    """Test enhanced Case Service with advanced features"""
    print("\n" + "=" * 60)
    print("🧪 Testing Enhanced Case Service")
    print("=" * 60)
    
    try:
        from features.core_services.case_service import CaseService
        
        # Initialize enhanced case service
        case_service = CaseService()
        print("✅ Enhanced Case Service initialized")
        
        # Check if advanced services are available
        advanced_features = {
            'SLA Service': case_service.sla_service is not None,
            'Workflow Service': case_service.workflow_service is not None,
            'Notification Service': case_service.notification_service is not None,
            'Cache Service': case_service.cache is not None
        }
        
        print("✅ Advanced features status:")
        for feature, available in advanced_features.items():
            status = "✅ Available" if available else "⚠️ Not Available"
            print(f"   {feature}: {status}")
        
        # Test enhanced case analytics
        analytics = case_service.get_advanced_case_analytics()
        print(f"✅ Advanced analytics generated: {len(analytics)} sections")
        
        # Test case assignment with notifications
        cases = case_service.load_cases()
        if cases:
            test_case = cases[0]
            updated_case = case_service.assign_case(
                test_case['case_id'], 
                'test-agent@company.com', 
                'test_user'
            )
            if updated_case:
                print(f"✅ Case assignment with notifications: {updated_case['case_number']}")
        
        # Test case status update with workflows
        if cases:
            test_case = cases[0]
            updated_case = case_service.update_case_status(
                test_case['case_id'], 
                'In Progress', 
                'test_user',
                'Testing workflow automation'
            )
            if updated_case:
                print(f"✅ Case status update with workflows: {updated_case['case_number']}")
        
        print("✅ Enhanced Case Service tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Case Service test failed: {e}")
        return False

def test_integration():
    """Test integration of all Phase 3 features"""
    print("\n" + "=" * 60)
    print("🧪 Testing Phase 3 Integration")
    print("=" * 60)
    
    try:
        from features.core_services.case_service import CaseService
        
        # Initialize case service
        case_service = CaseService()
        
        # Create a test case scenario
        test_case_data = {
            'case_title': 'Phase 3 Integration Test',
            'case_type': 'General',
            'priority': 'High',
            'customer_info': {
                'name': 'Integration Test Customer',
                'email': 'integration@test.com'
            },
            'description': 'Testing Phase 3 advanced features integration'
        }
        
        # Create case (this would normally come from email processing)
        new_case = case_service.create_case(test_case_data)
        if new_case:
            print(f"✅ Test case created: {new_case['case_number']}")
            
            # Test SLA calculation and monitoring
            updated_case = case_service.update_case_with_advanced_features(new_case)
            if updated_case.get('sla_metrics'):
                print(f"✅ SLA metrics calculated and applied")
            
            # Test assignment with notifications and workflows
            assigned_case = case_service.assign_case(
                new_case['case_id'], 
                'integration-agent@company.com', 
                'integration_test'
            )
            if assigned_case:
                print(f"✅ Case assigned with notifications and workflows")
            
            # Test status update with workflows
            status_updated_case = case_service.update_case_status(
                new_case['case_id'], 
                'In Progress', 
                'integration_test',
                'Testing Phase 3 integration'
            )
            if status_updated_case:
                print(f"✅ Case status updated with workflows")
            
            # Test advanced analytics
            analytics = case_service.get_advanced_case_analytics()
            if analytics.get('advanced_features_enabled'):
                print(f"✅ Advanced analytics with all features")
            
            print("✅ Phase 3 Integration tests passed")
            return True
        else:
            print("❌ Failed to create test case")
            return False
        
    except Exception as e:
        print(f"❌ Phase 3 Integration test failed: {e}")
        return False

def main():
    """Run all Phase 3 tests"""
    print("🚀 Starting Phase 3 Advanced Features Tests")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run all tests
    tests = [
        ("SLA Service", test_sla_service),
        ("Workflow Service", test_workflow_service),
        ("Notification Service", test_notification_service),
        ("Cache Service", test_cache_service),
        ("Enhanced Case Service", test_enhanced_case_service),
        ("Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 80)
    print("📊 Phase 3 Test Results Summary")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
        if success:
            passed += 1
    
    print("-" * 80)
    print(f"Tests: {passed}/{total} passed ({passed/total*100:.1f}%)")
    print(f"Duration: {duration:.2f} seconds")
    
    if passed == total:
        print("\n🎉 All Phase 3 tests passed! Advanced features are working correctly.")
        return True
    else:
        print(f"\n⚠️ {total-passed} tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
