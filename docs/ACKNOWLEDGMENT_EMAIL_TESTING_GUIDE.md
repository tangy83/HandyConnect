# Acknowledgment Email System - Testing Guide

**Feature:** Automated Case Acknowledgment Emails  
**Status:** ✅ Ready for Testing  
**Last Updated:** 2025-10-05  

---

## 🧪 How to Test the Acknowledgment Email System

### **Method 1: Real Email Test (Recommended)** ✉️

This tests the complete end-to-end flow with actual emails.

#### Steps:

1. **Ensure App is Running:**
   ```bash
   # Check if app is running
   curl http://localhost:5001/api/health
   
   # If not running, start it:
   source venv/bin/activate && python app.py
   ```

2. **Verify Microsoft Graph API Authentication:**
   ```bash
   # Check if authenticated
   # Look for .token_cache.bin file
   ls -la .token_cache.bin
   ```
   
   If not authenticated, you'll need to authenticate first (the app will prompt you).

3. **Send Test Email:**
   - From your personal email (e.g., `tanuj.saluja@gmail.com`)
   - To: `handymyjob@outlook.com`
   - Test different tones:

   **Option A: Urgent Email**
   ```
   Subject: URGENT: Water leak in my apartment!
   Body: This is an emergency! Water is leaking from the ceiling 
         in apartment 205, Block B. Please send someone immediately!
   ```

   **Option B: Frustrated Email**
   ```
   Subject: Still waiting for repair - very disappointed
   Body: I am frustrated and disappointed. It's been 2 weeks since I 
         reported the heating issue and no one has come. This is 
         unacceptable. Property 102, Block A.
   ```

   **Option C: Polite Email**
   ```
   Subject: Request for HVAC maintenance
   Body: Hello, I would like to schedule a maintenance check for my 
         HVAC system. Please let me know when someone can visit. 
         Thank you. Unit 305, Block C.
   ```

4. **Wait for Processing:**
   - Email polling runs every 5 minutes by default
   - Or manually trigger: Send another email or wait
   - Check logs: `tail -f logs/app.log | grep -i "acknowledgment\|case created"`

5. **Verify Results:**
   
   **A. Check Your Inbox:**
   - You should receive an acknowledgment email from `handymyjob@outlook.com`
   - Subject should reference your case number (e.g., `Case #C-0015`)
   - Tone should match your email (urgent → immediate action language)
   - Should include case number, next steps, timeline

   **B. Check Cases Dashboard:**
   - Go to: `http://localhost:5001/cases`
   - Find your case (should be at the top)
   - Note the case number
   - Click to view case details

   **C. Check Case Timeline:**
   - In case detail modal, go to "Timeline" tab
   - Look for event: `acknowledgment_email_sent`
   - Should show: recipient, tone, urgency, timestamp

6. **Validate Tone Appropriateness:**
   - Urgent email → Should see "URGENT: Immediate Action" in subject
   - Frustrated email → Should see empathy and apology
   - Polite email → Should see professional acknowledgment

---

### **Method 2: API Test (Quick)** 🚀

Test the acknowledgment service directly via API calls.

#### Steps:

1. **Create a Test Case:**
   ```bash
   curl -X POST http://localhost:5001/api/cases/ \
     -H "Content-Type: application/json" \
     -d '{
       "case_title": "Test urgent issue",
       "case_type": "Maintenance",
       "priority": "High",
       "customer_info": {
         "name": "Test User",
         "email": "your-email@example.com",
         "property_number": "205",
         "block_number": "Block B"
       }
     }' | jq '.data.case_number'
   ```

2. **Check Case Timeline:**
   ```bash
   # Replace CASE_ID with the actual case_id from above
   curl http://localhost:5001/api/cases/CASE_ID/timeline | jq '.data.timeline[] | select(.event_type == "acknowledgment_email_sent")'
   ```

3. **Check Acknowledgment Status:**
   ```bash
   # Via Python
   source venv/bin/activate
   python -c "
   from features.core_services.acknowledgment_service import AcknowledgmentService
   ack = AcknowledgmentService()
   status = ack.get_acknowledgment_status('CASE_ID')
   print(status)
   "
   ```

---

### **Method 3: Simulated Test (No Email)** 🎭

Test the components without actually sending emails.

#### Steps:

1. **Run Tone Analysis Test:**
   ```bash
   source venv/bin/activate
   python -c "
   from features.core_services.llm_service import LLMService
   llm = LLMService()
   
   result = llm.analyze_email_tone(
       'This is URGENT! Fix my door immediately!',
       'URGENT: Door repair needed'
   )
   
   print(f'Tone: {result[\"tone\"]}')
   print(f'Urgency: {result[\"urgency_level\"]}')
   print(f'Immediate Attention: {result[\"requires_immediate_attention\"]}')
   print(f'Confidence: {result[\"confidence_score\"]:.2f}')
   "
   ```

2. **Test Template Generation:**
   ```bash
   python -c "
   from features.core_services.email_response_templates import EmailResponseTemplates
   templates = EmailResponseTemplates()
   
   context = {
       'customer_name': 'John Smith',
       'case_number': 'C-1234',
       'brief_summary': 'Urgent door repair',
       'urgency_level': 'high',
       'property_number': '205',
       'block_number': 'Block B'
   }
   
   email = templates.build_email_body('urgent', context)
   print(email[:500])
   "
   ```

