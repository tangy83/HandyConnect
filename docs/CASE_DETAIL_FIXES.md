# Case Detail Modal - Issue Fixes

**Case:** 2510050018 (Anika's email)  
**Created:** 2025-10-05  
**Status:** 🔴 Issues Identified  

---

## 🐛 Issues Found

### **Issue 1: Tasks not showing (says 4 tasks but nothing listed)**
**Root Cause:** Case references task IDs (30, 31, 32) that don't exist in tasks.json  
**Impact:** High - Users can't see linked tasks  
**Fix:** 
- Option A: Remove invalid task IDs from case
- Option B: Create the missing tasks
- Option C: Fix task creation logic to ensure tasks are always created

### **Issue 2: Overview tab not necessary**
**Root Cause:** Redundant tab in case detail modal  
**Impact:** Low - UI cluttered  
**Fix:** Remove Overview tab from case detail modal

### **Issue 3: Original email not visible in Threads section**
**Root Cause:** Thread data not properly linked or displayed  
**Impact:** High - Users can't see communication history  
**Fix:** Ensure original email content loads in Threads tab

---

## 🔧 Fixes to Implement

### **Fix 1: Remove Invalid Task References**
```bash
# Clean up case task references
jq '(.[] | select(.case_number == "2510050018") | .tasks) = []' data/cases.json > temp.json && mv temp.json data/cases.json
```

### **Fix 2: Remove Overview Tab**
File: `templates/cases.html`
- Remove the Overview tab button
- Remove the Overview tab content pane
- Set Tasks or Threads as default active tab

### **Fix 3: Load Original Email in Threads**
File: `static/js/case-management.js`
- Fix `loadCaseThreads()` function
- Ensure it fetches actual thread data
- Display email content, sender, timestamp

---

**Priority Order:**
1. Fix 3 (Threads not showing) - HIGH
2. Fix 1 (Invalid task references) - HIGH  
3. Fix 2 (Remove Overview tab) - MEDIUM

