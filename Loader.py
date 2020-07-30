import pickle
import os.path
import pandas as pd
import MessageHeandler
from email.mime.text import MIMEText
import base64


class Loader:
    
    def __init__(self,service,directory,label_ids):
        """
        Parameters
        ----------
        service : Authorized Gmail API service instance.
        directory : User directory.
        label_ids : User LabelIds.
        """
        self.service = service
        self.directory = directory
        self.user_label_ids = label_ids
        if(os.path.exists(self.directory+'/spam/list')):
            with open(self.directory+'/spam/list','rb') as file:
                self.spam_ids = pickle.load(file)
        else:
            self.spam_ids = set()
         
   
    def list_messages(self):
        """
        List all Messages of the user's mailbox.
   
        Returns
        -------
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

    def get_message(self,msg_id):
        """
        Get a Message with given ID.
    
        Parameters
        ----------
        msg_id: The ID of the Message.
    
        Returns
        -------
        message: Message.
        
        """
        message = self.service.users().messages().get(userId='me', id=msg_id,format = 'full').execute()
        return message
    
    def save_message(self,msg_id):
        """
        Save a Message if it is not spam or if it has not been saved yet.

        Parameters
        ----------
        msg_id: The ID of the Message.
        
       """
        if(not self.spam(msg_id)):
            if(not os.path.exists(self.directory+'/mails/mail_{}'.format(msg_id))):
                msg = self.get_message(msg_id)
                if(MessageHeandler.is_user_msg(msg)):
                    msg_data = MessageHeandler.pack_message(msg,self.user_label_ids)      
                    with open(self.directory+'/mails/mail_{}'.format(msg_id),'wb') as file:
                        pickle.dump(msg_data,file)
                else:
                    self.spam_ids.add(msg_id)
                
    def save_all(self):
        """
        Load all Messages from user's mailbox and save them on disk. 
        Does not resave Messages that has already been saved. 
        
       """
        message_list = self.list_messages()
        for msg_info in message_list:
           self.save_message(msg_info['id'])
        self.save_spam()    
        
    def load_all(self):
        """
        Load all Messages from disk to DataFrame.
        
        Returns
        -------
        data : DataFrame with user Messages.

        """
        data = pd.DataFrame()
        for mail in os.listdir(self.directory+'/mails'):
            with open(self.directory+'/mails/'+mail,'rb') as file:
                cur_mail = pd.DataFrame.from_dict(pickle.load(file))
                data = data.append(cur_mail,ignore_index = True)
        return data   
             
    def spam(self,msg_id):
        """
        Check whether Message ID contains in Spam IDs.

        Parameters
        ----------
        msg_id: The ID of the Message.
        
        Returns
        -------
        True if msg_id contains in spam, in the other case returns False.

        """
        if(msg_id in self.spam_ids):
            return True
        return False
    
    def save_spam(self):
        """
        Save Spam IDs on disk for reusage purpose.
                
        """
        with open(self.directory+'/spam/list','wb') as file:
            pickle.dump(self.spam_ids,file)
    
    def send_message(self, message):
        """
        Send an email Message.

        Parameters
        ----------
        message: Message to be sent.
    
        Returns
        -------
        Sent Message.
        """
        message = self.service.users().messages().send(userId='me', body=message).execute()
        return message
    
    def create_message(message_text,subject,address = 'apchikov@miem.hse.ru'):
        """
        Create a Message for an email.

        Parameters
        ----------
        message_text: Text of the email Message.
        subject: Subject of the email Message.
        address: Email address.
        
        Returns
        -------
        An object containing a base64url encoded email object.
        
        """
        message = MIMEText(message_text)
        message['To'] = address
        message['Subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
        return {'raw': raw_message.decode("utf-8")}
            
    def create_label(self, label_object):
        """
        Creates a new label within user's mailbox.

        Parameters
        ----------
        label_object: label to be added.
        
        Returns
        -------
        None.

        """
     
        return self.service.users().labels().create(userId='me',body=label_object).execute()
             
    def make_label(label_name, mlv='show', llv='labelShow'):
        """
        Create new Label object.

        Parameters
        ----------
        label_name: The name of the Label.
        mlv: Message list visibility, show/hide.
        llv: Label list visibility, labelShow/labelHide.
        
        Returns
        -------
        Created Label object.
        """
        label = {'messageListVisibility': mlv,
                 'name': label_name,
                 'labelListVisibility': llv}
        return label   
     
           
                



    