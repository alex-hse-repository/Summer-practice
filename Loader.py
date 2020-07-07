import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup
import base64
import email
import pandas as pd
import MassegeHeandler

class Loader:
    def __init__(self,service,directory):
        self.service = service
        self.directory = directory
   
    def ListMessages(self):
        """
        List all Messages of the user's mailbox.
   
        Returns:
            List of Messages. Note that the returned list contains Message IDs, 
            you must use get with the appropriate ID to get the details of a Message.
        """
     
        response = self.service.users().messages().list(userId='me').execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(userId='me',pageToken=page_token).execute()
            messages.extend(response['messages'])
    
        return messages 

    def GetMessage(self,msg_id):
        """
          Get a Message with given ID.
    
          Args:
            msg_id: The ID of the Message required.
    
          Returns:
            A Message.
        """
        message = self.service.users().messages().get(userId='me', id=msg_id,format = 'full').execute()
        return message

    def GetMimeMessage(self,msg_id):
      """Get a Message and use it to create a MIME Message.
    
      Args:
        msg_id: The ID of the Message required.
    
      Returns:
        A MIME Message, consisting of data from Message.
      """
      message = self.service.users().messages().get(userId='me', id=msg_id,format='raw').execute()
      #TODO: посмотреть что там с кодировкой
      msg_str = base64.urlsafe_b64decode(bytes(message['raw'],'UTF-8'))
      mime_msg = email.message_from_bytes(msg_str)
      return mime_msg

  
    def save_message(self,msg):
        '''Сохранение одного сообщения на диск'''
        id = MassegeHeandler.GetID(msg)
        msg_full = self.GetMessage(id)
        mime_msg = self.GetMimeMessage(id)
        msg_data = MassegeHeandler.pack_message(msg_full,mime_msg)      
        with open(self.directory+'/mails/mail_{}'.format(id),'wb') as file:
            pickle.dump(msg_data,file)
    
    def save_all(self):
        '''Сохранение всех сообщений юзера c почты на диск'''
        message_list = self.ListMessages()
        for msg in message_list:
            id = MassegeHeandler.GetID(msg)
            if not os.path.exists(self.directory+'/mails/mail_{}'.format(id)):
                self.save_message(msg)
       
    def load_all(self):
        '''Загрузка всех сообщений юзера с диска в датафрейм'''
        data = pd.DataFrame()
        for mail in os.listdir(self.directory+'/mails'):
            with open(mail,'rb') as file:
                cur_mail = pickle.load(file)
                data = data.append(cur_mail,ignore_index = True)
        return data   
     
    



    