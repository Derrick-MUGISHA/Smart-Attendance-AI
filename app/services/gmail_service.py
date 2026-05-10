import os
import base64
import logging
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.config import settings

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        token_path = 'token_gmail.json'
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            elif settings.GMAIL_CREDENTIALS_PATH and os.path.exists(settings.GMAIL_CREDENTIALS_PATH):
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.GMAIL_CREDENTIALS_PATH, SCOPES)
                self.creds = flow.run_local_server(port=0)
                with open(token_path, 'w') as token:
                    token.write(self.creds.to_json())
            else:
                logger.error("GMAIL_CREDENTIALS_PATH not set or file not found.")
                return

        self.service = build('gmail', 'v1', credentials=self.creds)

    def get_latest_absentee_emails(self, days_back: int = 1) -> List[Dict]:
        """
        Fetches emails from the last X days and identifies messages related to absence.
        """
        if not self.service:
            return []

        # Simple query for "absence" or "absent" or "permission"
        query = f'newer_than:{days_back}d (absence OR absent OR permission OR sick)'
        try:
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            email_data = []
            for msg in messages:
                m = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                
                payload = m.get('payload', {})
                headers = payload.get('headers', [])
                
                subject = ""
                sender = ""
                for h in headers:
                    if h['name'] == 'Subject':
                        subject = h['value']
                    if h['name'] == 'From':
                        sender = h['value']
                
                # Extract body
                body = ""
                if 'data' in payload.get('body', {}):
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                elif 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break

                email_data.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'body': body,
                    'date': m['internalDate']
                })
            
            return email_data
        except Exception as e:
            logger.error(f"Error fetching Gmail messages: {e}")
            return []

gmail_service = GmailService()
