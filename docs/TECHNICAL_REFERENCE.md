# HandyConnect Technical Reference

## 🏗️ System Architecture

### **Core Components**

#### **1. Application Layer**
- **Main Application**: `app.py` - Flask application with modular architecture
- **Configuration**: Environment-based configuration management
- **Routing**: RESTful API endpoints with error handling

#### **2. Service Layer**
```
features/core_services/
├── case_service.py         # Case management and CRUD operations
├── task_service.py         # Task management and lifecycle
├── email_service.py        # Email processing and Microsoft Graph integration
├── llm_service.py          # AI/LLM integration with OpenAI
├── sla_service.py          # SLA tracking and compliance monitoring
├── workflow_service.py     # Workflow automation and rule engine
├── notification_service.py # Email notifications and alerts
├── cache_service.py        # Performance caching and optimization
└── performance_monitor.py  # System performance monitoring
```

#### **3. Data Models**
```
features/models/
├── base_models.py          # Base dataclasses and mixins
├── case_models.py          # Case, CustomerInfo, CaseMetadata, TimelineEvent
└── __init__.py             # Model exports
```

#### **4. API Layer**
```
features/case_management/
├── case_api.py             # Case CRUD and management endpoints
├── case_analytics.py       # Case analytics and reporting endpoints
└── __init__.py             # Blueprint exports
```

---

## 📊 Data Models

### **Case Model**
```python
@dataclass
class Case:
    case_id: str
    case_number: str
    case_title: str
    case_type: CaseType
    status: CaseStatus
    priority: CasePriority
    sentiment: str
    sla_due_date: Optional[datetime]
    sla_status: str
    assigned_to: Optional[str]
    assigned_team: str
    customer_info: Optional[CustomerInfo]
    case_metadata: Optional[CaseMetadata]
    threads: List[str]  # thread_ids
    tasks: List[int]    # task_ids
    timeline: List[TimelineEvent]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
```

### **Task Model**
```python
@dataclass
class Task:
    id: int
    case_id: Optional[str]  # Linked to case
    email_id: str
    thread_id: str
    subject: str
    content: str
    sender: str
    sender_email: str
    priority: str
    category: str
    status: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    summary: str
    sentiment: str
    action_required: str
```

### **Thread Model**
```python
@dataclass
class EmailThread:
    thread_id: str
    subject: str
    participants: List[str]
    emails: List[Dict]
    status: str
    priority: str
    category: str
    created_at: datetime
    updated_at: datetime
```

---

## 🔧 Service Architecture

### **CaseService**
```python
class CaseService:
    def __init__(self):
        self.data_file = 'data/cases.json'
        self.sla_service = SLAService()
        self.workflow_service = WorkflowService()
        self.notification_service = NotificationService()
        self.cache = get_case_cache()
        self.performance_monitor = get_performance_monitor()
    
    def load_cases(self) -> List[Dict]
    def save_cases(self, cases: List[Dict])
    def create_case(self, case_data: Dict) -> Dict
    def create_case_from_email(self, email: Dict, thread_id: str, llm_result: Dict) -> Dict
    def get_case_by_id(self, case_id: str) -> Optional[Dict]
    def update_case_status(self, case_id: str, status: str, actor: str) -> Optional[Dict]
    def assign_case(self, case_id: str, assigned_to: str, actor: str) -> Optional[Dict]
    def add_task_to_case(self, case_id: str, task_id: int, actor: str)
    def add_thread_to_case(self, case_id: str, thread_id: str, actor: str)
    def get_case_stats(self) -> Dict
    def search_cases(self, query: str) -> List[Dict]
    def get_advanced_case_analytics(self) -> Dict
```

### **SLAService**
```python
class SLAService:
    def __init__(self, config_file='data/sla_config.json'):
        self.sla_configs = self._load_sla_configs()
    
    def calculate_sla_metrics(self, case: Dict) -> Optional[SLAMetrics]
    def update_case_sla_status(self, case: Dict) -> Dict
    def get_sla_compliance_report(self, cases: List[Dict]) -> Dict
    def get_sla_trends(self, cases: List[Dict], period_days: int = 30) -> Dict
    def get_cases_at_risk(self, cases: List[Dict]) -> List[Dict]
    def get_cases_breached(self, cases: List[Dict]) -> List[Dict]
```

### **WorkflowService**
```python
class WorkflowService:
    def __init__(self, rules_file='data/workflow_rules.json'):
        self.workflow_rules = self._load_workflow_rules()
    
    def execute_workflow(self, case: Dict, trigger: WorkflowTrigger, trigger_data: Any = None)
    def add_workflow_rule(self, rule: Dict)
    def update_workflow_rule(self, rule_id: str, updates: Dict)
    def delete_workflow_rule(self, rule_id: str)
    def get_workflow_statistics(self) -> Dict
```

---

## 🌐 API Endpoints

### **Case Management APIs**
```python
# Case CRUD Operations
GET    /api/cases                    # List all cases
POST   /api/cases                    # Create new case
GET    /api/cases/{case_id}          # Get case by ID
PUT    /api/cases/{case_id}          # Update case
DELETE /api/cases/{case_id}          # Delete case

# Case Operations
PATCH  /api/cases/{case_id}/status   # Update case status
PATCH  /api/cases/{case_id}/assign   # Assign case
GET    /api/cases/number/{case_number} # Get case by number
GET    /api/cases/{case_id}/tasks    # Get case tasks
GET    /api/cases/{case_id}/timeline # Get case timeline

# Case Analytics
GET    /api/cases/analytics/dashboard    # Dashboard metrics
GET    /api/cases/analytics/trends       # Trend analysis
GET    /api/cases/analytics/performance  # Performance metrics
GET    /api/cases/analytics/reports      # Generate reports

# Case Search and Filtering
GET    /api/cases/search             # Search cases
GET    /api/cases/stats              # Case statistics

# Bulk Operations
PATCH  /api/cases/bulk/status        # Bulk status update
PATCH  /api/cases/bulk/assign        # Bulk assignment
```

