from django.shortcuts import render
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json


def get_emails(request):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    file_path = 'config/client.json'

    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(file_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    results = service.users().messages().list(userId='me').execute()
    messages = results.get('messages', [])

    email_list = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        email_list.append(msg['snippet'])

    return render(request, 'emails.html', {'email_list': email_list})
