from __future__ import print_function

import os.path
import pickle
import base64
import email

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the token file so it re-authenticates.
# For read/write: "https://www.googleapis.com/auth/gmail.modify"
# For readonly: "https://www.googleapis.com/auth/gmail.readonly"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    """
    1. Builds a Gmail service instance using provided credentials.
    2. Fetches emails from a specific sender and downloads PDF attachments.
    """

    creds = None
    # Path to the client secrets file
    client_secrets_path = os.path.join("config", "client_secret_280337572135-bm9uigi0o89lmeep72j2fphs54sh7po4.apps.googleusercontent.com.json")

    if os.path.exists(client_secrets_path):
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
        creds = flow.run_local_server(port=0)
    else:
        raise FileNotFoundError(f"Client secrets file not found at {client_secrets_path}")

    service = build('gmail', 'v1', credentials=creds)

    # Example: Find emails from a specific sender and download PDF attachments
    sender_email = "ERP.Barnet@mail.biu.ac.il"  # Replace with actual sender's email
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q=f"from:{sender_email}",
        maxResults=5
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No messages found from the specified sender.")
    else:
        print("\nMessages from specified sender:")
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

            # Extract subject from the email
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            subject = None
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                    break

            print(f"- Subject: {subject}")

            # Download PDF attachments
            parts = payload.get('parts', [])
            for part in parts:
                if part['filename'] and part['filename'].endswith('.pdf'):
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


if __name__ == '__main__':
    main()
