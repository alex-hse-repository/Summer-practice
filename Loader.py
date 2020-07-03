import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup
import base64
import pandas as pd


def Authorize():
    SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'    
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service
    
def ListMessages(service, user_id = 'me'):
    """
    List all Messages of the user's mailbox.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.

    Returns:
        List of Messages. Note that the returned list contains Message IDs, 
        you must use get with the appropriate ID to get the details of a Message.
    """
 
    response = service.users().messages().list(userId=user_id).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])
    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id,pageToken=page_token).execute()
        messages.extend(response['messages'])

    return messages 

def GetMessage(service,msg_id,user_id='me'):
    """
      Get a Message with given ID.

      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

      Returns:
        A Message.
    """
    message = service.users().messages().get(userId=user_id, id=msg_id,format = 'full').execute()
    return message
 
def GetText(msg):
    #TODO
    payld = msg['payload'] # get payload of the message 
    if(payld['mimeType']=='text/html'):
        part_body = payld['body'] # fetching body of the message
        part_data = part_body['data'] # fetching data from the body
        clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
        clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
        clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
        soup = BeautifulSoup(clean_two , "lxml" )
        return soup.text
    return 'Error'

def GetSnippet(msg):
    return msg['snippet']

def GetLabels(msg):
    return msg['labelIds']

def GetID(msg):
    return msg['id']

def GetSubject(msg):
    headers = msg['payload']['headers']
    subject = 'Unknon'# Specail constant 
    for header in headers:
        if(header['name'] == 'Subject'):
            subject = header['value']
    return subject        

def getSender(msg):
    headers = msg['payload']['headers']
    sender = 'Unknon'# Specail constant 
    for header in headers:
        if(header['name'] == 'From'):
            sender = header['value']
    return sender 
               
def pack_message(msg,full = False): 
    labels = GetLabels(msg)
    text = GetSnippet(msg)
    if(full):
        text = GetText(msg)
    sender = getSender(msg)
    subject = GetSubject(msg)
    msg_data = {'text' : text,'labels':labels,'sender':sender,'subject':subject}
    return msg_data
    
def save_message(msg,full = False):
    id = GetID(msg)
    msg_data = pack_message(msg,full)
    with open('mails/mail_{}'.format(id),'wb') as file:
        pickle.dump(msg_data,file)
    
def save_all(service,message_list,full = False):
    for msg in message_list:
        msg = GetMessage(service, msg['id'])
        save_message(msg,full)
        
def load_message(service,id):
    msg_data = None
    if not os.path.exists('mails/mail_{}'.format(id)):
        msg = GetMessage(service, id)
        save_message(msg)
    with open('mails/mail_{}'.format(id),'rb') as file:
        msg_data = pickle.load(file)
    return msg_data 
def load_all():
    data = pd.DataFrame()
    os.chdir('mails')
    for mail in os.listdir('.'):
        with open(mail,'rb') as file:
            cur_mail = pickle.load(file)
            data = data.append(cur_mail,ignore_index = True)
    return data        
def load_from_gmail():
    service = Authorize()
    message_list = ListMessages(service)
    data = pd.DataFrame()
    for msg in message_list:
        message = load_message(service,msg['id'])
        data = data.append(message,ignore_index = True)
    return data    
    
    