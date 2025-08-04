import os
import json
import base64
import email
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    def __init__(self):
        self.service = None
        self.creds = None
        
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        token_path = 'token.json'
        
        # Load existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError("credentials.json not found. Please download it from Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.creds = creds
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service

    def list_emails(self, max_results: int = 10, query: str = None) -> List[Dict[str, Any]]:
        """List recent emails"""
        try:
            if not self.service:
                self.authenticate()
            
            # Build query
            gmail_query = query or "in:inbox"
            
            # Get messages
            results = self.service.users().messages().list(
                userId='me',
                q=gmail_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_list = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = msg['payload']['headers']
                email_data = {
                    'id': message['id'],
                    'threadId': message['threadId'],
                    'snippet': msg.get('snippet', ''),
                    'from': '',
                    'subject': '',
                    'date': '',
                    'labels': msg.get('labelIds', [])
                }
                
                for header in headers:
                    if header['name'] == 'From':
                        email_data['from'] = header['value']
                    elif header['name'] == 'Subject':
                        email_data['subject'] = header['value']
                    elif header['name'] == 'Date':
                        email_data['date'] = header['value']
                
                email_list.append(email_data)
            
            return email_list
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            raise Exception(f"Failed to list emails: {error}")
        except Exception as e:
            logger.error(f"Error listing emails: {e}")
            raise

    def read_email(self, email_id: str) -> Dict[str, Any]:
        """Read a specific email by ID"""
        try:
            if not self.service:
                self.authenticate()
            
            # Get full message
            message = self.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            # Parse headers
            headers = message['payload']['headers']
            email_data = {
                'id': email_id,
                'threadId': message['threadId'],
                'snippet': message.get('snippet', ''),
                'from': '',
                'to': '',
                'subject': '',
                'date': '',
                'body': '',
                'labels': message.get('labelIds', [])
            }
            
            for header in headers:
                if header['name'] == 'From':
                    email_data['from'] = header['value']
                elif header['name'] == 'To':
                    email_data['to'] = header['value']
                elif header['name'] == 'Subject':
                    email_data['subject'] = header['value']
                elif header['name'] == 'Date':
                    email_data['date'] = header['value']
            
            # Extract body
            if 'parts' in message['payload']:
                # Multipart message
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        email_data['body'] = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
                    elif part['mimeType'] == 'text/html':
                        # Fallback to HTML if no plain text
                        email_data['body'] = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
            else:
                # Simple message
                if message['payload']['mimeType'] == 'text/plain':
                    email_data['body'] = base64.urlsafe_b64decode(
                        message['payload']['body']['data']
                    ).decode('utf-8')
                elif message['payload']['mimeType'] == 'text/html':
                    email_data['body'] = base64.urlsafe_b64decode(
                        message['payload']['body']['data']
                    ).decode('utf-8')
            
            return email_data
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            raise Exception(f"Failed to read email: {error}")
        except Exception as e:
            logger.error(f"Error reading email: {e}")
            raise

    def search_emails(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search emails with a specific query"""
        try:
            if not self.service:
                self.authenticate()
            
            # Get messages matching query
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_list = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = msg['payload']['headers']
                email_data = {
                    'id': message['id'],
                    'threadId': message['threadId'],
                    'snippet': msg.get('snippet', ''),
                    'from': '',
                    'subject': '',
                    'date': '',
                    'labels': msg.get('labelIds', [])
                }
                
                for header in headers:
                    if header['name'] == 'From':
                        email_data['from'] = header['value']
                    elif header['name'] == 'Subject':
                        email_data['subject'] = header['value']
                    elif header['name'] == 'Date':
                        email_data['date'] = header['value']
                
                email_list.append(email_data)
            
            return email_list
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            raise Exception(f"Failed to search emails: {error}")
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            raise

# Global Gmail service instance
gmail_service = GmailService()

def compose_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    """Compose and send an email"""
    try:
        if not gmail_service.service:
            gmail_service.authenticate()
        
        # Create message
        message = email.mime.text.MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send message
        sent_message = gmail_service.service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return {
            'status': 'sent',
            'message_id': sent_message['id'],
            'thread_id': sent_message['threadId']
        }
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise Exception(f"Failed to send email: {e}")

def list_emails(max_results: int = 10, query: str = None) -> Dict[str, Any]:
    """List recent emails"""
    try:
        emails = gmail_service.list_emails(max_results, query)
        return {
            'status': 'success',
            'emails': emails,
            'count': len(emails)
        }
    except Exception as e:
        logger.error(f"Error listing emails: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def read_email(email_id: str) -> Dict[str, Any]:
    """Read a specific email by ID"""
    try:
        email_data = gmail_service.read_email(email_id)
        return {
            'status': 'success',
            'email': email_data
        }
    except Exception as e:
        logger.error(f"Error reading email: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def search_emails(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Search emails with a specific query"""
    try:
        emails = gmail_service.search_emails(query, max_results)
        return {
            'status': 'success',
            'emails': emails,
            'count': len(emails),
            'query': query
        }
    except Exception as e:
        logger.error(f"Error searching emails: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    """Send email using Gmail API (alias for compose_email)"""
    return compose_email(to, subject, body) 