### **Task Management APIs**
```python
# Task CRUD Operations
GET    /api/tasks                    # List all tasks
POST   /api/tasks                    # Create new task
GET    /api/tasks/{task_id}          # Get task by ID
PUT    /api/tasks/{task_id}          # Update task
DELETE /api/tasks/{task_id}          # Delete task

# Task Operations
PATCH  /api/tasks/{task_id}/status   # Update task status
PATCH  /api/tasks/{task_id}/assign   # Assign task
GET    /api/tasks/stats              # Task statistics
GET    /api/tasks/search             # Search tasks
```

### **Analytics APIs**
```python
# Analytics and Reporting
GET    /api/analytics/dashboard      # Dashboard metrics
GET    /api/analytics/trends         # Trend analysis
GET    /api/analytics/performance    # Performance metrics
GET    /api/analytics/reports        # Generate reports
```

---

## 🔄 Data Flow

### **Email Processing Pipeline**
```
1. Email Received (Microsoft Graph API)
   ↓
2. Thread Creation/Update (EmailThreadingService)
   ↓
3. LLM Analysis (LLMService)
   ↓
4. Case Creation/Linking (CaseService)
   ↓
5. Task Creation (TaskService)
   ↓
6. SLA Calculation (SLAService)
   ↓
7. Workflow Execution (WorkflowService)
   ↓
8. Notifications (NotificationService)
   ↓
9. Performance Monitoring (PerformanceMonitor)
```

### **Case Lifecycle**
```
New → In Progress → Awaiting Customer → Awaiting Vendor → Resolved → Closed
```

### **Task Lifecycle**
```
New → In Progress → Resolved → Closed
```

---

## 🎯 Performance Optimization

### **Caching Strategy**
```python
class CacheService:
    def __init__(self, max_size: int = 100, default_ttl: Optional[int] = 60):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: collections.OrderedDict[str, CacheEntry] = collections.OrderedDict()
    
    def get(self, key: str) -> Optional[Any]
    def set(self, key: str, value: Any, ttl: Optional[int] = None)
    def delete(self, key: str)
    def clear(self)
    def cleanup_expired_entries(self) -> int
```

### **Performance Monitoring**
```python
class PerformanceMonitor:
    def __init__(self, config: Optional[Dict] = None):
        self.metrics: List[PerformanceMetric] = []
        self.alerts: List[PerformanceAlert] = []
        self.config = config or {
            "response_time_threshold_ms": 1000,
            "memory_usage_threshold_percent": 80,
            "cpu_usage_threshold_percent": 90
        }
    
    def record_metric(self, component: str, operation: str, duration_ms: float, success: bool = True)
    def get_metrics_summary(self) -> Dict[str, Any]
    def get_component_performance(self) -> Dict[str, Any]
    def get_performance_trends(self, period_hours: int = 24) -> Dict[str, Any]
```

---

## 🔐 Security Considerations

### **Authentication & Authorization**
- Microsoft Graph API authentication
- API key management for OpenAI
- Environment variable security
- Input validation and sanitization

### **Data Protection**
- JSON data encryption at rest
- Secure API endpoints
- Error handling without information leakage
- Audit logging for all operations

---

## 🧪 Testing Architecture

### **Test Structure**
```
tests/
├── unit/                    # Unit tests for individual components
├── integration/            # Integration tests for service interactions
├── api/                    # API endpoint testing
├── performance/            # Performance and load testing
└── fixtures/               # Test data and fixtures
```

### **Test Coverage**
- **Unit Tests**: 100% coverage for core services
- **Integration Tests**: End-to-end testing
- **API Tests**: Complete endpoint testing
- **Performance Tests**: Load testing and benchmarking

---

## 📈 Monitoring & Observability

### **Health Checks**
- Application health endpoint
- Database connectivity checks
- External service availability
- Performance metrics collection

### **Logging**
- Structured logging with levels
- Request/response logging
- Error tracking and alerting
- Performance metrics logging

### **Metrics**
- Response time tracking
- Error rate monitoring
- Resource usage metrics
- Business metrics tracking

---

## 🚀 Deployment Architecture

### **Development**
```bash
python app.py
```

### **Production**
```bash
# Docker deployment
docker-compose up -d

# Or manual deployment
python app.py
```

### **Scaling Considerations**
- Horizontal scaling with load balancers
- Database optimization for high volume
- Caching strategy for performance
- Microservices architecture foundation

---

## 🔧 Configuration Management

### **Environment Variables**
```bash
# Required
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=your_tenant_id
OPENAI_API_KEY=your_openai_key
FLASK_SECRET_KEY=your_secret_key

# Optional
FLASK_ENV=production
LOG_LEVEL=INFO
CACHE_TTL=300
MAX_CACHE_SIZE=1000
```

### **Configuration Files**
- `data/sla_config.json` - SLA policies and thresholds
- `data/workflow_rules.json` - Workflow automation rules
- `data/notification_templates.json` - Email templates
- `config/` - Application configuration

---

This technical reference provides comprehensive information about the HandyConnect system architecture, data models, services, APIs, and deployment considerations.
