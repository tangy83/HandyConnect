"""
Email Notification Service for HandyConnect
Handles sending notifications to customers when cases are created or updated.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class EmailNotificationService:
    """Service for sending email notifications to customers"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@handyconnect.com')
        self.from_name = os.getenv('FROM_NAME', 'HandyConnect Support')
        
    def send_case_created_notification(self, case: Dict, customer_email: str) -> bool:
        """Send notification email when a case is created"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured. Skipping email notification.")
                return False
            
            # Create email content
            subject = f"Case #{case.get('case_number', 'N/A')} - Your Request Has Been Received"
            
            # Extract property details
            customer_info = case.get('customer_info', {})
            property_number = customer_info.get('property_number', 'N/A')
            block_number = customer_info.get('block_number', 'N/A')
            property_details = ""
            
            if property_number != 'N/A' or block_number != 'N/A':
                property_details = f"""
Property Details:
- Property Number: {property_number}
- Block Number: {block_number}
"""
            
            # Create email body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Case Created - HandyConnect</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="margin: 0; font-size: 24px;">HandyConnect</h1>
                        <p style="margin: 5px 0 0 0; opacity: 0.9;">Property Management Support</p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #667eea; margin-top: 0;">Your Case Has Been Created</h2>
                        
                        <p>Dear {customer_info.get('name', 'Valued Customer')},</p>
                        
                        <p>Thank you for contacting HandyConnect. We have successfully logged your request and created a case for tracking purposes.</p>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                            <h3 style="margin-top: 0; color: #333;">Case Details</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; width: 40%;">Case Number:</td>
                                    <td style="padding: 8px 0;">{case.get('case_number', 'N/A')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold;">Subject:</td>
                                    <td style="padding: 8px 0;">{case.get('case_title', 'N/A')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold;">Priority:</td>
                                    <td style="padding: 8px 0;">{case.get('priority', 'Medium')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold;">Category:</td>
                                    <td style="padding: 8px 0;">{case.get('case_type', 'General')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold;">Created:</td>
                                    <td style="padding: 8px 0;">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</td>
                                </tr>
                            </table>
                            {property_details}
                        </div>
                        
                        <div style="background: #e8f4f8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4 style="margin-top: 0; color: #2c5aa0;">What Happens Next?</h4>
                            <ul style="margin: 0; padding-left: 20px;">
                                <li>Our support team will review your case within the next business day</li>
                                <li>You will receive updates on the progress of your request</li>
                                <li>We will contact you if we need any additional information</li>
                                <li>Expected resolution time varies based on the complexity of your request</li>
                            </ul>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                            <h4 style="margin-top: 0; color: #856404;">Important Notes:</h4>
                            <ul style="margin: 0; padding-left: 20px; color: #856404;">
                                <li>Please keep this case number for your records: <strong>{case.get('case_number', 'N/A')}</strong></li>
                                <li>For urgent matters, please call our emergency line</li>
                                <li>You can reply to this email with any additional information</li>
                            </ul>
                        </div>
                        
                        <p>Thank you for choosing HandyConnect. We appreciate your patience and look forward to resolving your request promptly.</p>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; font-size: 12px;">
                            <p>This is an automated message. Please do not reply to this email address.</p>
                            <p>© 2025 HandyConnect. All rights reserved.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_body = f"""
HandyConnect - Case Created Notification

Dear {customer_info.get('name', 'Valued Customer')},

Thank you for contacting HandyConnect. We have successfully logged your request and created a case for tracking purposes.

Case Details:
- Case Number: {case.get('case_number', 'N/A')}
- Subject: {case.get('case_title', 'N/A')}
- Priority: {case.get('priority', 'Medium')}
- Category: {case.get('case_type', 'General')}
- Created: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

{property_details.replace('<br>', '\n').replace('<strong>', '').replace('</strong>', '')}

What Happens Next?
- Our support team will review your case within the next business day
- You will receive updates on the progress of your request
- We will contact you if we need any additional information
- Expected resolution time varies based on the complexity of your request

Important Notes:
- Please keep this case number for your records: {case.get('case_number', 'N/A')}
- For urgent matters, please call our emergency line
- You can reply to this email with any additional information

Thank you for choosing HandyConnect. We appreciate your patience and look forward to resolving your request promptly.

Best regards,
HandyConnect Support Team

This is an automated message. Please do not reply to this email address.
© 2025 HandyConnect. All rights reserved.
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = customer_email
            
            # Attach parts
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Case created notification sent to {customer_email} for case {case.get('case_number')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send case created notification to {customer_email}: {e}")
            return False
    
    def send_case_update_notification(self, case: Dict, customer_email: str, update_message: str) -> bool:
        """Send notification email when a case is updated"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured. Skipping email notification.")
                return False
            
            subject = f"Case #{case.get('case_number', 'N/A')} - Update"
            
            customer_info = case.get('customer_info', {})
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Case Update - HandyConnect</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="margin: 0; font-size: 24px;">HandyConnect</h1>
                        <p style="margin: 5px 0 0 0; opacity: 0.9;">Property Management Support</p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #667eea; margin-top: 0;">Case Update</h2>
                        
                        <p>Dear {customer_info.get('name', 'Valued Customer')},</p>
                        
                        <p>We have an update on your case #{case.get('case_number', 'N/A')}.</p>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                            <h3 style="margin-top: 0; color: #333;">Update Details</h3>
                            <p>{update_message}</p>
                            <p><em>Updated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</em></p>
                        </div>
                        
                        <p>Thank you for your patience. If you have any questions, please don't hesitate to contact us.</p>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; font-size: 12px;">
                            <p>This is an automated message. Please do not reply to this email address.</p>
                            <p>© 2025 HandyConnect. All rights reserved.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = customer_email
            
            # Attach parts
            part1 = MIMEText(html_body, 'html')
            msg.attach(part1)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Case update notification sent to {customer_email} for case {case.get('case_number')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send case update notification to {customer_email}: {e}")
            return False