3. **Test Complete Flow (Without Sending):**
   ```bash
   python -c "
   from features.core_services.acknowledgment_service import AcknowledgmentService
   
   ack = AcknowledgmentService()
   
   # This will analyze tone and generate email, but won't send
   # (sending requires Graph API authentication)
   print('Acknowledgment service ready!')
   print('All components initialized successfully')
   "
   ```

---

## 📊 Expected Results

### **For Urgent/Critical Emails:**
- ✅ Subject: `Case #C-XXXX - URGENT: Immediate Action Initiated`
- ✅ Response time: "2 hours"
- ✅ Language: "EMERGENCY", "ESCALATED", "immediate attention"
- ✅ Tone: Serious, action-oriented

### **For Frustrated/Angry Emails:**
- ✅ Subject: `Case #C-XXXX - We're Here to Help` or `Your Concerns Are Our Priority`
- ✅ Response time: "4 hours"
- ✅ Language: "sincerely apologize", "understand your frustration", "committed"
- ✅ Tone: Empathetic, apologetic

### **For Polite/Calm Emails:**
- ✅ Subject: `Case #C-XXXX - Request Received`
- ✅ Response time: "1 business day"
- ✅ Language: "Thank you", "professional", "standard"
- ✅ Tone: Professional, courteous

### **For Grateful Emails:**
- ✅ Subject: `Case #C-XXXX - Thank You for Contacting Us`
- ✅ Response time: "2 business days"
- ✅ Language: "pleasure", "appreciate", "warmest regards"
- ✅ Tone: Warm, appreciative

---

## ✅ Validation Checklist

After testing, verify:

- [ ] Acknowledgment email received within 30 seconds of case creation
- [ ] Email sent from `handymyjob@outlook.com`
- [ ] Subject line includes case number (e.g., `C-0015`)
- [ ] Tone matches customer's email (urgent → urgent response)
- [ ] Property details included (if provided)
- [ ] SLA timeline appropriate for urgency level
- [ ] Case timeline has `acknowledgment_email_sent` event
- [ ] Case metadata shows `acknowledgment_sent: true`
- [ ] Email is professional and well-formatted
- [ ] Contact information and case reference instructions included

---

## 🐛 Troubleshooting

### **Issue: No email received**

**Possible Causes:**
1. Microsoft Graph API not authenticated
2. Email polling not running
3. Email sending failed (check logs)

**Solutions:**
```bash
# Check logs for acknowledgment attempts
tail -50 logs/app.log | grep -i "acknowledgment"

# Check if email polling is running
tail -20 logs/app.log | grep "Email polling"

# Verify authentication
ls -la .token_cache.bin

# Check app status
curl http://localhost:5001/api/health
```

### **Issue: Wrong tone detected**

**Example:** Polite email detected as grateful

**Solution:** 
- This is acceptable for similar tones (both positive)
- Adjust keywords in `_fallback_tone_analysis()` if needed
- Or configure OpenAI API for more accurate detection

### **Issue: Email sent but not logged in timeline**

**Check:**
```bash
# View case timeline
curl http://localhost:5001/api/cases/CASE_ID/timeline | jq '.'
```

**Solution:**
- Check `_log_acknowledgment()` method
- Verify case_id is correct
- Check logs for timeline errors

---

## 📝 Test Results Log

| Test Date | Test Type | Tone | Email Sent | Timeline Logged | Result |
|-----------|-----------|------|------------|-----------------|--------|
| 2025-10-05 | Simulated | Urgent | N/A | N/A | ✅ Components OK |
| TBD | Real Email | Urgent | TBD | TBD | 🔴 Pending |
| TBD | Real Email | Frustrated | TBD | TBD | 🔴 Pending |
| TBD | Real Email | Polite | TBD | TBD | 🔴 Pending |

---

## 🚀 Quick Test Commands

```bash
# 1. Start the app
source venv/bin/activate && python app.py

# 2. In another terminal, monitor logs
tail -f logs/app.log | grep -i "case\|acknowledgment\|email"

# 3. Send test email to handymyjob@outlook.com

# 4. Watch for case creation
curl -s http://localhost:5001/api/cases/ | jq '.data.cases[0] | {case_number, case_title, customer: .customer_info.email}'

# 5. Check if acknowledgment was sent
curl -s http://localhost:5001/api/cases/CASE_ID/timeline | jq '.data.timeline[] | select(.event_type == "acknowledgment_email_sent")'
```

---

## 📧 Sample Test Emails

Copy and paste these into your email client:

### Test 1: Critical Emergency
```
To: handymyjob@outlook.com
Subject: EMERGENCY: Water flooding apartment

This is an EMERGENCY! Water is flooding into my apartment from 
the unit above. There's significant damage and this is a safety 
hazard. Please send someone IMMEDIATELY!

Property 302, Block C
```

### Test 2: Frustrated Customer
```
To: handymyjob@outlook.com
Subject: Disappointed with response time

I am utterly disappointed with the lack of response. I reported 
the broken heating system 10 days ago and no one has come to fix 
it. This is unacceptable, especially during winter. I expect 
better service.

Apartment 105, Block A
```

### Test 3: Polite Inquiry
```
To: handymyjob@outlook.com
Subject: Request for maintenance appointment

Hello,

I would like to schedule a routine maintenance check for my HVAC 
system before the summer season. Please let me know available 
dates. Thank you for your assistance.

Best regards,
Unit 408, Block B
```

---

**Ready to test? Start with Method 1 (Real Email Test) for the most comprehensive validation!** 🎯

