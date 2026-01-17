import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sys
from bs4 import BeautifulSoup
import re

# Scope for reading Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.getcwd()

def get_credentials():
    creds = None
    base_path = get_base_path()
    token_path = os.path.join(base_path, 'token.json')
    creds_path = os.path.join(base_path, 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None # invalid refresh, needs login
        
        if not creds:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"credentials.json not found at {creds_path}")
            
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    return creds

def get_service():
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)

def logout():
    base_path = get_base_path()
    token_path = os.path.join(base_path, 'token.json')
    if os.path.exists(token_path):
        os.remove(token_path)
        return True
    return False

def search_messages(query):
    try:
        service = get_service()
        # 'q' parameter searches in Gmail
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        final_list = []
        if messages:
            # Get details for first batch (limit to 20 for speed in this demo, or loop)
            # For a real app, use batch request. Here we loop for simplicity but limit count.
            for msg in messages[:20]: 
                full_msg = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
                headers = full_msg.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                snippet = full_msg.get('snippet', '')
                final_list.append({
                    'id': msg['id'],
                    'subject': subject,
                    'date': date,
                    'snippet': snippet
                })
        return final_list
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def get_mime_part(parts, mime_type):
    """Recursively search for a specific mime_type."""
    for part in parts:
        if part.get('mimeType') == mime_type:
            return part
        if 'parts' in part:
            found = get_mime_part(part['parts'], mime_type)
            if found:
                return found
    return None

def get_attachment_data(service, msg_id, att_id):
    try:
        att = service.users().messages().attachments().get(userId='me', messageId=msg_id, id=att_id).execute()
        return att['data']
    except Exception as e:
        print(f"Error fetching attachment: {e}")
        return None

def process_inline_images(service, msg_id, html_content, parts):
    """Finds inline images (cid:) and replaces them with base64 data."""
    if not parts:
        return html_content
    
    import re
    
    # helper to traverse parts to find attachments
    def find_attachments(part_list, acc):
        for part in part_list:
            if 'body' in part and 'attachmentId' in part['body']:
                # It's an attachment. Check headers for Content-ID
                headers = part.get('headers', [])
                content_id = next((h['value'] for h in headers if h['name'] == 'Content-ID'), None)
                if content_id:
                    # Clean content_id (remove < and >)
                    clean_cid = content_id.strip('<>')
                    acc[clean_cid] = part['body']['attachmentId']
            
            if 'parts' in part:
                 find_attachments(part['parts'], acc)

    cid_map = {}
    find_attachments(parts, cid_map)

    # Replace src="cid:..."
    for cid, att_id in cid_map.items():
        if f"cid:{cid}" in html_content:
            b64_data = get_attachment_data(service, msg_id, att_id)
            if b64_data:
                # Gmail API returns urlsafe base64, need to convert to standard for data URI if needed, 
                # strictly speaking data URIs use standard base64, but browsers tolerate urlsafe often. 
                # Let's fix it to be safe.
                start_b64 = b64_data.replace('-', '+').replace('_', '/')
                replacement = f"data:image/jpeg;base64,{start_b64}" # Mime type assumption or extract from part?
                # Hard to get mime type easily here without keeping map of part objects. 
                # Trying generic image/jpeg or we can improve finding part mimeType.
                html_content = html_content.replace(f"cid:{cid}", replacement)
    
    return html_content

def clean_html_content(html_content):
    """Removes Gmail signatures and other noise."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove standard Gmail signature div
        for sig in soup.find_all('div', class_='gmail_signature'):
            sig.decompose()
            
        # Remove other common signature containers if necessary
        # e.g. divs with 'data-smartmail' attributes
        
        return str(soup)
    except Exception as e:
        print(f"Error cleaning HTML: {e}")
        return html_content

def get_message_content(msg_id):
    try:
        service = get_service()
        message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        
        payload = message.get('payload', {})
        parts = payload.get('parts', [])
        body_data = None
        
        # recursive fetch
        if not parts:
            body_data = payload.get('body', {}).get('data')
        else:
            html_part = get_mime_part(parts, 'text/html')
            if html_part:
                body_data = html_part['body'].get('data')
            else:
                plain_part = get_mime_part(parts, 'text/plain')
                if plain_part:
                    body_data = plain_part['body'].get('data')
        
        if body_data:
            html = base64.urlsafe_b64decode(body_data).decode('utf-8')
            
            # Clean signatures BEFORE processing images (efficiency + avoid messing with signature images)
            html = clean_html_content(html)
            
            # Now process inline images
            if parts:
                html = process_inline_images(service, msg_id, html, parts)
            return html
            
        return "No content found."

    except HttpError as error:
        print(f'An error occurred: {error}')
        return f"Error: {error}"
