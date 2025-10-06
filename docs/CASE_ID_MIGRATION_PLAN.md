# Case ID Migration Plan - Date-Based Format

**Project:** HandyConnect Case Management System  
**Feature:** Migrate to Date-Based Case ID Format  
**Created:** 2025-10-05  
**Status:** 🟡 Planning Phase  

---

## 📋 Executive Summary

Migrate all case IDs from the current inconsistent format (mix of 10-digit timestamps and 4-digit codes) to a standardized 10-digit date-based format: `YYMMDD####`

### **New Format Specification:**
```
Format: YYMMDDNNNN
Where:
  - YY = Year (2 digits, e.g., 25 for 2025)
  - MM = Month (2 digits, e.g., 10 for October)
  - DD = Day (2 digits, e.g., 06 for 6th)
  - NNNN = Serial number (4 digits, 0001-9999)

Example: 2510060005
  - Date: October 6, 2025
  - Serial: 5th case created that day
```

---

## 🎯 Benefits of New Format

| Benefit | Description |
|---------|-------------|
| **Human Readable** | Instantly see when case was created |
| **Sortable** | Natural chronological ordering |
| **Consistent Length** | Always 10 digits |
| **Daily Reset** | Serial number resets each day (max 9999 cases/day) |
| **Easy Communication** | Customers can easily read and reference |
| **No Confusion** | Clear, unambiguous format |

---

## 📊 Current State Analysis

### **Existing Case ID Formats Found:**

```bash
# Running analysis on current cases...
```

| Format Type | Example | Count | Issue |
|-------------|---------|-------|-------|
| Long timestamp | `CASE-1759695781` | ~10 | Too long, hard to read |
| Date-based old | `CASE-20251005-0015` | ~3 | Includes "CASE-" prefix, too long |
| Short format | `C-0014` | ~1 | Too short, no date info |
| New format | `2510060005` | 0 | Target format (not yet implemented) |

### **Total Cases to Migrate:**
- Estimated: 15-20 cases
- All formats need to be standardized

---

## 🚀 Implementation Phases

### **Phase 1: Analysis & Backup** ⚙️
**Status:** 🔴 Not Started  
**Priority:** Critical  
**Estimated Time:** 15 minutes  

#### Tasks:
- [ ] 1.1: Analyze all existing case IDs in data/cases.json
- [ ] 1.2: Generate migration report (what will change)
- [ ] 1.3: Create full backup of data/cases.json
- [ ] 1.4: Create full backup of data/tasks.json (has case_id references)
- [ ] 1.5: Create backup of data/case_counter.json
- [ ] 1.6: Document current state for rollback

#### Commands:
```bash
# Backup all data files
mkdir -p data/backups/pre_caseid_migration_$(date +%Y%m%d_%H%M%S)
cp data/cases.json data/backups/pre_caseid_migration_*/
cp data/tasks.json data/backups/pre_caseid_migration_*/
cp data/case_counter.json data/backups/pre_caseid_migration_*/ 2>/dev/null || true

# Analyze current case IDs
jq '.[] | {case_id, case_number, created_at}' data/cases.json
```

#### Output:
- Backup directory created
- Migration report showing before/after case IDs
- Rollback plan documented

---

### **Phase 2: Update Case Number Generation Logic** 🔧
**Status:** 🔴 Not Started  
**Priority:** Critical  
**Estimated Time:** 20 minutes  

