import pickle
import os.path
import pandas as pd
import MassegeHeandler

class Loader:
    def __init__(self,service,directory,label_ids):
        self.service = service
        self.directory = directory
        self.user_label_ids = label_ids
   
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
            if 'messages' in response:
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
    
    def save_message(self,msg_info):
        '''Сохранение одного сообщения на диск'''
        id = MassegeHeandler.GetID(msg_info)
        msg = self.GetMessage(id)
        msg_data = MassegeHeandler.pack_message(msg,self.user_label_ids)      
        with open(self.directory+'/mails/mail_{}'.format(id),'wb') as file:
            pickle.dump(msg_data,file)
    
    def save_all(self):
        '''Сохранение всех сообщений юзера c почты на диск'''
        message_list = self.ListMessages()
        for msg_info in message_list:
            id = MassegeHeandler.GetID(msg_info)
            if not os.path.exists(self.directory+'/mails/mail_{}'.format(id)):
                self.save_message(msg_info)
                
    def update_all(self):
        message_list = self.ListMessages()
        for msg in message_list:
            self.save_message(msg)
        
    def load_all(self):
        '''Загрузка всех сообщений юзера с диска в датафрейм'''
        data = pd.DataFrame()
        os.chdir(self.directory+'/mails')
        for mail in os.listdir('.'):
            with open(mail,'rb') as file:
                cur_mail = pd.DataFrame.from_dict(pickle.load(file))
                data = data.append(cur_mail,ignore_index = True)
        return data   
     
    
    



    