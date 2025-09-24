# HandyConnect API Reference

## Overview
The HandyConnect API provides endpoints for managing customer support tasks generated from email processing. The API follows RESTful conventions and returns JSON responses.

## Base URL
- Development: `http://localhost:5000`
- Production: `https://your-domain.com`

## Authentication
Currently, the API does not require authentication. In production, consider implementing API key authentication or OAuth2.

## Response Format
All API responses follow a consistent format:

### Success Response
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description",
  "details": "Additional error details (optional)"
}
```

## Endpoints

### Health Check
Check the health status of the API.

**GET** `/api/health`

**Response:**
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T10:00:00.000Z",
    "version": "1.0.0"
  }
}
```

### Get All Tasks
Retrieve all tasks with optional filtering.

**GET** `/api/tasks`

**Query Parameters:**
- `status` (optional): Filter by task status (`New`, `In Progress`, `Completed`)
- `category` (optional): Filter by task category
- `priority` (optional): Filter by priority (`Low`, `Medium`, `High`, `Urgent`)
- `assigned_to` (optional): Filter by assigned team member

**Example:**
```
GET /api/tasks?status=New&priority=High
```

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved 2 tasks",
  "data": [
    {
      "id": 1,
      "email_id": "email123",
      "subject": "Login Issues",
      "sender": "John Doe",
      "sender_email": "john@example.com",
      "content": "I cannot log into my account...",
      "summary": "Customer experiencing login problems",
      "category": "Technical Issue",
      "priority": "High",
      "status": "New",
      "created_at": "2024-01-01T10:00:00.000Z",
      "updated_at": "2024-01-01T10:00:00.000Z",
      "assigned_to": null,
      "notes": null,
      "sentiment": "Frustrated",
      "action_required": "Investigate login system"
    }
  ]
}
```

### Get Task by ID
Retrieve a specific task by its ID.

**GET** `/api/tasks/{task_id}`

**Path Parameters:**
- `task_id` (integer): The ID of the task to retrieve

**Response:**
```json
{
  "status": "success",
  "message": "Task retrieved successfully",
  "data": {
    "id": 1,
    "email_id": "email123",
    "subject": "Login Issues",
    "sender": "John Doe",
    "sender_email": "john@example.com",
    "content": "I cannot log into my account...",
    "summary": "Customer experiencing login problems",
    "category": "Technical Issue",
    "priority": "High",
    "status": "New",
    "created_at": "2024-01-01T10:00:00.000Z",
    "updated_at": "2024-01-01T10:00:00.000Z",
    "assigned_to": null,
    "notes": null,
    "sentiment": "Frustrated",
    "action_required": "Investigate login system"
  }
}
```

**Error Response (404):**
```json
{
  "status": "error",
  "message": "Task not found"
}
```

### Update Task
Update a specific task.

**PUT** `/api/tasks/{task_id}`

**Path Parameters:**
- `task_id` (integer): The ID of the task to update

**Request Body:**
```json
{
  "status": "In Progress",
  "priority": "High",
  "assigned_to": "Jane Smith",
  "notes": "Working on this issue",
  "category": "Technical Issue"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Task updated successfully. Fields updated: status, priority, assigned_to",
  "data": {
    "id": 1,
    "email_id": "email123",
    "subject": "Login Issues",
    "sender": "John Doe",
    "sender_email": "john@example.com",
    "content": "I cannot log into my account...",
    "summary": "Customer experiencing login problems",
    "category": "Technical Issue",
    "priority": "High",
    "status": "In Progress",
    "created_at": "2024-01-01T10:00:00.000Z",
    "updated_at": "2024-01-01T11:00:00.000Z",
    "assigned_to": "Jane Smith",
    "notes": "Working on this issue",
    "sentiment": "Frustrated",
    "action_required": "Investigate login system"
  }
}
```

### Delete Task
Delete a specific task.

**DELETE** `/api/tasks/{task_id}`

**Path Parameters:**
- `task_id` (integer): The ID of the task to delete

**Response:**
```json
{
  "status": "success",
  "message": "Task deleted successfully",
  "data": {
    "task_id": 1
  }
}
```

### Get Task Statistics
Retrieve task statistics for the dashboard.

**GET** `/api/tasks/stats`

**Response:**
```json
{
  "status": "success",
  "message": "Task statistics retrieved successfully",
  "data": {
    "total": 25,
    "new": 10,
    "in_progress": 8,
    "completed": 7,
    "high_priority": 5,
    "urgent_priority": 2,
    "categories": {
      "Technical Issue": 12,
      "Billing Question": 6,
      "Feature Request": 4,
      "General Inquiry": 3
    }
  }
}
```

### Poll Emails
Manually trigger email polling to process new emails.

**POST** `/api/poll-emails`

**Response:**
```json
{
  "status": "success",
  "message": "Processed 3 new emails",
  "data": {
    "processed_count": 3,
    "total_emails": 5,
    "errors": []
  }
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

## Rate Limiting
Currently, there are no rate limits implemented. Consider implementing rate limiting for production use.

## CORS
CORS is not configured by default. Add CORS headers if the API will be accessed from a different domain.

## Examples

### Using curl

**Get all tasks:**
```bash
curl -X GET "http://localhost:5000/api/tasks"
```

**Get tasks with filters:**
```bash
curl -X GET "http://localhost:5000/api/tasks?status=New&priority=High"
```

**Update a task:**
```bash
curl -X PUT "http://localhost:5000/api/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "In Progress", "assigned_to": "Jane Smith"}'
```

**Delete a task:**
```bash
curl -X DELETE "http://localhost:5000/api/tasks/1"
```

**Poll emails:**
```bash
curl -X POST "http://localhost:5000/api/poll-emails"
```

### Using Python requests

```python
import requests

# Get all tasks
response = requests.get('http://localhost:5000/api/tasks')
tasks = response.json()

# Update a task
update_data = {
    'status': 'In Progress',
    'assigned_to': 'Jane Smith'
}
response = requests.put(
    'http://localhost:5000/api/tasks/1',
    json=update_data
)

# Poll emails
response = requests.post('http://localhost:5000/api/poll-emails')
```

## Data Models

### Task Object
```json
{
  "id": 1,
  "email_id": "string",
  "subject": "string",
  "sender": "string",
  "sender_email": "string",
  "content": "string",
  "summary": "string",
  "category": "string",
  "priority": "Low|Medium|High|Urgent",
  "status": "New|In Progress|Completed",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime",
  "assigned_to": "string|null",
  "notes": "string|null",
  "sentiment": "Positive|Neutral|Negative|Frustrated",
  "action_required": "string"
}
```

### Task Statistics Object
```json
{
  "total": 0,
  "new": 0,
  "in_progress": 0,
  "completed": 0,
  "high_priority": 0,
  "urgent_priority": 0,
  "categories": {
    "category_name": 0
  }
}
```


