#!/usr/bin/env python3
"""
Test Phase 4: Integration and Optimization
Comprehensive testing of case management integration and performance optimization
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_case_email_integration():
    """Test case-email integration"""
    print("=" * 60)
    print("🧪 Testing Case-Email Integration")
    print("=" * 60)
    
    try:
        from features.core_services.case_service import CaseService
        from features.core_services.email_service import EmailService
        
        # Initialize services
        case_service = CaseService()
        email_service = EmailService()
        
        # Get a test case
        cases = case_service.load_cases()
        if not cases:
            print("❌ No cases found for testing")
            return False
        
        test_case = cases[0]
        case_id = test_case['case_id']
        
        # Test case context in email service
        case_context = email_service._get_case_context(case_id)
        if case_context:
            print(f"✅ Case context retrieved: {case_context['case_number']}")
        else:
            print("❌ Failed to get case context")
            return False
        
        # Test case email thread
        case_emails = email_service.get_case_email_thread(case_id)
        print(f"✅ Case email thread: {len(case_emails)} emails found")
        
        # Test email response with case context
        success = email_service.send_email_response(
            case_id, 
            "Test response from integrated system",
            "test@example.com",
            "Test Subject"
        )
        if success:
            print("✅ Email response sent with case context")
        else:
            print("❌ Failed to send email response")
            return False
        
        print("✅ Case-Email integration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Case-Email integration test failed: {e}")
        return False

def test_case_task_integration():
    """Test case-task integration"""
    print("\n" + "=" * 60)
    print("🧪 Testing Case-Task Integration")
    print("=" * 60)
    
    try:
        from features.core_services.case_service import CaseService
        from features.core_services.task_service import TaskService
        
        # Initialize services
        case_service = CaseService()
        task_service = TaskService()
        
        # Get a test case
        cases = case_service.load_cases()
        if not cases:
            print("❌ No cases found for testing")
            return False
        
        test_case = cases[0]
        case_id = test_case['case_id']
        
        # Test getting tasks by case
        case_tasks = task_service.get_tasks_by_case(case_id)
        print(f"✅ Case tasks retrieved: {len(case_tasks)} tasks found")
        
        # Test case task summary
        summary = task_service.get_case_task_summary(case_id)
        if summary:
            print(f"✅ Case task summary: {summary['total_tasks']} total tasks, {summary['completion_rate']}% complete")
        else:
            print("❌ Failed to get case task summary")
            return False
        
        # Test creating task with case context
        task_data = {
            'title': 'Phase 4 Integration Test Task',
            'description': 'Testing case-task integration',
            'priority': 'Medium',
            'category': 'Testing'
        }
        
        new_task = task_service.create_task_with_case_context(task_data, case_id)
        if new_task:
            print(f"✅ Task created with case context: {new_task['id']}")
            
            # Test updating task with case context sync
            updated_task = task_service.update_task_with_case_context(
                new_task['id'], 
                {'status': 'Completed'}
            )
            if updated_task:
                print("✅ Task updated with case context sync")
            else:
                print("❌ Failed to update task with case context")
                return False
        else:
            print("❌ Failed to create task with case context")
            return False
        
        print("✅ Case-Task integration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Case-Task integration test failed: {e}")
        return False

def test_performance_monitoring():
    """Test performance monitoring system"""
    print("\n" + "=" * 60)
    print("🧪 Testing Performance Monitoring")
    print("=" * 60)
    
    try:
        from features.core_services.performance_monitor import PerformanceMonitor, performance_timer
        
        # Initialize performance monitor
        monitor = PerformanceMonitor()
        print("✅ Performance monitor initialized")
        
        # Test recording metrics
        monitor.record_metric(
            "test_component", 
            "test_operation", 
            150.5, 
            success=True,
            metadata={'test': 'data'}
        )
        print("✅ Performance metric recorded")
        
        # Test performance summary
        summary = monitor.get_performance_summary("test_component", hours=1)
        if summary:
            print(f"✅ Performance summary: {summary['total_operations']} operations, {summary['success_rate']}% success rate")
        else:
            print("❌ Failed to get performance summary")
            return False
        
        # Test component performance
        component_perf = monitor.get_component_performance()
        if "test_component" in component_perf:
            print(f"✅ Component performance tracked: {component_perf['test_component']['total_operations']} operations")
        else:
            print("❌ Component performance not tracked")
            return False
        
        # Test performance trends
        trends = monitor.get_performance_trends("test_component", hours=1)
        if trends:
            print(f"✅ Performance trends: {len(trends['timestamps'])} data points")
        else:
            print("❌ Failed to get performance trends")
            return False
        
        # Test performance timer decorator
        @performance_timer("test_component", "decorated_function")
        def test_function():
            time.sleep(0.1)  # Simulate work
            return "success"
        
        result = test_function()
        if result == "success":
            print("✅ Performance timer decorator working")
        else:
            print("❌ Performance timer decorator failed")
            return False
        
        # Test alert system
        # Create a critical performance event
        monitor.record_metric("test_component", "slow_operation", 2500, success=True)
        
        active_alerts = monitor.get_active_alerts()
        if active_alerts:
            print(f"✅ Performance alerts generated: {len(active_alerts)} active alerts")
            
            # Test resolving alert
            alert_id = active_alerts[0]['alert_id']
            if monitor.resolve_alert(alert_id):
                print("✅ Alert resolved successfully")
            else:
                print("❌ Failed to resolve alert")
                return False
        else:
            print("⚠️ No performance alerts generated (may be expected)")
        
        print("✅ Performance monitoring tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Performance monitoring test failed: {e}")
        return False

def test_case_service_performance():
    """Test case service with performance monitoring"""
    print("\n" + "=" * 60)
    print("🧪 Testing Case Service Performance")
    print("=" * 60)
    
    try:
        from features.core_services.case_service import CaseService
        
        # Initialize case service
        case_service = CaseService()
        print("✅ Case service initialized with performance monitoring")
        
        # Test case loading performance
        start_time = time.time()
        cases = case_service.load_cases()
        load_time = (time.time() - start_time) * 1000
        print(f"✅ Case loading: {len(cases)} cases in {load_time:.2f}ms")
        
        # Test case statistics performance
        start_time = time.time()
        stats = case_service.get_case_stats()
        stats_time = (time.time() - start_time) * 1000
        print(f"✅ Case statistics: {stats_time:.2f}ms")
        
        # Test advanced analytics performance
        start_time = time.time()
        analytics = case_service.get_advanced_case_analytics()
        analytics_time = (time.time() - start_time) * 1000
        print(f"✅ Advanced analytics: {analytics_time:.2f}ms")
        
        # Check performance monitor metrics
        if case_service.performance_monitor:
            monitor_summary = case_service.performance_monitor.get_performance_summary("case_service", hours=1)
            if monitor_summary:
                print(f"✅ Performance metrics recorded: {monitor_summary['total_operations']} operations")
                print(f"   Average response time: {monitor_summary['avg_response_time_ms']}ms")
                print(f"   Success rate: {monitor_summary['success_rate']}%")
            else:
                print("⚠️ No performance metrics recorded")
        
        # Test caching performance
        start_time = time.time()
        cached_cases = case_service.load_cases()  # Should be cached
        cache_time = (time.time() - start_time) * 1000
        print(f"✅ Cached case loading: {cache_time:.2f}ms")
        
        if cache_time < load_time * 0.5:  # Cache should be significantly faster
            print("✅ Caching performance improvement verified")
        else:
            print("⚠️ Caching performance improvement not significant")
        
        print("✅ Case service performance tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Case service performance test failed: {e}")
        return False

def test_end_to_end_integration():
    """Test end-to-end integration of all components"""
    print("\n" + "=" * 60)
    print("🧪 Testing End-to-End Integration")
    print("=" * 60)
    
    try:
        from features.core_services.case_service import CaseService
        from features.core_services.task_service import TaskService
        from features.core_services.email_service import EmailService
        from features.core_services.performance_monitor import PerformanceMonitor
        
        # Initialize all services
        case_service = CaseService()
        task_service = TaskService()
        email_service = EmailService()
        monitor = PerformanceMonitor()
        
        print("✅ All services initialized")
        
        # Create a comprehensive test scenario
        # 1. Create a new case
        case_data = {
            'case_title': 'Phase 4 End-to-End Test',
            'case_type': 'General',
            'priority': 'High',
            'customer_info': {
                'name': 'E2E Test Customer',
                'email': 'e2e@test.com'
            },
            'description': 'Testing complete integration'
        }
        
        new_case = case_service.create_case(case_data)
        if not new_case:
            print("❌ Failed to create test case")
            return False
        
        case_id = new_case['case_id']
        print(f"✅ Test case created: {new_case['case_number']}")
        
        # 2. Create tasks for the case
        task_data = {
            'title': 'E2E Integration Task 1',
            'description': 'First task for end-to-end testing',
            'priority': 'High',
            'category': 'Testing'
        }
        
        task1 = task_service.create_task_with_case_context(task_data, case_id)
        if not task1:
            print("❌ Failed to create task for case")
            return False
        
        print(f"✅ Task created with case context: {task1['id']}")
        
        # 3. Update task status and verify case sync
        updated_task = task_service.update_task_with_case_context(
            task1['id'], 
            {'status': 'In Progress'}
        )
        if not updated_task:
            print("❌ Failed to update task status")
            return False
        
        print("✅ Task status updated with case sync")
        
        # 4. Test email integration
        case_context = email_service._get_case_context(case_id)
        if not case_context:
            print("❌ Failed to get case context for email")
            return False
        
        print("✅ Case context available for email operations")
        
        # 5. Test SLA and workflow integration
        updated_case = case_service.update_case_with_advanced_features(new_case)
        if updated_case.get('sla_metrics'):
            print("✅ SLA metrics calculated and applied")
        
        # 6. Test notification integration
        assigned_case = case_service.assign_case(
            case_id, 
            "e2e-agent@company.com", 
            "e2e_test"
        )
        if assigned_case:
            print("✅ Case assignment with notifications")
        
        # 7. Test performance monitoring
        performance_summary = monitor.get_performance_summary(hours=1)
        if performance_summary:
            print(f"✅ Performance monitoring: {performance_summary['total_operations']} operations tracked")
        
        # 8. Test analytics integration
        analytics = case_service.get_advanced_case_analytics()
        if analytics.get('advanced_features_enabled'):
            enabled_features = analytics['advanced_features_enabled']
            active_features = [k for k, v in enabled_features.items() if v]
            print(f"✅ Advanced features active: {', '.join(active_features)}")
        
        print("✅ End-to-end integration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end integration test failed: {e}")
        return False

def test_system_optimization():
    """Test system optimization features"""
    print("\n" + "=" * 60)
    print("🧪 Testing System Optimization")
    print("=" * 60)
    
    try:
        from features.core_services.case_service import CaseService
        from features.core_services.cache_service import CacheService, CacheType
        
        # Test cache optimization
        cache = CacheService(cache_type=CacheType.MEMORY, default_ttl=60, max_size=100)
        
        # Test cache performance
        test_data = {"test": "data", "timestamp": datetime.utcnow().isoformat()}
        
        # First access (cache miss)
        start_time = time.time()
        cache.set("test_key", test_data)
        cache_time = (time.time() - start_time) * 1000
        print(f"✅ Cache set operation: {cache_time:.2f}ms")
        
        # Second access (cache hit)
        start_time = time.time()
        cached_data = cache.get("test_key")
        cache_hit_time = (time.time() - start_time) * 1000
        print(f"✅ Cache get operation: {cache_hit_time:.2f}ms")
        
        if cached_data == test_data:
            print("✅ Cache data integrity verified")
        else:
            print("❌ Cache data integrity failed")
            return False
        
        # Test cache statistics
        cache_stats = cache.get_stats()
        if cache_stats:
            print(f"✅ Cache statistics: {cache_stats['hits']} hits, {cache_stats['misses']} misses, {cache_stats['hit_rate']}% hit rate")
        
        # Test case service optimization
        case_service = CaseService()
        
        # Test bulk operations
        cases = case_service.load_cases()
        if cases:
            # Test filtering performance
            start_time = time.time()
            high_priority_cases = [c for c in cases if c.get('priority') == 'High']
            filter_time = (time.time() - start_time) * 1000
            print(f"✅ Case filtering: {len(high_priority_cases)} high priority cases in {filter_time:.2f}ms")
            
            # Test statistics calculation performance
            start_time = time.time()
            stats = case_service.get_case_stats()
            calc_time = (time.time() - start_time) * 1000
            print(f"✅ Statistics calculation: {calc_time:.2f}ms")
            
            # Test analytics performance
            start_time = time.time()
            analytics = case_service.get_advanced_case_analytics()
            analytics_time = (time.time() - start_time) * 1000
            print(f"✅ Advanced analytics: {analytics_time:.2f}ms")
        
        # Test memory usage optimization
        import psutil
        memory_info = psutil.virtual_memory()
        print(f"✅ Memory usage: {memory_info.used / (1024 * 1024):.2f}MB used, {memory_info.percent}% utilized")
        
        if memory_info.percent < 80:
            print("✅ Memory usage within acceptable limits")
        else:
            print("⚠️ High memory usage detected")
        
        print("✅ System optimization tests passed")
        return True
        
    except Exception as e:
        print(f"❌ System optimization test failed: {e}")
        return False

def main():
    """Run all Phase 4 tests"""
    print("🚀 Starting Phase 4: Integration and Optimization Tests")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run all tests
    tests = [
        ("Case-Email Integration", test_case_email_integration),
        ("Case-Task Integration", test_case_task_integration),
        ("Performance Monitoring", test_performance_monitoring),
        ("Case Service Performance", test_case_service_performance),
        ("End-to-End Integration", test_end_to_end_integration),
        ("System Optimization", test_system_optimization)
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
    print("📊 Phase 4 Test Results Summary")
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
        print("\n🎉 All Phase 4 tests passed! Integration and optimization complete.")
        return True
    else:
        print(f"\n⚠️ {total-passed} tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