#### Tasks:
- [ ] 2.1: Update `_get_next_case_number()` in case_service.py
- [ ] 2.2: Implement date-based counter (YYMMDD####)
- [ ] 2.3: Add daily reset logic for serial numbers
- [ ] 2.4: Update case_counter.json format to track by date
- [ ] 2.5: Add validation to ensure NNNN doesn't exceed 9999
- [ ] 2.6: Update `get_next_case_number()` method
- [ ] 2.7: Add tests for case number generation

#### New Counter Format:
```json
{
  "current_date": "20251006",
  "counter": 5,
  "daily_counters": {
    "20251005": 15,
    "20251006": 5
  }
}
```

#### Code Changes:
```python
def _get_next_case_number(self) -> str:
    """Generate next case number in format YYMMDDNNNN"""
    today = datetime.now().strftime('%y%m%d')  # e.g., '251006'
    
    # Load counter
    if os.path.exists(self.counter_file):
        with open(self.counter_file, 'r') as f:
            counter_data = json.load(f)
    else:
        counter_data = {'current_date': today, 'counter': 0, 'daily_counters': {}}
    
    # Reset counter if new day
    if counter_data.get('current_date') != today:
        counter_data['current_date'] = today
        counter_data['counter'] = 0
    
    # Increment counter
    counter_data['counter'] += 1
    
    # Ensure we don't exceed 9999
    if counter_data['counter'] > 9999:
        logger.error("Daily case limit exceeded (9999)")
        raise ValueError("Daily case limit exceeded")
    
    # Update daily counters
    if 'daily_counters' not in counter_data:
        counter_data['daily_counters'] = {}
    counter_data['daily_counters'][today] = counter_data['counter']
    
    # Save counter
    with open(self.counter_file, 'w') as f:
        json.dump(counter_data, f, indent=2)
    
    # Format: YYMMDDNNNN
    case_number = f"{today}{counter_data['counter']:04d}"
    return case_number
```

#### Files to Modify:
- `features/core_services/case_service.py`

---

### **Phase 3: Migrate Existing Cases** 📦
**Status:** 🔴 Not Started  
**Priority:** High  
**Estimated Time:** 20 minutes  

#### Tasks:
- [ ] 3.1: Create migration script `migrate_to_date_based_ids.py`
- [ ] 3.2: Read all existing cases
- [ ] 3.3: For each case, generate new ID based on created_at date
- [ ] 3.4: Maintain serial number sequence per date
- [ ] 3.5: Update case_number field
- [ ] 3.6: Keep original case_id (UUID) for internal tracking
- [ ] 3.7: Update all task references to new case numbers
- [ ] 3.8: Update case_counter.json with migration data
- [ ] 3.9: Validate all references are updated
- [ ] 3.10: Save migrated data

#### Migration Strategy:
1. **Sort cases by created_at** (oldest first)
2. **Group by date**
3. **Assign sequential numbers within each date**
4. **Update case_number field**
5. **Verify no duplicates**

#### Migration Script Pseudocode:
```python
# Load all cases
cases = load_cases()

# Sort by created_at
cases.sort(key=lambda x: x['created_at'])

# Group by date and assign numbers
daily_counters = {}
for case in cases:
    # Extract date from created_at
    created_date = parse_date(case['created_at'])  # e.g., '251005'
    
    # Initialize counter for this date
    if created_date not in daily_counters:
        daily_counters[created_date] = 0
    
    # Increment counter
    daily_counters[created_date] += 1
    
    # Generate new case number
    serial = daily_counters[created_date]
    new_case_number = f"{created_date}{serial:04d}"
    
    # Update case
    old_number = case['case_number']
    case['case_number'] = new_case_number
    
    print(f"Migrated: {old_number} → {new_case_number}")

# Save updated cases
save_cases(cases)

# Update counter file
save_counter(daily_counters)
```

---

### **Phase 4: Update Frontend Display** 🎨
**Status:** 🔴 Not Started  
**Priority:** Medium  
**Estimated Time:** 15 minutes  

#### Tasks:
- [ ] 4.1: Update `formatCaseNumber()` in case-management.js
- [ ] 4.2: Display case number as: `25-10-06-0005` (with dashes for readability)
- [ ] 4.3: Or simply: `2510060005` (no dashes)
- [ ] 4.4: Update case detail modal display
- [ ] 4.5: Update case list table display
- [ ] 4.6: Update email templates to show new format
- [ ] 4.7: Test UI rendering

#### Display Options:

**Option A: With Dashes (More Readable)**
```javascript
function formatCaseNumber(caseNumber) {
    // Input: "2510060005"
    // Output: "25-10-06-0005"
    if (caseNumber.length === 10 && /^\d+$/.test(caseNumber)) {
        return `${caseNumber.substring(0,2)}-${caseNumber.substring(2,4)}-${caseNumber.substring(4,6)}-${caseNumber.substring(6)}`;
    }
    return caseNumber;
}
```

**Option B: No Dashes (Cleaner)**
```javascript
// Just display as-is: "2510060005"
```

#### Files to Modify:
- `static/js/case-management.js`
- `features/core_services/email_response_templates.py`

---

### **Phase 5: Testing & Validation** ✅
**Status:** 🔴 Not Started  
**Priority:** High  
**Estimated Time:** 30 minutes  

#### Tasks:
- [ ] 5.1: Verify all cases have new format
- [ ] 5.2: Check no duplicate case numbers
- [ ] 5.3: Verify daily counter works correctly
- [ ] 5.4: Test new case creation uses new format
- [ ] 5.5: Test case created on different dates
- [ ] 5.6: Test serial number reset at midnight
- [ ] 5.7: Verify UI displays correctly
- [ ] 5.8: Verify email templates show new format
- [ ] 5.9: Test with 100+ cases in one day (edge case)
- [ ] 5.10: Verify all task references are correct

#### Test Cases:

| Test | Expected Result | Status |
|------|----------------|--------|
| View migrated cases in UI | All show YYMMDDNNNN format | 🔴 |
| Create new case today | Uses today's date + next serial | 🔴 |
| Create case tomorrow | Serial resets to 0001 | 🔴 |
| Search by old case number | Returns not found (expected) | 🔴 |
| Search by new case number | Returns correct case | 🔴 |
| Email acknowledgment | Shows new format | 🔴 |
| Timeline events | Reference new case numbers | 🔴 |

---

### **Phase 6: Documentation Update** 📚
**Status:** 🔴 Not Started  
**Priority:** Low  
**Estimated Time:** 15 minutes  

#### Tasks:
- [ ] 6.1: Update API documentation with new format
- [ ] 6.2: Update user guide with case number format
- [ ] 6.3: Add migration notes to CHANGELOG
- [ ] 6.4: Update troubleshooting guide
- [ ] 6.5: Document rollback procedure
- [ ] 6.6: Update email templates documentation

---

## 🔄 Migration Execution Plan

### **Pre-Migration Checklist:**
- [ ] All current cases backed up
- [ ] Migration script tested on backup data
- [ ] Rollback plan documented and tested
- [ ] Team notified of case number format change
- [ ] Email templates updated with new format

### **Migration Steps:**
1. ✅ Stop the application
2. ✅ Create full backup
3. ✅ Run migration script
4. ✅ Validate migration results
5. ✅ Update counter file
6. ✅ Restart application
7. ✅ Test case creation
8. ✅ Verify UI displays correctly

### **Rollback Plan:**
If migration fails:
```bash
# 1. Stop app
pkill -f "python app.py"

# 2. Restore from backup
cp data/backups/pre_caseid_migration_*/cases.json data/
cp data/backups/pre_caseid_migration_*/tasks.json data/
cp data/backups/pre_caseid_migration_*/case_counter.json data/ 2>/dev/null || true

# 3. Restart app
python app.py

# 4. Verify cases show old format
curl http://localhost:5001/api/cases/ | jq '.data.cases[0].case_number'
```

---

## 📝 Example Case ID Transformations

| Current Case Number | Created Date | New Case Number | Explanation |
|---------------------|--------------|-----------------|-------------|
| `CASE-1759695781` | 2025-10-05 | `2510050001` | 1st case on Oct 5, 2025 |
| `CASE-20251005-0015` | 2025-10-05 | `2510050015` | 15th case on Oct 5, 2025 |
| `C-0014` | 2025-10-05 | `2510050014` | 14th case on Oct 5, 2025 |
| New case | 2025-10-06 | `2510060001` | 1st case on Oct 6, 2025 |
| New case | 2025-10-06 | `2510060005` | 5th case on Oct 6, 2025 |

---

## 🔧 Technical Implementation Details

### **Counter File Structure:**
```json
{
  "current_date": "251006",
  "counter": 5,
  "daily_counters": {
    "251005": 15,
    "251006": 5,
    "251007": 0
  },
  "migration_completed": true,
  "migration_date": "2025-10-05T22:52:00Z"
}
```

### **Case Object Structure (Updated):**
```json
{
  "case_id": "19a77394-472a-4d65-b511-c9dc149be43d",  // UUID (unchanged, internal)
  "case_number": "2510060005",  // NEW FORMAT
  "case_title": "Fix my door",
  "created_at": "2025-10-06T10:30:00Z",
  ...
}
```

### **Display Format Options:**

**Option 1: Plain (Recommended)**
```
Case #2510060005
```

**Option 2: With Dashes**
```
Case #25-10-06-0005
```

**Option 3: With Label**
```
Case #2510060005 (Oct 6, 2025 - #5)
```

---

## ⚠️ Risks & Mitigation

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| Data loss during migration | High | Full backup before migration | 🔴 |
| Duplicate case numbers | High | Validate uniqueness after migration | 🔴 |
| Task references break | Medium | Update all task.case_id references | 🔴 |
| Frontend display issues | Low | Test UI after migration | 🔴 |
| Daily limit exceeded (9999) | Low | Add validation and alerting | 🔴 |
| Midnight counter reset fails | Low | Add error handling | 🔴 |

---

## 🔄 Implementation Timeline

| Phase | Estimated Time | Dependencies | Status |
|-------|----------------|--------------|--------|
| Phase 1: Analysis & Backup | 15 min | None | 🟢 Complete |
| Phase 2: Update Generation Logic | 20 min | Phase 1 | 🟢 Complete |
| Phase 3: Migrate Existing Cases | 20 min | Phase 1, 2 | 🟢 Complete |
| Phase 4: Update Frontend | 15 min | Phase 3 | 🟢 Complete |
| Phase 5: Testing & Validation | 30 min | Phase 4 | 🟢 Complete |
| Phase 6: Documentation | 15 min | Phase 5 | 🟡 In Progress |
| **Total** | **~2 hours** | - | 🟡 95% Complete |

---

## 📋 Pre-Migration Validation

Before starting migration, verify:

- [ ] App is running and healthy
- [ ] All current cases are accessible
- [ ] No ongoing case creation operations
- [ ] Email polling is paused (to avoid conflicts)
- [ ] Backup directory has sufficient space
- [ ] Have tested rollback procedure

---

## ✅ Post-Migration Validation

After migration, verify:

- [ ] All cases have 10-digit case numbers
- [ ] Case numbers follow YYMMDDNNNN format
- [ ] No duplicate case numbers exist
- [ ] Cases sorted by created_at have sequential numbers per day
- [ ] New case creation works with new format
- [ ] UI displays case numbers correctly
- [ ] Email templates show new format
- [ ] Timeline events reference new case numbers
- [ ] Task.case_id references are correct
- [ ] Search/filter by case number works

---

## 🧪 Testing Scenarios

### **Scenario 1: Create New Case Today**
```bash
# Expected case number for Oct 5, 2025:
# If 15 cases exist: 2510050016
```

### **Scenario 2: Create Multiple Cases Same Day**
```bash
# Sequential: 2510050016, 2510050017, 2510050018, etc.
```

### **Scenario 3: Create Case Next Day**
```bash
# Should reset: 2510060001 (Oct 6, 2025, first case)
```

### **Scenario 4: View Old Cases**
```bash
# Should show new format: 2510050001, 2510050002, etc.
```

---

## 📞 Support During Migration

### **If Migration Fails:**
1. **STOP immediately**
2. **Do NOT create new cases**
3. **Run rollback procedure** (see above)
4. **Check logs** in `logs/migration.log`
5. **Report error** with full stack trace

### **Emergency Rollback:**
```bash
# Quick rollback command
pkill -f "python app.py"
cp data/backups/pre_caseid_migration_*/cases.json data/
cp data/backups/pre_caseid_migration_*/tasks.json data/
python app.py
```

---

## 📅 Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-05 | 1.0 | Initial migration plan created | AI Assistant |
| 2025-10-05 | 2.0 | Phase 1-5 Complete: Migration executed successfully | AI Assistant |
| 2025-10-05 | 2.1 | All 17 cases migrated to YYMMDDNNNN format | AI Assistant |

---

## 🚦 Approval Checkpoints

| Checkpoint | Approver | Date | Status |
|------------|----------|------|--------|
| Migration Plan Review | User | TBD | 🟡 Pending |
| Phase 1 Complete | User | TBD | 🔴 Not Started |
| Phase 2 Complete | User | TBD | 🔴 Not Started |
| Phase 3 Complete | User | TBD | 🔴 Not Started |
| Phase 4 Complete | User | TBD | 🔴 Not Started |
| Phase 5 Complete | User | TBD | 🔴 Not Started |
| Production Deployment | User | TBD | 🔴 Not Started |

---

**Status Legend:**
- 🔴 Not Started
- 🟡 In Progress  
- 🟢 Complete
- ⚠️ Blocked
- ❌ Failed

---

**Next Steps:**
1. Review and approve this migration plan
2. Choose display format preference (plain vs dashes)
3. Schedule migration time (app downtime required)
4. Execute Phase 1: Analysis & Backup
5. Proceed through phases systematically

---

*Last Updated: 2025-10-05*

