import openai
import os
import json
import re
from .category_tree import property_categories

class LLMService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
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
                "action_required": "Brief description of what action needs to be taken"
            }}
            
            Guidelines:
            - This is a PROPERTY MANAGEMENT system, so focus on property-related issues
            - Priority should be High for urgent maintenance, safety, or security issues
            - Priority should be Urgent for emergencies, safety hazards, or security breaches
            - Category should be the most specific category that matches the issue
            - Common categories include: Plumbing, Electrical, HVAC, Structural, Maintenance & Repairs, Utilities, Billing & Accounts, Amenities & Services, Safety & Security, Neighbour Relations, Cleaning & Waste, Requests & Inquiries
            - Summary should capture the essence of what the customer is asking for
            - Be concise but informative
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
                    'action_required': result.get('action_required', 'Review and respond')
                }
            else:
                # Fallback if JSON parsing fails
                category, _ = property_categories.find_best_category(email_content)
                return {
                    'summary': content[:200] + '...' if len(content) > 200 else content,
                    'category': category,
                    'priority': 'Medium',
                    'sentiment': 'Neutral',
                    'action_required': 'Review and respond'
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
                'action_required': 'Review and respond'
            }
    
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


