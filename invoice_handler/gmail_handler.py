from __future__ import print_function

import os.path
import base64
from datetime import datetime
from invoice_handler.config import gmail_secret_filename, sender_email
import invoice_handler.log_functions as log
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# For read/write: "https://www.googleapis.com/auth/gmail.modify"
# For readonly: "https://www.googleapis.com/auth/gmail.readonly"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def fetch_pdf_attachments(sender: str | None = None):
    """
    Fetches emails from a specific sender and downloads PDF attachments.
    Default sender email stored in config
    Returns a list of downloaded PDF filenames.
    """
    if sender is None:
        sender = sender_email
    log.initialize_logs()
    max_emails = 5
    creds = None
    # Path to the client secrets file
    client_secrets_path = os.path.join("invoice_handler/config", gmail_secret_filename)

    if os.path.exists(client_secrets_path):
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
        creds = flow.run_local_server(port=0)
    else:
        raise FileNotFoundError(f"Client secrets file not found at {client_secrets_path}")

    service = build('gmail', 'v1', credentials=creds)

    # Read processed email and filenames from logs
    processed_logs = log.read_log("emails")
    processed_files = {entry['filename'] for entry in processed_logs}

    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q=f"from:{sender}",
        maxResults=max_emails
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No messages found from the specified sender.")
        return []

    pdf_filenames = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

        # Extract subject and email date
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])
        subject = None
        email_date = None

        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'Date':
                email_date = header['value']

        print(f"- Processing email: {subject}")

        # Download PDF attachments
        parts = payload.get('parts', [])
        for part in parts:
            if part['filename'] and part['filename'].endswith('.pdf'):
                if part['filename'] in processed_files:
                    print(f"File already processed: {part['filename']}")
                    continue

                attachment_id = part['body'].get('attachmentId')
                if attachment_id:
                    attachment = service.users().messages().attachments().get(
                        userId='me', messageId=message['id'], id=attachment_id
                    ).execute()
                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

                    # Save the file
                    file_path = os.path.join("downloads", part['filename'])
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'wb') as f:
                        f.write(file_data)

                    print(f"Attachment saved: {file_path}")
                    pdf_filenames.append(part['filename'])

                    # Log the processed file
                    log.write_log("emails", {
                        "email_date": email_date,
                        "filename": part['filename'],
                        "timestamp": datetime.now().isoformat()
                    })

    return pdf_filenames
