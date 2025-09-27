# HandyConnect - New Developer Setup Guide

**Welcome to HandyConnect, Swetha! 👋**

This guide will help you set up your development environment from scratch. Follow each step carefully, and don't hesitate to ask for help if you get stuck.

---

## 🎯 **What You'll Build**

HandyConnect is an AI-powered email support system that:
- Receives customer emails automatically
- Processes them using AI (OpenAI GPT)
- Creates support tasks and tracks them
- Provides analytics and reporting

---

## 📋 **Prerequisites**

Before starting, make sure you have:
- [ ] A computer with internet access
- [ ] A personal email address (Gmail, Outlook, etc.)
- [ ] Basic familiarity with command line/terminal
- [ ] Git installed on your computer

---

## 🛠️ **Phase 1: Environment Setup (30 minutes)**

### **Step 1.1: Install Required Software**

#### **Python 3.8+ (Required)**
```bash
# Check if Python is installed
python3 --version

# If not installed, download from: https://python.org/downloads/
```

#### **Git (Required)**
```bash
# Check if Git is installed
git --version

# If not installed, download from: https://git-scm.com/downloads
```

#### **Code Editor (Recommended: VS Code)**
- Download from: https://code.visualstudio.com/

### **Step 1.2: Clone the Repository**
```bash
# Clone the project
git clone <repository-url>
cd HandyConnect

# Create a new branch for your work
git checkout -b swetha-development
```

### **Step 1.3: Set Up Python Environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## ☁️ **Phase 2: Azure Setup (45 minutes)**

You'll need to create a fresh Azure account for email integration.

