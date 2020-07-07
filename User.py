import Loader
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class User:
                   
    def __init__(self,name):
        self.name = name
        self.directory = 'users/'+name
        self.label_names = {}
        self.label_ids = {}
        if(not User.exists(name)):
            self.create_user()
        else:
            self.load_user()
        self.authorize()
        self.load_labels()
        self.loader = Loader.Loader(self.service, self.directory)
        self.load_mails()
        self.get_unlabeled()
        
        
        
    def exists(user):
        if(os.path.exists('users/'+user)) :
            return True
        return False
        
    def load_labels(self):
        response = self.service.users().labels().list(userId='me').execute()
        for lab in response['labels']:
            if(lab['type'] == 'user'):
                self.label_names.add(lab['name'])
                self.label_ids.add(lab['id'])
           
    def create_user(self):
        self.userdir = 'users/'+self.user
        os.mkdir(self.userdir)
        os.mkdir(self.userdir+'/mails')
        
    def authorize(self):
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
                      'https://www.googleapis.com/auth/gmail.modify']   
        creds = None
        if os.path.exists(self.directory+'/token.pickle'):
            with open(self.directory + '/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                with open(self.directory+'/token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
        self.service = build('gmail', 'v1', credentials=creds)
        
    def load_mails(self):
        self.loader.save_all()
        self.mails = self.loader.load_all()
        
    def load_user(self):
        pass
        
    def get_unlabeled(self):
        #TODO: протестить
        '''Получает список номеров не помеченных сообщений'''
        unlbeled = len(set(self.mails['labels']).intersection(self.label_ids))==0
        self.unlbeled = self.mails.loc[unlbeled]['id']
    
    
    def label_msg(msg):
        pass
    def label_all(self):
        pass
        
