import openai
import os
import json
import re
from .category_tree import property_categories

class LLMService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not found. AI features will use fallback responses.")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=api_key)
    
    def analyze_email_tone(self, email_content: str, email_subject: str = "") -> dict:
        """
        Analyze the tone and urgency of customer email for appropriate response generation.
        
        Returns detailed tone analysis including:
        - tone: primary emotional tone (urgent, frustrated, angry, calm, polite, confused, grateful)
        - urgency_level: critical, high, medium, low
        - emotional_indicators: list of detected emotional keywords
        - requires_immediate_attention: boolean
        - confidence_score: 0.0-1.0
        """
        try:
            if not self.client:
                return self._fallback_tone_analysis(email_content, email_subject)
            
            full_content = f"Subject: {email_subject}\n\n{email_content}"
            
            prompt = f"""
            Analyze the tone and urgency of this customer email for a property management system.
            
            Email:
            {full_content}
            
            Provide a detailed tone analysis in JSON format:
            {{
                "tone": "One of: urgent, frustrated, angry, calm, polite, confused, grateful, concerned",
                "urgency_level": "One of: critical, high, medium, low",
                "emotional_indicators": ["list", "of", "detected", "emotional", "keywords"],
                "requires_immediate_attention": true/false,
                "confidence_score": 0.85,
                "empathy_required": true/false,
                "response_priority": "immediate/high/standard",
                "tone_explanation": "Brief explanation of why this tone was detected"
            }}
            
            Guidelines for tone detection:
            - CRITICAL/URGENT: Safety issues, emergencies, words like "emergency", "urgent", "immediately", "ASAP", "critical", "dangerous"
            - FRUSTRATED: "disappointed", "unacceptable", "still waiting", "fed up", "frustrated", multiple exclamation marks
            - ANGRY: "appalled", "outraged", "unbelievable", "complaint", "disgusted", ALL CAPS words
            - CALM: Neutral language, "please", "would like", "requesting", "kindly"
            - POLITE: "thank you", "appreciate", "grateful", "please", courteous language
            - CONFUSED: "not sure", "unclear", "don't understand", "help", questions
            - GRATEFUL: "thank you", "appreciate", "great service", positive feedback
            - CONCERNED: Worry indicators, "worried", "concerned", "anxious"
            
            Urgency levels:
            - CRITICAL: Safety hazards, emergencies, security breaches
            - HIGH: Urgent repairs, service interruptions, time-sensitive issues
            - MEDIUM: Standard maintenance, non-urgent repairs
            - LOW: General inquiries, information requests
            
            Return confidence_score based on clarity of emotional indicators (0.0-1.0).
            Set requires_immediate_attention to true for critical/urgent cases.
            Set empathy_required to true for negative tones (frustrated, angry, concerned).
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in emotional intelligence and customer communication analysis. Analyze customer emails to determine appropriate response tone and urgency."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.2  # Lower temperature for more consistent analysis
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                
                # Validate and set defaults
                return {
                    'tone': result.get('tone', 'calm'),
                    'urgency_level': result.get('urgency_level', 'medium'),
                    'emotional_indicators': result.get('emotional_indicators', []),
                    'requires_immediate_attention': result.get('requires_immediate_attention', False),
                    'confidence_score': float(result.get('confidence_score', 0.7)),
                    'empathy_required': result.get('empathy_required', False),
                    'response_priority': result.get('response_priority', 'standard'),
                    'tone_explanation': result.get('tone_explanation', 'Standard communication detected')
                }
            else:
                return self._fallback_tone_analysis(email_content, email_subject)
                
        except Exception as e:
            print(f"Error analyzing email tone with LLM: {e}")
            return self._fallback_tone_analysis(email_content, email_subject)
    
    def _fallback_tone_analysis(self, email_content: str, email_subject: str = "") -> dict:
        """
        Fallback tone analysis using keyword matching when LLM is unavailable.
        """
        full_text = f"{email_subject} {email_content}".lower()
        
        # Define keyword patterns for different tones
        urgent_keywords = ['urgent', 'emergency', 'immediately', 'asap', 'critical', 'dangerous', 'safety', 'hazard']
        frustrated_keywords = ['disappointed', 'unacceptable', 'still waiting', 'fed up', 'frustrated', 'weeks', 'months']
        angry_keywords = ['appalled', 'outraged', 'unbelievable', 'complaint', 'disgusted', 'terrible', 'worst']
        polite_keywords = ['please', 'thank you', 'appreciate', 'grateful', 'kindly']
        confused_keywords = ['not sure', 'unclear', 'confused', "don't understand", 'help', 'how do']
        grateful_keywords = ['thank you', 'thanks', 'appreciate', 'grateful', 'excellent', 'great service']
        
        # Count matches
        emotional_indicators = []
        tone = 'calm'
        urgency_level = 'medium'
        requires_immediate_attention = False
        empathy_required = False
        
        # Check for urgent/critical
        urgent_matches = [kw for kw in urgent_keywords if kw in full_text]
        if urgent_matches:
            emotional_indicators.extend(urgent_matches)
            tone = 'urgent'
            urgency_level = 'critical' if any(kw in ['emergency', 'dangerous', 'critical'] for kw in urgent_matches) else 'high'
            requires_immediate_attention = True
        
        # Check for frustrated
        frustrated_matches = [kw for kw in frustrated_keywords if kw in full_text]
        if frustrated_matches and tone == 'calm':
            emotional_indicators.extend(frustrated_matches)
            tone = 'frustrated'
            urgency_level = 'high'
            empathy_required = True
        
        # Check for angry
        angry_matches = [kw for kw in angry_keywords if kw in full_text]
        if angry_matches:
            emotional_indicators.extend(angry_matches)
            tone = 'angry'
            urgency_level = 'high'
            requires_immediate_attention = True
            empathy_required = True
        
        # Check for grateful
        grateful_matches = [kw for kw in grateful_keywords if kw in full_text]
        if grateful_matches and tone == 'calm':
            emotional_indicators.extend(grateful_matches)
            tone = 'grateful'
            urgency_level = 'low'
        
        # Check for confused
        confused_matches = [kw for kw in confused_keywords if kw in full_text]
        if confused_matches and tone == 'calm':
            emotional_indicators.extend(confused_matches)
            tone = 'confused'
            urgency_level = 'medium'
        
        # Check for polite
        polite_matches = [kw for kw in polite_keywords if kw in full_text]
        if polite_matches and tone == 'calm':
            emotional_indicators.extend(polite_matches[:2])  # Limit to avoid too many
            tone = 'polite'
        
        # Determine response priority
        if urgency_level == 'critical':
            response_priority = 'immediate'
        elif urgency_level == 'high':
            response_priority = 'high'
        else:
            response_priority = 'standard'
        
        # Calculate confidence score based on number of matches
        confidence_score = min(0.9, 0.5 + (len(emotional_indicators) * 0.1))
        
        return {
            'tone': tone,
            'urgency_level': urgency_level,
            'emotional_indicators': list(set(emotional_indicators))[:5],  # Limit to 5 unique indicators
            'requires_immediate_attention': requires_immediate_attention,
            'confidence_score': confidence_score,
            'empathy_required': empathy_required,
            'response_priority': response_priority,
            'tone_explanation': f'Detected {tone} tone based on keyword analysis'
        }
        
    def process_email(self, email):
        """Process email content using OpenAI to extract summary, category, and priority"""
        try:
            # Prepare the email content for analysis
            email_content = f"""
            Subject: {email.get('subject', '')}
            From: {email.get('sender', {}).get('name', '')} ({email.get('sender', {}).get('email', '')})
            Content: {email.get('body', '')}
            """
            
            # Get all available categories for the prompt
            all_categories = property_categories.get_all_leaf_categories()
            category_list = ", ".join(all_categories[:20])  # Limit to first 20 for prompt length
            
            # Create a prompt for the LLM
            prompt = f"""
            Analyze the following property management email and extract key information:
            
            {email_content}
            
            Please provide a JSON response with the following structure:
            {{
                "summary": "A concise summary of the customer's issue or request (max 200 words)",
                "category": "One of: {category_list}",
                "priority": "One of: Low, Medium, High, Urgent",
                "sentiment": "One of: Positive, Neutral, Negative, Frustrated",
                "action_required": "Brief description of what action needs to be taken",
                "property_number": "Extract property number if mentioned (e.g., 'Apt 205', 'Unit 12', 'Property 45') or null",
                "block_number": "Extract block number if mentioned (e.g., 'Block A', 'Block 3', 'Building B') or null",
                "property_address": "Extract any specific property address details mentioned or null"
            }}
            
            Guidelines:
            - This is a PROPERTY MANAGEMENT system, so focus on property-related issues
            - Priority should be High for urgent maintenance, safety, or security issues
            - Priority should be Urgent for emergencies, safety hazards, or security breaches
            - Category should be the most specific category that matches the issue
            - Common categories include: Plumbing, Electrical, HVAC, Structural, Maintenance & Repairs, Utilities, Billing & Accounts, Amenities & Services, Safety & Security, Neighbour Relations, Cleaning & Waste, Requests & Inquiries
            - Summary should capture the essence of what the customer is asking for
            - Be concise but informative
            - IMPORTANT: Extract property_number and block_number from text like "Apt 205", "Unit 12", "Block A", "Building 3", etc.
            - Look for patterns like: "apartment/unit/property/house [number]", "block/building [letter/number]"
            - Return null if not mentioned explicitly
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert customer support analyst. Analyze emails and extract structured information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Extract JSON from response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Validate and clean the result
                category = result.get('category', 'Miscellaneous')
                
                # Validate category against our tree
                if category not in property_categories.categories:
                    # Try to find best match
                    category, _ = property_categories.find_best_category(email_content)
                
                return {
                    'summary': result.get('summary', 'No summary available'),
                    'category': category,
                    'priority': result.get('priority', 'Medium'),
                    'sentiment': result.get('sentiment', 'Neutral'),
                    'action_required': result.get('action_required', 'Review and respond'),
                    'property_number': result.get('property_number'),
                    'block_number': result.get('block_number'),
                    'property_address': result.get('property_address')
                }
            else:
                # Fallback if JSON parsing fails
                category, _ = property_categories.find_best_category(email_content)
                return {
                    'summary': content[:200] + '...' if len(content) > 200 else content,
                    'category': category,
                    'priority': 'Medium',
                    'sentiment': 'Neutral',
                    'action_required': 'Review and respond',
                    'property_number': None,
                    'block_number': None,
                    'property_address': None
                }
                
        except Exception as e:
            print(f"Error processing email with LLM: {e}")
            # Return default values if LLM processing fails
            email_content = f"{email.get('subject', '')} {email.get('body', '')}"
            category, _ = property_categories.find_best_category(email_content)
            return {
                'summary': f"Email from {email.get('sender', {}).get('name', 'Unknown')}: {email.get('subject', 'No Subject')}",
                'category': category,
                'priority': 'Medium',
                'sentiment': 'Neutral',
                'action_required': 'Review and respond',
                'property_number': None,
                'block_number': None,
                'property_address': None
            }
    
    def generate_case_summary(self, case_context: str) -> str:
        """Generate AI-powered case summary with 3 actionable points"""
        try:
            if not self.client:
                return self._generate_fallback_summary(case_context)
                
            prompt = f"""
            Analyze the following case information and generate a comprehensive summary:
            
            {case_context}
            
            Please provide:
            1. A 2-3 sentence overview that captures:
               - The core issue or request from the sender
               - Property details (property number, block number) if available
               - Current status and priority
            
            2. THREE specific actionable points extracted from the sender's email/communications:
               - List exactly 3 actionable items that need to be addressed
               - Each action should be specific, clear, and derived from the customer's request
               - Format as: "Action 1:", "Action 2:", "Action 3:"
            
            Format your response as:
            
            **Overview:**
            [Your 2-3 sentence summary]
            
            **Actionable Points:**
            1. [First action point]
            2. [Second action point]
            3. [Third action point]
            
            Focus on property management context. Keep it professional and actionable.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a property management support assistant. Generate clear summaries with specific actionable points from customer communications."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating case summary: {e}")
            return self._generate_fallback_summary(case_context)
    
    def _generate_fallback_summary(self, case_context: str) -> str:
        """
        Generate intelligent, case-specific fallback summary without OpenAI
        Uses rule-based parsing and analysis of email content
        """
        # Extract key information from case context
        lines = case_context.strip().split('\n')
        case_info = {}
        email_content = ""
        
        for line in lines:
            if ':' in line and line.strip():
                # Handle both "- Key: value" and "Key: value" formats
                clean_line = line.strip().lstrip('-').strip()
                if ':' in clean_line:
                    key, value = clean_line.split(':', 1)
                    case_info[key.strip()] = value.strip()
            elif line.strip() and not line.strip().startswith('-') and not line.strip().startswith('Case Details'):
                email_content += line.strip() + " "
        
        # Parse email content if available
        if "Customer Email Content:" in case_context:
            email_section = case_context.split("Customer Email Content:")[1] if "Customer Email Content:" in case_context else ""
            email_content = email_section.strip()
        
        # Extract basic info
        title = case_info.get('Title', 'Unknown Case')
        case_type = case_info.get('Type', 'General')
        priority = case_info.get('Priority', 'Medium')
        status = case_info.get('Status', 'New')
        customer = case_info.get('Customer', 'Unknown Customer')
        property_number = case_info.get('Property Number', 'N/A')
        block_number = case_info.get('Block Number', 'N/A')
        completed_tasks = case_info.get('Completed Tasks', '0')
        total_tasks = case_info.get('Total Tasks', '0')
        
        # Analyze email content for issues, urgency, sentiment
        analysis = self._analyze_email_content(email_content, title)
        
        # Build property reference
        property_ref = f"Property {property_number}, Block {block_number}" if property_number != 'N/A' else "the property"
        
        # Build intelligent overview
        overview = self._build_overview(
            customer, property_ref, title, analysis, 
            priority, status, completed_tasks, total_tasks
        )
        
        # Generate case-specific actionable points
        actionable_points = self._generate_smart_actions(
            analysis, property_ref, customer, property_number, block_number
        )
        
        # Format summary
        summary = f"**Overview:**\n{overview}\n\n**Actionable Points:**\n"
        for i, point in enumerate(actionable_points[:3], 1):
            summary += f"{i}. {point}\n"
        
        return summary.strip()
    
    def _analyze_email_content(self, email_text: str, title: str) -> dict:
        """
        Analyze email content to detect issues, urgency, and sentiment
        Returns dict with detected issues, urgency level, and sentiment
        """
        combined_text = (email_text + " " + title).lower()
        
        # Issue type detection (expanded keyword lists)
        issue_keywords = {
            'door': ['door', 'jammed', 'stuck', 'broken door', 'door stuck', 'cant open', "can't open"],
            'plumbing': ['leak', 'pipe', 'pipeline', 'water', 'plumbing', 'drain', 'faucet', 'toilet', 'sink'],
            'electrical': ['power', 'electric', 'light', 'socket', 'wiring', 'electricity', 'bulb', 'switch'],
            'hvac': ['heating', 'cooling', 'ac', 'temperature', 'hvac', 'air conditioning', 'heater', 'cold', 'hot'],
            'pest': ['pest', 'rat', 'mouse', 'cockroach', 'insect', 'bug', 'infestation'],
            'noise': ['noise', 'loud', 'noisy', 'sound', 'disturb', 'disruption'],
            'security': ['lock', 'key', 'security', 'broken', 'theft', 'break in', 'unsafe'],
            'cleaning': ['dirty', 'clean', 'trash', 'garbage', 'mess', 'sanitation'],
            'structural': ['crack', 'wall', 'ceiling', 'floor', 'damage', 'broken', 'collapse']
        }
        
        detected_issues = []
        for issue_type, keywords in issue_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                detected_issues.append(issue_type)
        
        # Urgency detection
        urgent_keywords = ['urgent', 'emergency', 'asap', 'immediately', 'critical', 'dangerous', 'safety', 'hazard', 'right now', 'today']
        is_urgent = any(keyword in combined_text for keyword in urgent_keywords)
        
        # Sentiment detection
        angry_keywords = ['angry', 'furious', 'outraged', 'appalled', 'disgusted', 'unacceptable']
        frustrated_keywords = ['frustrated', 'disappointed', 'upset', 'fed up', 'waiting', 'still not fixed']
        satisfied_keywords = ['thank', 'appreciate', 'satisfied', 'happy', 'grateful', 'excellent']
        
        sentiment = 'Neutral'
        if any(keyword in combined_text for keyword in angry_keywords):
            sentiment = 'Angry'
        elif any(keyword in combined_text for keyword in frustrated_keywords):
            sentiment = 'Frustrated'
        elif any(keyword in combined_text for keyword in satisfied_keywords):
            sentiment = 'Satisfied'
        
        return {
            'issues': detected_issues,
            'is_urgent': is_urgent,
            'sentiment': sentiment,
            'has_content': len(email_text.strip()) > 10
        }
    
    def _build_overview(self, customer: str, property_ref: str, title: str, 
                       analysis: dict, priority: str, status: str, 
                       completed: str, total: str) -> str:
        """Build intelligent overview based on analysis"""
        
        # Start with customer and property
        overview_parts = [f"{customer} "]
        
        # Add issue description
        if analysis['issues']:
            issue_names = {
                'door': 'door jamming',
                'plumbing': 'plumbing',
                'electrical': 'electrical',
                'hvac': 'HVAC',
                'pest': 'pest control',
                'noise': 'noise disturbance',
                'security': 'security',
                'cleaning': 'cleaning',
                'structural': 'structural damage'
            }
            issue_list = [issue_names.get(i, i) for i in analysis['issues'][:2]]
            if len(issue_list) == 1:
                overview_parts.append(f"reports {issue_list[0]} issue at {property_ref}. ")
            else:
                overview_parts.append(f"reports {' and '.join(issue_list)} issues at {property_ref}. ")
        else:
            # Use title as issue
            overview_parts.append(f"has submitted a request regarding '{title}' for {property_ref}. ")
        
        # Add urgency context
        if analysis['is_urgent']:
            overview_parts.append("This is an **urgent** matter requiring immediate attention. ")
        elif priority in ['High', 'Urgent']:
            overview_parts.append("This is a high-priority issue. ")
        
        # Add status and progress
        overview_parts.append(f"Current status: {status}. ")
        if total != '0':
            overview_parts.append(f"Progress: {completed}/{total} tasks completed.")
        else:
            overview_parts.append("No tasks created yet.")
        
        return ''.join(overview_parts)
    
    def _generate_smart_actions(self, analysis: dict, property_ref: str, 
                                customer: str, property_number: str, 
                                block_number: str) -> list:
        """Generate case-specific actionable points based on detected issues"""
        
        actions = []
        
        # Issue-specific actions
        if 'door' in analysis['issues']:
            actions.append(f"Dispatch carpenter/handyman to inspect and repair door issue at {property_ref}")
        
        if 'plumbing' in analysis['issues']:
            actions.append(f"Schedule licensed plumber for {property_ref} to assess and fix plumbing issue")
        
        if 'electrical' in analysis['issues']:
            actions.append(f"Assign certified electrician to {property_ref} for electrical safety inspection and repair")
        
        if 'hvac' in analysis['issues']:
            actions.append(f"Contact HVAC specialist to service heating/cooling system at {property_ref}")
        
        if 'pest' in analysis['issues']:
            actions.append(f"Arrange pest control service for {property_ref} immediately")
        
        if 'security' in analysis['issues']:
            actions.append(f"Dispatch security/locksmith to {property_ref} to address security concern")
        
        if 'structural' in analysis['issues']:
            actions.append(f"Schedule structural inspection at {property_ref} to assess safety and damage")
        
        # Customer communication action
        if analysis['is_urgent']:
            actions.append(f"Contact {customer} immediately (within 2 hours) to confirm contractor dispatch time")
        else:
            actions.append(f"Contact {customer} within 24 hours with inspection timeline and next steps")
        
        # Property detail gathering (if missing)
        if property_number == 'N/A' or block_number == 'N/A':
            actions.insert(0, f"Gather complete property details (number, block, address) from {customer}")
        
        # Follow-up action
        if not actions:
            # Generic fallback actions
            actions = [
                f"Review case details and email communications from {customer}",
                f"Contact {customer} to clarify requirements and gather additional information",
                "Determine appropriate action and update case status to 'In Progress'"
            ]
        else:
            # Add status update action
            actions.append("Update case status to 'In Progress' once contractor is assigned and dispatched")
        
        return actions[:3]  # Return top 3
    
    def generate_case_tasks(self, case_context: str, completed_tasks: list = None) -> list:
        """Generate actionable tasks for case resolution"""
        try:
            if not self.client:
                return self._generate_fallback_tasks(case_context)
                
            completed_tasks_text = ""
            if completed_tasks:
                completed_tasks_text = f"\nCompleted tasks so far:\n" + "\n".join([f"- {task}" for task in completed_tasks])
            
            prompt = f"""
            Based on the following case information, generate a list of actionable tasks needed to resolve this case:
            
            {case_context}
            {completed_tasks_text}
            
            Generate 3-5 specific, actionable tasks that would help resolve this case. Each task should be:
            - Specific and actionable
            - Relevant to the case type, priority, and property details
            - Appropriate for property management support staff
            - Consider the property number and block number for location-specific tasks
            - Include property inspection, maintenance, or communication tasks as appropriate
            
            Focus on property management context:
            - If it's a maintenance issue, include property inspection and repair tasks
            - If it's a tenant request, include verification and implementation tasks
            - If property details are available, reference them in task descriptions
            - Consider escalation paths for urgent issues
            
            Return as a JSON array of task objects with this structure:
            [
                {{
                    "id": "task_1",
                    "title": "Task title",
                    "description": "Detailed description of what needs to be done (include property details if relevant)",
                    "priority": "High|Medium|Low",
                    "estimated_time": "15 minutes|30 minutes|1 hour|etc"
                }}
            ]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a property management support assistant. Generate actionable tasks for case resolution."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            import json
            tasks_json = response.choices[0].message.content.strip()
            # Clean up the response to extract JSON
            if "```json" in tasks_json:
                tasks_json = tasks_json.split("```json")[1].split("```")[0]
            elif "```" in tasks_json:
                tasks_json = tasks_json.split("```")[1].split("```")[0]
            
            return json.loads(tasks_json)
            
        except Exception as e:
            print(f"Error generating case tasks: {e}")
            return self._generate_fallback_tasks(case_context)
    
    def _generate_fallback_tasks(self, case_context: str) -> list:
        """Generate fallback tasks when OpenAI API is not available"""
        # Extract key information from case context
        lines = case_context.strip().split('\n')
        case_info = {}
        for line in lines:
            if ':' in line and line.strip():
                key, value = line.split(':', 1)
                case_info[key.strip()] = value.strip()
        
        case_type = case_info.get('Type', 'General').lower()
        priority = case_info.get('Priority', 'Medium').lower()
        property_number = case_info.get('Property Number', 'N/A')
        block_number = case_info.get('Block Number', 'N/A')
        
        # Build property reference for task descriptions
        property_ref = ""
        if property_number != 'N/A' or block_number != 'N/A':
            property_ref = f" for {property_number}, {block_number}"
        
        # Check if property details are missing
        missing_property_details = property_number == 'N/A' and block_number == 'N/A'
        
        # Generate tasks based on case type and priority
        if case_type == 'complaint' or case_type == 'maintenance':
            tasks = []
            
            # If property details are missing, add task to gather them
            if missing_property_details:
                tasks.append({
                    "id": "task_1",
                    "title": "Gather property details",
                    "description": "Contact customer to obtain property number and block number for accurate case tracking",
                    "priority": "High",
                    "estimated_time": "15 minutes"
                })
            
            # Add standard tasks
            start_id = 2 if missing_property_details else 1
            tasks.extend([
                {
                    "id": f"task_{start_id}",
                    "title": "Property inspection",
                    "description": f"Conduct on-site inspection{property_ref} to assess the reported issue",
                    "priority": "High",
                    "estimated_time": "45 minutes"
                },
                {
                    "id": f"task_{start_id + 1}",
                    "title": "Contact customer",
                    "description": f"Reach out to customer to gather additional details about the issue{property_ref}",
                    "priority": "High",
                    "estimated_time": "20 minutes"
                },
                {
                    "id": f"task_{start_id + 2}",
                    "title": "Arrange repair/maintenance",
                    "description": f"Schedule and coordinate repair work{property_ref} with appropriate contractors",
                    "priority": "High",
                    "estimated_time": "1 hour"
                },
                {
                    "id": f"task_{start_id + 3}",
                    "title": "Follow up and verify",
                    "description": f"Verify that the issue has been resolved{property_ref} and follow up with customer",
                    "priority": "Medium",
                    "estimated_time": "30 minutes"
                }
            ])
            return tasks
        elif case_type == 'request':
            tasks = []
            
            # If property details are missing, add task to gather them
            if missing_property_details:
                tasks.append({
                    "id": "task_1",
                    "title": "Gather property details",
                    "description": "Contact customer to obtain property number and block number for accurate case tracking",
                    "priority": "High",
                    "estimated_time": "15 minutes"
                })
            
            # Add standard request tasks
            start_id = 2 if missing_property_details else 1
            tasks.extend([
                {
                    "id": f"task_{start_id}",
                    "title": "Review request",
                    "description": f"Analyze the service request{property_ref} and determine feasibility",
                    "priority": "Medium",
                    "estimated_time": "20 minutes"
                },
                {
                    "id": f"task_{start_id + 1}",
                    "title": "Plan implementation",
                    "description": f"Create implementation plan and timeline for {property_ref}",
                    "priority": "Medium",
                    "estimated_time": "30 minutes"
                },
                {
                    "id": f"task_{start_id + 2}",
                    "title": "Execute request",
                    "description": f"Implement the requested service or solution{property_ref}",
                    "priority": "Medium",
                    "estimated_time": "45 minutes"
                },
                {
                    "id": f"task_{start_id + 3}",
                    "title": "Verify completion",
                    "description": f"Confirm that the request has been fulfilled{property_ref}",
                    "priority": "Medium",
                    "estimated_time": "15 minutes"
                }
            ])
            return tasks
        else:
            tasks = []
            
            # If property details are missing, add task to gather them
            if missing_property_details:
                tasks.append({
                    "id": "task_1",
                    "title": "Gather property details",
                    "description": "Contact customer to obtain property number and block number for accurate case tracking",
                    "priority": "High",
                    "estimated_time": "15 minutes"
                })
            
            # Add standard general tasks
            start_id = 2 if missing_property_details else 1
            tasks.extend([
                {
                    "id": f"task_{start_id}",
                    "title": "Review case details",
                    "description": f"Thoroughly review all case information and customer communications{property_ref}",
                    "priority": "High",
                    "estimated_time": "15 minutes"
                },
                {
                    "id": f"task_{start_id + 1}",
                    "title": "Contact customer",
                    "description": f"Reach out to customer to gather additional information if needed{property_ref}",
                    "priority": "Medium",
                    "estimated_time": "30 minutes"
                },
                {
                    "id": f"task_{start_id + 2}",
                    "title": "Update case status",
                    "description": f"Update case with progress and resolution steps{property_ref}",
                    "priority": "Medium",
                    "estimated_time": "10 minutes"
                }
            ])
            return tasks
    
    def generate_case_timeline_summary(self, threads: list, tasks: list) -> str:
        """Generate a summary of case progression from threads and tasks"""
        try:
            if not self.client:
                return self._generate_fallback_timeline_summary(threads, tasks)
                
            threads_text = ""
            if threads:
                threads_text = "\nCommunication History:\n" + "\n".join([f"- {thread.get('subject', 'Communication')}: {thread.get('preview', 'No preview')}" for thread in threads])
            
            tasks_text = ""
            if tasks:
                tasks_text = "\nCompleted Tasks:\n" + "\n".join([f"- {task.get('title', task.get('subject', 'Task'))}: {task.get('status', 'Unknown status')}" for task in tasks])
            
            prompt = f"""
            Based on the following case progression, generate a concise timeline summary:
            
            {threads_text}
            {tasks_text}
            
            Provide a 2-3 sentence summary that captures:
            - How the case has progressed
            - Key communications and actions taken
            - Current state and next steps
            
            Keep it professional and informative for support staff.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a property management support assistant. Summarize case progression clearly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating timeline summary: {e}")
            return self._generate_fallback_timeline_summary(threads, tasks)
    
    def _generate_fallback_timeline_summary(self, threads: list, tasks: list) -> str:
        """Generate fallback timeline summary when OpenAI API is not available"""
        thread_count = len(threads) if threads else 0
        task_count = len(tasks) if tasks else 0
        
        if thread_count > 0 and task_count > 0:
            return f"Case has progressed with {thread_count} communication(s) and {task_count} task(s) completed. Ongoing resolution process with active customer engagement."
        elif thread_count > 0:
            return f"Case involves {thread_count} communication(s) with customer. Active dialogue in progress to resolve the issue."
        elif task_count > 0:
            return f"Case has {task_count} task(s) completed. Progress is being made on resolution activities."
        else:
            return "Case is in initial stages. No significant progress recorded yet."
    
    def generate_response_suggestion(self, task):
        """Generate a suggested response for a task"""
        try:
            prompt = f"""
            Based on this customer support task, suggest a professional response:
            
            Category: {task.category}
            Priority: {task.priority}
            Summary: {task.summary}
            Original Email: {task.content[:500]}...
            
            Provide a professional, helpful response that addresses the customer's needs.
            Keep it concise but comprehensive.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional customer support agent. Write helpful, empathetic responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating response suggestion: {e}")
            return "Thank you for contacting us. We are reviewing your request and will get back to you soon."