### **Step 2.1: Create Azure Account**
1. **Go to**: https://portal.azure.com
2. **Click**: "Create a free account"
3. **Use your personal email** (not work email)
4. **Complete**: Phone verification
5. **Note**: You may need a credit card for verification (won't be charged)

### **Step 2.2: Create Azure Active Directory Tenant**
1. **Search for**: "Microsoft Entra ID" in Azure Portal
2. **Click**: "Create a tenant"
3. **Choose**: "Azure Active Directory"
4. **Fill in**:
   - Organization name: `HandyConnect Development`
   - Initial domain: `handyconnectdev` (or similar)
   - Country: Your country
5. **Click**: "Review + create" → "Create"
6. **Wait**: 2-3 minutes for creation
7. **Switch**: to your new tenant (top-right corner)

### **Step 2.3: Create App Registration**
1. **Go to**: "App registrations" in your new tenant
2. **Click**: "+ New registration"
3. **Fill in**:
   - Name: `HandyConnect Email Integration`
   - Supported accounts: "Accounts in this organizational directory only"
   - Redirect URI: Leave blank
4. **Click**: "Register"
5. **Save these values** (you'll need them later):
   - Application (client) ID: `[COPY THIS]`
   - Directory (tenant) ID: `[COPY THIS]`

### **Step 2.4: Create Client Secret**
1. **Go to**: "Certificates & secrets"
2. **Click**: "+ New client secret"
3. **Fill in**:
   - Description: `Development Secret`
   - Expires: 24 months
4. **Click**: "Add"
5. **IMPORTANT**: Copy the **Value** immediately (you can't see it again!)
6. **Save**: Client Secret Value: `[COPY THIS]`

### **Step 2.5: Add API Permissions**
1. **Go to**: "API permissions"
2. **Click**: "+ Add a permission"
3. **Select**: "Microsoft Graph"
4. **Choose**: "Application permissions"
5. **Add these permissions**:
   - `Mail.Read`
   - `Mail.ReadWrite`
   - `User.Read.All`
6. **Click**: "Grant admin consent for [Your Organization]"
7. **Click**: "Yes" to confirm
8. **Verify**: All permissions show green checkmarks ✅

### **Step 2.6: Create Test User**
1. **Go to**: "Users" in Microsoft Entra ID
2. **Click**: "+ New user"
3. **Fill in**:
   - User name: `support`
   - Name: `Support Team`
   - Password: Auto-generate (save it!)
4. **Click**: "Create"
5. **Note**: Full email will be `support@handyconnectdev.onmicrosoft.com`

---

## 🔑 **Phase 3: OpenAI Setup (15 minutes)**

### **Step 3.1: Create OpenAI Account**
1. **Go to**: https://platform.openai.com
2. **Sign up**: with your personal email
3. **Verify**: your account

### **Step 3.2: Get API Key**
1. **Go to**: https://platform.openai.com/api-keys
2. **Click**: "Create new secret key"
3. **Name**: `HandyConnect Development`
4. **Copy**: the API key immediately
5. **Save**: OpenAI API Key: `[COPY THIS]`

### **Step 3.3: Add Credits (Optional)**
- **Free tier**: $5 credit for new accounts
- **For testing**: This should be sufficient
- **If needed**: Add $10-20 for extended development

---

## ⚙️ **Phase 4: Application Configuration (10 minutes)**

### **Step 4.1: Create Environment File**
```bash
# In the HandyConnect directory, create .env file
cp config/environment/env.example .env
```

### **Step 4.2: Update .env File**
Open `.env` file and update with your values:

```env
# Microsoft Graph API Configuration
CLIENT_ID=your-client-id-from-step-2.3
CLIENT_SECRET=your-client-secret-from-step-2.4
TENANT_ID=your-tenant-id-from-step-2.3
SCOPE=https://graph.microsoft.com/.default

# OpenAI Configuration
OPENAI_API_KEY=your-openai-key-from-step-3.2

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-make-it-random

# Data Storage Configuration
DATA_DIR=data
TASKS_FILE=data/tasks.json

# Email Configuration
POLL_INTERVAL_MINUTES=5
SUPPORT_EMAIL_FOLDER=Inbox
TARGET_USER_EMAIL=support@handyconnectdev.onmicrosoft.com
```

---

## 🚀 **Phase 5: First Run (10 minutes)**

### **Step 5.1: Test the Application**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the application
python app.py
```

### **Step 5.2: Verify Setup**
Open browser and go to: http://localhost:5001

You should see the HandyConnect interface.

### **Step 5.3: Test API Endpoints**
```bash
# In a new terminal, test these endpoints:

# Test configuration
curl http://localhost:5001/api/test/configuration

# Test authentication
curl -X POST http://localhost:5001/api/test/graph-auth

# Test email access
curl -X POST http://localhost:5001/api/test/email-access
```

---

## 📧 **Phase 6: Email Testing (15 minutes)**

### **Step 6.1: Send Test Email**
1. **From your personal email**, send an email to:
   - **To**: `support@handyconnectdev.onmicrosoft.com`
   - **Subject**: `Test Support Request`
   - **Body**: `Hello, I need help with my account. Please assist me.`

### **Step 6.2: Verify Email Processing**
```bash
# Wait 2-3 minutes after sending, then test:
curl -X POST http://localhost:5001/api/test/email-processing

# Check if task was created:
curl http://localhost:5001/api/tasks
```

---

## 🧪 **Phase 7: Run Tests (10 minutes)**

### **Step 7.1: Run Unit Tests**
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_app.py -v
python -m pytest tests/test_email_service.py -v
```

### **Step 7.2: Check Test Coverage**
```bash
# Generate test coverage report
coverage run -m pytest tests/
coverage report
coverage html
```

---

## 📁 **Phase 8: Understanding the Codebase**

### **Key Files to Review:**
- `app.py` - Main Flask application
- `email_service.py` - Email integration with Microsoft Graph
- `llm_service.py` - AI processing with OpenAI
- `task_service.py` - Task management
- `features/` - Feature modules (your focus area)

### **Your Development Areas:**
Based on the project roadmap, you'll be working on:
- **Phase 6**: Frontend UI components
- **Phase 7**: User authentication system
- **Phase 8**: Advanced email processing features

---

## 🔧 **Development Workflow**

### **Daily Workflow:**
1. **Pull latest changes**: `git pull origin main`
2. **Switch to your branch**: `git checkout swetha-development`
3. **Activate environment**: `source venv/bin/activate`
4. **Start development**: `python app.py`
5. **Run tests**: `python -m pytest tests/ -v`
6. **Commit changes**: `git add .` → `git commit -m "Description"`
7. **Push changes**: `git push origin swetha-development`

### **Before Committing:**
```bash
# Run linting
flake8 .

# Run tests
python -m pytest tests/ -v

# Check for security issues
bandit -r .
```

---

## 📚 **Helpful Resources**

### **Documentation:**
- **Project Docs**: `docs/` folder
- **API Reference**: `docs/api/API_REFERENCE.md`
- **Development Guide**: `docs/guides/DEVELOPER_SETUP.md`

### **External Resources:**
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Microsoft Graph API**: https://docs.microsoft.com/en-us/graph/
- **OpenAI API**: https://platform.openai.com/docs/
- **Python Testing**: https://docs.pytest.org/

---

## 🆘 **Getting Help**

### **If You Get Stuck:**
1. **Check the logs**: Look at terminal output for error messages
2. **Check documentation**: Review the `docs/` folder
3. **Search the codebase**: Use `grep` or VS Code search
4. **Ask the team**: Don't hesitate to reach out!

### **Common Issues:**
- **Port 5001 in use**: Kill existing processes or use different port
- **Azure permissions**: Check app registration permissions
- **Email not working**: Verify Azure user and permissions
- **OpenAI errors**: Check API key and credits

---

## ✅ **Setup Checklist**

Mark each item as you complete it:

**Environment Setup:**
- [ ] Python 3.8+ installed
- [ ] Git installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed

**Azure Setup:**
- [ ] Azure account created
- [ ] Azure AD tenant created
- [ ] App registration created
- [ ] Client secret generated
- [ ] API permissions added and consented
- [ ] Test user created

**OpenAI Setup:**
- [ ] OpenAI account created
- [ ] API key generated
- [ ] Credits available

**Application Setup:**
- [ ] .env file configured
- [ ] Application runs successfully
- [ ] API endpoints respond
- [ ] Tests pass

**Email Testing:**
- [ ] Test email sent
- [ ] Email processed successfully
- [ ] Task created from email

---

## 🎉 **Welcome to the Team!**

Congratulations on completing the setup! You're now ready to start developing HandyConnect features.

**Next Steps:**
1. **Review the codebase** to understand the architecture
2. **Check the project roadmap** in `docs/roadmaps/`
3. **Start working on your assigned phases**
4. **Set up regular check-ins** with the team

**Happy coding! 🚀**

---

*Last updated: September 2025*
*If you find any issues with this guide, please update it and help future developers!*

