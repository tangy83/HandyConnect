#!/usr/bin/env python3
"""
HandyConnect Setup Verification Script
This script checks if all required components are properly configured.
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - MISSING")
        return False

def check_env_var(var_name, description):
    """Check if environment variable is set"""
    if os.getenv(var_name):
        print(f"✅ {description}: {var_name} is set")
        return True
    else:
        print(f"❌ {description}: {var_name} - NOT SET")
        return False

def main():
    print("🔍 HandyConnect Setup Verification")
    print("=" * 50)
    
    all_good = True
    
    # Check core files
    print("\n📁 Core Files:")
    files_to_check = [
        ("app.py", "Main Flask application"),
        ("email_service.py", "Email service"),
        ("llm_service.py", "LLM service"),
        ("task_service.py", "Task service"),
        ("requirements.txt", "Python dependencies"),
    ]
    
    for filepath, desc in files_to_check:
        if not check_file_exists(filepath, desc):
            all_good = False
    
    # Check Docker files
    print("\n🐳 Docker Files:")
    docker_files = [
        ("Dockerfile", "Docker configuration"),
        ("docker-compose.yml", "Production Docker Compose"),
        ("docker-compose.dev.yml", "Development Docker Compose"),
        (".dockerignore", "Docker ignore file"),
        ("start.sh", "Startup script"),
    ]
    
    for filepath, desc in docker_files:
        if not check_file_exists(filepath, desc):
            all_good = False
    
    # Check template files
    print("\n🎨 Template Files:")
    template_files = [
        ("templates/base.html", "Base template"),
        ("templates/index.html", "Main template"),
        ("static/css/style.css", "CSS styles"),
        ("static/js/app.js", "JavaScript"),
    ]
    
    for filepath, desc in template_files:
        if not check_file_exists(filepath, desc):
            all_good = False
    
    # Check configuration
    print("\n⚙️  Configuration:")
    config_files = [
        ("env.example", "Environment template"),
        (".gitignore", "Git ignore file"),
        ("README.md", "Documentation"),
        ("Makefile", "Build automation"),
    ]
    
    for filepath, desc in config_files:
        if not check_file_exists(filepath, desc):
            all_good = False
    
    # Check environment variables (if .env exists)
    print("\n🔐 Environment Variables:")
    if Path(".env").exists():
        from dotenv import load_dotenv
        load_dotenv()
        
        env_vars = [
            ("CLIENT_ID", "Azure Client ID"),
            ("CLIENT_SECRET", "Azure Client Secret"),
            ("TENANT_ID", "Azure Tenant ID"),
            ("OPENAI_API_KEY", "OpenAI API Key"),
            ("SECRET_KEY", "Flask Secret Key"),
        ]
        
        for var_name, desc in env_vars:
            if not check_env_var(var_name, desc):
                all_good = False
    else:
        print("⚠️  .env file not found - copy env.example to .env and configure")
        all_good = False
    
    # Check directories
    print("\n📂 Directories:")
    directories = ["templates", "static", "static/css", "static/js"]
    for directory in directories:
        if Path(directory).exists():
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")
            all_good = False
    
    # Final status
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All checks passed! HandyConnect is ready to run.")
        print("\n🚀 Next steps:")
        print("1. Configure your .env file with actual credentials")
        print("2. Run: make setup")
        print("3. Run: make dev (for development)")
        print("4. Or run: make run (for production)")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
