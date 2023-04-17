
import os.path
import time
from winotify import Notification, audio
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_FILE = "credentials.json"
API_NAME = "gmail"
API_VERSION = "v1"
SCOPES = ["https://mail.google.com/"]

def login():
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
        service = build(API_NAME, API_VERSION, credentials=credentials)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, scopes=SCOPES)
            credentials = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(credentials.to_json())
            print("token.json created")    
    return credentials

def watch_emails(service):
    try:
        response = service.users().watch(userId="me", body = { "labelIds": ["INBOX"], "topicName": "projects/boreal-pride-383611/topics/email"  }).execute()
        print('Successfully set up push notification channel')
        return response    
    except TypeError as error:
        print(f'An error occurred: {error}')
        return None    
    
def get_emails():
    wait_flag = 1
    credentials = login()
    service = build(API_NAME, API_VERSION, credentials=credentials)
    while True:
        response = service.users().messages().list(userId = "me", labelIds = ["INBOX"], q="is:unread").execute()
        messages = response.get("messages", [])
        if messages != [] and wait_flag == 1:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg['payload']
                headers = payload['headers']
                subject = ""
                sender = ""
                for header in headers:
                    if header['name'] == 'Subject':
                        subject = header['value']
                    if  header["name"] == "From":
                        sender = header["value"]
                notification = Notification(app_id = "New Email", title = sender, msg = subject, duration = "long", icon = r"C:\Users\ASUS\Desktop\Email PopUp\gmail-icon.png")   
                notification.set_audio(audio.SMS, loop=False);
                notification.add_actions(label="Open Email", launch="https://mail.google.com/mail/u/0/#inbox")
                notification.show()
                print("Labels:", msg["labelIds"])            
                print('Message Subject:', subject)
                print("From:", sender)
                time.sleep(5)
            wait_flag = 0
        if messages == [] and wait_flag == 0:
            print("nothing new...")
            wait_flag = 1
        time.sleep(10)   
    
get_emails()

