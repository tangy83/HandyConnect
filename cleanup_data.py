#!/usr/bin/env python3
"""
Data Cleanup Script for HandyConnect
This script resets the application data to start fresh with only new incoming emails.
"""

import os
import json
import shutil
from datetime import datetime

def backup_existing_data():
    """Create a timestamped backup of current data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"data/backups/pre_cleanup_{timestamp}"
    
    os.makedirs(backup_dir, exist_ok=True)
    
    # Files to backup
    files_to_backup = [
        'cases.json',
        'tasks.json', 
        'notifications.json',
        'notification_templates.json',
        'sla_configurations.json',
        'workflow_executions.json',
        'workflow_rules.json'
    ]
    
    print(f"Creating backup in {backup_dir}...")
    
    for filename in files_to_backup:
        src_path = f"data/{filename}"
        if os.path.exists(src_path):
            dst_path = f"{backup_dir}/{filename}"
            shutil.copy2(src_path, dst_path)
            print(f"  ✓ Backed up {filename}")
    
    return backup_dir

def reset_cases_data():
    """Reset cases.json to empty array"""
    cases_file = "data/cases.json"
    
    with open(cases_file, 'w') as f:
        json.dump([], f, indent=2)
    
    print(f"✓ Reset {cases_file} to empty array")

def reset_tasks_data():
    """Reset tasks.json to empty array"""
    tasks_file = "data/tasks.json"
    
    with open(tasks_file, 'w') as f:
        json.dump([], f, indent=2)
    
    print(f"✓ Reset {tasks_file} to empty array")

def reset_notifications_data():
    """Reset notifications.json to empty array"""
    notifications_file = "data/notifications.json"
    
    with open(notifications_file, 'w') as f:
        json.dump([], f, indent=2)
    
    print(f"✓ Reset {notifications_file} to empty array")

def reset_workflow_executions():
    """Reset workflow_executions.json to empty array"""
    workflow_file = "data/workflow_executions.json"
    
    with open(workflow_file, 'w') as f:
        json.dump([], f, indent=2)
    
    print(f"✓ Reset {workflow_file} to empty array")

def reset_case_counter():
    """Reset case counter to 0"""
    counter_file = "data/case_counter.json"
    
    with open(counter_file, 'w') as f:
        json.dump({"counter": 0}, f, indent=2)
    
    print(f"✓ Reset {counter_file} to counter: 0")

def clean_analytics_data():
    """Clean up analytics data files"""
    analytics_dir = "data/analytics"
    
    if os.path.exists(analytics_dir):
        # Remove thread data
        threads_dir = f"{analytics_dir}/threads"
        if os.path.exists(threads_dir):
            shutil.rmtree(threads_dir)
            print("✓ Removed analytics/threads directory")
        
        # Clean other analytics subdirectories
        subdirs = ['backups', 'performance', 'system_health', 'tasks', 'user_behavior']
        for subdir in subdirs:
            subdir_path = f"{analytics_dir}/{subdir}"
            if os.path.exists(subdir_path):
                # Remove contents but keep directory
                for filename in os.listdir(subdir_path):
                    file_path = os.path.join(subdir_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                print(f"✓ Cleaned {subdir_path}")

def preserve_configuration_files():
    """Preserve important configuration files"""
    config_files = [
        'notification_templates.json',
        'sla_configurations.json', 
        'workflow_rules.json'
    ]
    
    print("\n📋 Configuration files preserved:")
    for config_file in config_files:
        if os.path.exists(f"data/{config_file}"):
            print(f"  ✓ {config_file} - kept for configuration")

def main():
    """Main cleanup function"""
    print("🧹 HandyConnect Data Cleanup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("data"):
        print("❌ Error: data directory not found. Run this script from the HandyConnect root directory.")
        return
    
    # Confirm cleanup
    print("\n⚠️  WARNING: This will reset all case and task data!")
    print("   - All existing cases will be removed")
    print("   - All existing tasks will be removed") 
    print("   - Analytics data will be cleaned")
    print("   - Configuration files will be preserved")
    print("   - A backup will be created before cleanup")
    
    confirm = input("\nAre you sure you want to proceed? (yes/no): ").lower().strip()
    
    if confirm != 'yes':
        print("❌ Cleanup cancelled.")
        return
    
    print("\n🔄 Starting cleanup process...")
    
    # Step 1: Create backup
    backup_dir = backup_existing_data()
    
    # Step 2: Reset data files
    print("\n📊 Resetting data files...")
    reset_cases_data()
    reset_tasks_data()
    reset_notifications_data()
    reset_workflow_executions()
    reset_case_counter()
    
    # Step 3: Clean analytics
    print("\n📈 Cleaning analytics data...")
    clean_analytics_data()
    
    # Step 4: Preserve configuration
    preserve_configuration_files()
    
    print("\n✅ Cleanup completed successfully!")
    print(f"📦 Backup created at: {backup_dir}")
    print("\n🎯 The application is now ready for fresh email processing.")
    print("   Only new incoming emails will be processed from now on.")

if __name__ == "__main__":
    main()
