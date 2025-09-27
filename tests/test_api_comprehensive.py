"""
Comprehensive API tests for HandyConnect application
"""
import pytest
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch

class TestAnalyticsAPI:
    """Test analytics API endpoints"""
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_analytics_health_endpoint(self, test_app):
        """Test analytics health endpoint"""
        response = test_app.get('/api/analytics/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert data['data']['service'] == 'analytics'
        assert data['data']['status'] == 'healthy'
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_analytics_report_endpoint(self, test_app):
        """Test analytics report endpoint"""
        # Test with default date range
        response = test_app.get('/api/analytics/report')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'task_analytics' in data['data']
        assert 'thread_analytics' in data['data']
        assert 'performance_metrics' in data['data']
        assert 'system_health' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_analytics_report_with_date_range(self, test_app):
        """Test analytics report endpoint with custom date range"""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        
        response = test_app.get('/api/analytics/report', query_string=params)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_task_analytics_endpoint(self, test_app):
        """Test task analytics endpoint"""
        response = test_app.get('/api/analytics/tasks')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'total_tasks' in data['data']
        assert 'status_distribution' in data['data']
        assert 'priority_distribution' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_thread_analytics_endpoint(self, test_app):
        """Test thread analytics endpoint"""
        response = test_app.get('/api/analytics/threads')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'total_threads' in data['data']
        assert 'total_messages' in data['data']
        assert 'status_distribution' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_performance_analytics_endpoint(self, test_app):
        """Test performance analytics endpoint"""
        response = test_app.get('/api/analytics/performance')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'metrics' in data['data']
        assert 'total_metrics' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_performance_analytics_with_metric_type(self, test_app):
        """Test performance analytics endpoint with specific metric type"""
        params = {'metric_type': 'response_time'}
        response = test_app.get('/api/analytics/performance', query_string=params)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_system_health_analytics_endpoint(self, test_app):
        """Test system health analytics endpoint"""
        response = test_app.get('/api/analytics/system-health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'services' in data['data']
        assert 'total_records' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_current_metrics_endpoint(self, test_app):
        """Test current metrics endpoint"""
        response = test_app.get('/api/analytics/current-metrics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'timestamp' in data['data']
        assert 'system' in data['data']
        assert 'application' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_dashboard_charts_endpoint(self, test_app):
        """Test dashboard charts endpoint"""
        response = test_app.get('/api/analytics/charts')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'charts' in data['data']
        assert 'generated_at' in data['data']
        assert 'period' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_task_status_chart_endpoint(self, test_app):
        """Test task status chart endpoint"""
        response = test_app.get('/api/analytics/charts/task-status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'type' in data['data']
        assert 'data' in data['data']
        assert 'options' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_priority_distribution_chart_endpoint(self, test_app):
        """Test priority distribution chart endpoint"""
        response = test_app.get('/api/analytics/charts/priority-distribution')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'type' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_response_time_trend_chart_endpoint(self, test_app):
        """Test response time trend chart endpoint"""
        response = test_app.get('/api/analytics/charts/response-time-trend')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'type' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_performance_metrics_chart_endpoint(self, test_app):
        """Test performance metrics chart endpoint"""
        response = test_app.get('/api/analytics/charts/performance-metrics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'type' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_system_health_chart_endpoint(self, test_app):
        """Test system health chart endpoint"""
        response = test_app.get('/api/analytics/charts/system-health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'type' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_collect_task_data_endpoint(self, test_app, sample_task_data):
        """Test collect task data endpoint"""
        response = test_app.post('/api/analytics/collect/task', 
                               data=json.dumps(sample_task_data),
                               content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['processed'] == True
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_collect_thread_data_endpoint(self, test_app, sample_thread_data):
        """Test collect thread data endpoint"""
        response = test_app.post('/api/analytics/collect/thread',
                               data=json.dumps(sample_thread_data),
                               content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['processed'] == True
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_collect_user_behavior_endpoint(self, test_app, sample_user_behavior):
        """Test collect user behavior endpoint"""
        response = test_app.post('/api/analytics/collect/user-behavior',
                               data=json.dumps(sample_user_behavior),
                               content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['tracked'] == True
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_collect_user_behavior_missing_fields(self, test_app):
        """Test collect user behavior endpoint with missing required fields"""
        incomplete_data = {
            'user_id': 'test_user',
            'action': 'page_view'
            # Missing session_id and page
        }
        
        response = test_app.post('/api/analytics/collect/user-behavior',
                               data=json.dumps(incomplete_data),
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Missing required field' in data['message']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_cleanup_old_data_endpoint(self, test_app):
        """Test cleanup old data endpoint"""
        response = test_app.post('/api/analytics/admin/cleanup')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'deleted_files' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_storage_stats_endpoint(self, test_app):
        """Test storage stats endpoint"""
        response = test_app.get('/api/analytics/admin/storage-stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'total_size_mb' in data['data']
        assert 'file_counts' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_export_analytics_data_endpoint(self, test_app):
        """Test export analytics data endpoint"""
        export_data = {
            'data_type': 'tasks',
            'start_date': (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
            'end_date': datetime.now(timezone.utc).isoformat()
        }
        
        response = test_app.post('/api/analytics/admin/export',
                               data=json.dumps(export_data),
                               content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'output_file' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_export_analytics_data_missing_type(self, test_app):
        """Test export analytics data endpoint with missing data type"""
        export_data = {
            'start_date': (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
            'end_date': datetime.now(timezone.utc).isoformat()
            # Missing data_type
        }
        
        response = test_app.post('/api/analytics/admin/export',
                               data=json.dumps(export_data),
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Missing data_type parameter' in data['message']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_metrics_summary_endpoint(self, test_app):
        """Test metrics summary endpoint"""
        response = test_app.get('/api/analytics/metrics/summary')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'total_metrics' in data['data']
        assert 'time_range' in data['data']
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_metrics_summary_with_hours(self, test_app):
        """Test metrics summary endpoint with custom hours"""
        params = {'hours': '12'}
        response = test_app.get('/api/analytics/metrics/summary', query_string=params)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert data['data']['time_range']['hours'] == 12
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_record_custom_metric_endpoint(self, test_app):
        """Test record custom metric endpoint"""
        metric_data = {
            'metric_type': 'test_metric',
            'value': 42.5,
            'unit': 'test_units',
            'category': 'test'
        }
        
        response = test_app.post('/api/analytics/metrics/record',
                               data=json.dumps(metric_data),
                               content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['recorded'] == True
    
    @pytest.mark.api
    @pytest.mark.analytics
    def test_record_custom_metric_missing_fields(self, test_app):
        """Test record custom metric endpoint with missing required fields"""
        incomplete_data = {
            'metric_type': 'test_metric',
            'value': 42.5
            # Missing unit
        }
        
        response = test_app.post('/api/analytics/metrics/record',
                               data=json.dumps(incomplete_data),
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Missing required field' in data['message']

class TestMainAPI:
    """Test main application API endpoints"""
    
    @pytest.mark.api
    def test_health_check_endpoint(self, test_app):
        """Test main health check endpoint"""
        response = test_app.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'service' in data['data']
        assert 'status' in data['data']
    
    @pytest.mark.api
    def test_tasks_endpoint(self, test_app):
        """Test tasks endpoint"""
        response = test_app.get('/api/tasks')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    @pytest.mark.api
    def test_tasks_stats_endpoint(self, test_app):
        """Test tasks stats endpoint"""
        response = test_app.get('/api/tasks/stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'total_tasks' in data['data']
        assert 'status_distribution' in data['data']
        assert 'priority_distribution' in data['data']
    
    @pytest.mark.api
    def test_poll_emails_endpoint(self, test_app):
        """Test poll emails endpoint"""
        response = test_app.post('/api/poll-emails')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'message' in data
    
    @pytest.mark.api
    @patch('app.email_service.get_access_token')
    def test_graph_auth_test_endpoint(self, mock_get_token, test_app):
        """Test graph auth test endpoint"""
        # Mock successful token acquisition
        mock_get_token.return_value = "mock_token_12345"
        
        response = test_app.post('/api/test/graph-auth')
        
        # Should return 200 with successful authentication
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'success'
    
    @pytest.mark.api
    def test_email_access_test_endpoint(self, test_app):
        """Test email access test endpoint"""
        response = test_app.post('/api/test/email-access')
        
        # This might return 401 if credentials are not properly configured
        assert response.status_code in [200, 401]
        data = json.loads(response.data)
        assert 'status' in data
    
    @pytest.mark.api
    def test_configuration_test_endpoint(self, test_app):
        """Test configuration test endpoint"""
        response = test_app.get('/api/test/configuration')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'environment_variables' in data['data']
        assert 'services' in data['data']

class TestWebPages:
    """Test web page endpoints"""
    
    @pytest.mark.e2e
    def test_home_page(self, test_app):
        """Test home page"""
        response = test_app.get('/')
        
        assert response.status_code == 200
        assert b'HandyConnect' in response.data
        assert b'Customer Support Task Manager' in response.data
    
    @pytest.mark.e2e
    def test_threads_page(self, test_app):
        """Test threads page"""
        response = test_app.get('/threads')
        
        assert response.status_code == 200
        assert b'Email Threads' in response.data
        assert b'Thread Statistics' in response.data
    
    @pytest.mark.e2e
    def test_analytics_page(self, test_app):
        """Test analytics page"""
        response = test_app.get('/analytics')
        
        assert response.status_code == 200
        assert b'Analytics Dashboard' in response.data
        assert b'Key Metrics' in response.data

class TestErrorHandling:
    """Test error handling"""
    
    @pytest.mark.api
    def test_invalid_date_format(self, test_app):
        """Test invalid date format handling"""
        params = {
            'start_date': 'invalid-date',
            'end_date': '2025-09-20'
        }
        
        response = test_app.get('/api/analytics/report', query_string=params)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Invalid date parameters' in data['message']
    
    @pytest.mark.api
    def test_missing_json_data(self, test_app):
        """Test missing JSON data handling"""
        response = test_app.post('/api/analytics/collect/task',
                               data='',
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'No data provided' in data['message']
    
    @pytest.mark.api
    def test_invalid_json_data(self, test_app):
        """Test invalid JSON data handling"""
        response = test_app.post('/api/analytics/collect/task',
                               data='invalid json',
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    @pytest.mark.api
    def test_nonexistent_endpoint(self, test_app):
        """Test nonexistent endpoint handling"""
        response = test_app.get('/api/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Analytics endpoint not found' in data['message']
    
    @pytest.mark.api
    def test_invalid_http_method(self, test_app):
        """Test invalid HTTP method handling"""
        response = test_app.put('/api/analytics/health')
        
        assert response.status_code == 405
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Method not allowed' in data['message']
