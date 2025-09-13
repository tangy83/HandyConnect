import openai
import os
import json
import re

class LLMService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def process_email(self, email):
        """Process email content using OpenAI to extract summary, category, and priority"""
        try:
            # Prepare the email content for analysis
            email_content = f"""
            Subject: {email['subject']}
            From: {email['sender']['name']} ({email['sender']['email']})
            Content: {email['body']}
            """
            
            # Create a prompt for the LLM
            prompt = f"""
            Analyze the following customer support email and extract key information:
            
            {email_content}
            
            Please provide a JSON response with the following structure:
            {{
                "summary": "A concise summary of the customer's issue or request (max 200 words)",
                "category": "One of: Technical Issue, Billing Question, Feature Request, Complaint, General Inquiry, Account Issue",
                "priority": "One of: Low, Medium, High, Urgent",
                "sentiment": "One of: Positive, Neutral, Negative, Frustrated",
                "action_required": "Brief description of what action needs to be taken"
            }}
            
            Guidelines:
            - Priority should be High for urgent technical issues, billing problems, or complaints
            - Priority should be Urgent for security issues, service outages, or angry customers
            - Category should be based on the main topic of the email
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
                return {
                    'summary': result.get('summary', 'No summary available'),
                    'category': result.get('category', 'General Inquiry'),
                    'priority': result.get('priority', 'Medium'),
                    'sentiment': result.get('sentiment', 'Neutral'),
                    'action_required': result.get('action_required', 'Review and respond')
                }
            else:
                # Fallback if JSON parsing fails
                return {
                    'summary': content[:200] + '...' if len(content) > 200 else content,
                    'category': 'General Inquiry',
                    'priority': 'Medium',
                    'sentiment': 'Neutral',
                    'action_required': 'Review and respond'
                }
                
        except Exception as e:
            print(f"Error processing email with LLM: {e}")
            # Return default values if LLM processing fails
            return {
                'summary': f"Email from {email['sender']['name']}: {email['subject']}",
                'category': 'General Inquiry',
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
