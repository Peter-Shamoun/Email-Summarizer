import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import pickle
from openai import OpenAI

# Add this line at the top of the file
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP for development

class GmailSummarizer:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.creds = None
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def authenticate(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        return build('gmail', 'v1', credentials=self.creds)

    def get_emails(self, service):
        # Calculate timestamp for 24 hours ago
        one_day_ago = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
        
        # Query for primary inbox emails from last 24 hours
        query = f"""
            in:inbox 
            category:primary 
            after:{one_day_ago}
        """.replace('\n', ' ').strip()
        
        results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
        messages = results.get('messages', [])
        emails = []

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = self._parse_email(msg)
            emails.append(email_data)

        return emails

    def _parse_email(self, msg):
        payload = msg['payload']
        headers = payload['headers']
        
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        sender = next(header['value'] for header in headers if header['name'] == 'From')
        
        # Get the email content more robustly
        def get_text_from_part(part):
            if 'data' in part.get('body', {}):
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif 'parts' in part:
                for subpart in part['parts']:
                    text = get_text_from_part(subpart)
                    if text:
                        return text
            return ''

        content = ''
        if 'parts' in payload:
            content = get_text_from_part(payload)
        elif 'data' in payload.get('body', {}):
            content = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return {
            'subject': subject,
            'sender': sender,
            'content': content
        }

    def summarize_emails(self, emails):
        # Combine all email information into a single prompt
        email_details = []
        for email in emails:
            # Skip Reddit emails
            if 'reddit' in email['sender'].lower():
                continue
                
            email_details.append(f"""
Subject: {email['subject']}
From: {email['sender']}
Content: {email['content'][:500]}...
---""")
        
        if not email_details:
            return "No non-Reddit emails found in the last 24 hours."
        
        combined_prompt = f"""
        Please provide a brief summary report of these emails from the last 24 hours. 
        Group similar topics together and highlight any important action items or urgent matters. Return your asnwers in markdown format.
        
        {"\n".join(email_details)}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise email summary reports. Focus on key information and action items."},
                {"role": "user", "content": combined_prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content

def main():
    # First check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("Please set your OPENAI_API_KEY environment variable")

    summarizer = GmailSummarizer()
    service = summarizer.authenticate()
    emails = summarizer.get_emails(service)
    summary_report = summarizer.summarize_emails(emails)

    print("\nEmail Summary Report for the Last 24 Hours:")
    print("==========================================")
    print(summary_report)

if __name__ == "__main__":
    main()
