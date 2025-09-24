"""
HandyConnect Features Module

This module contains all functional components organized by feature area.
Each feature is designed to be modular and independently developable.

Feature Modules:
- outlook_email_api: Microsoft Graph API integration
- llm_prompt_design: Prompt engineering and evaluation
- task_structure_metadata: Task schema and metadata management
- email_response_automation: Automated email responses
- lightweight_ui: Performance-optimized UI components
- performance_reporting: Analytics and reporting
- case_id_generation: Unique ID generation strategies
"""

# Feature registry for dynamic loading
FEATURE_REGISTRY = {
    'outlook_email_api': {
        'module': 'features.outlook_email_api',
        'description': 'Microsoft Graph API integration for Outlook emails',
        'status': 'planned',
        'priority': 'high'
    },
    'llm_prompt_design': {
        'module': 'features.llm_prompt_design', 
        'description': 'Prompt engineering and evaluation framework',
        'status': 'planned',
        'priority': 'high'
    },
    'task_structure_metadata': {
        'module': 'features.task_structure_metadata',
        'description': 'Task schema and metadata management',
        'status': 'planned', 
        'priority': 'high'
    },
    'email_response_automation': {
        'module': 'features.email_response_automation',
        'description': 'Automated email response system',
        'status': 'planned',
        'priority': 'medium'
    },
    'lightweight_ui': {
        'module': 'features.lightweight_ui',
        'description': 'Performance-optimized UI components',
        'status': 'planned',
        'priority': 'medium'
    },
    'performance_reporting': {
        'module': 'features.performance_reporting',
        'description': 'Analytics and reporting capabilities',
        'status': 'planned',
        'priority': 'low'
    },
    'case_id_generation': {
        'module': 'features.case_id_generation',
        'description': 'Unique case ID generation strategies',
        'status': 'planned',
        'priority': 'low'
    }
}

def get_feature_info(feature_name):
    """Get information about a specific feature."""
    return FEATURE_REGISTRY.get(feature_name, None)

def list_features():
    """List all available features."""
    return list(FEATURE_REGISTRY.keys())

def get_features_by_priority(priority):
    """Get features filtered by priority level."""
    return {
        name: info for name, info in FEATURE_REGISTRY.items() 
        if info['priority'] == priority
    }

def get_features_by_status(status):
    """Get features filtered by development status."""
    return {
        name: info for name, info in FEATURE_REGISTRY.items() 
        if info['status'] == status
    }



