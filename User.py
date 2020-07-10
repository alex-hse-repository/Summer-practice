import Loader
import DataCleaner
import DataTransformer
import MassegeHeandler
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class User:
                   
    def __init__(self,name):
        self.name = name
        self.directory = 'users/'+name
        self.label_ids = []
        if(not User.exists(name)):
            self.create_user()
        self.authorize()
        self.load_labels()
        self.loader = Loader.Loader(self.service, self.directory,self.label_ids)
        self.load_mails()
        self.sort_mails()
        
    def trian_model(self,model):
        X,y = DataTransformer.transform(DataCleaner.pack_data(self.labeled))
        model.fit(X,y)
        self.model = model
    
    def save_model(self,model_name):
        with open(self.directory+'/models/'+model_name,'wb') as file:
            pickle.dump(self.model,file)
    
    def load_model(self,model_name):
        with open(self.directory+'/models/'+model_name,'rb') as file:
            self.model = pickle.load(file)
           
    def exists(user):
        if(os.path.exists('users/'+user)) :
            return True
        return False
        
    def load_labels(self):
        response = self.service.users().labels().list(userId='me').execute()
        for lab in response['labels']:
            if(lab['type'] == 'user'):
                self.label_ids.append(lab['id'])
           
    def create_user(self):
        self.userdir = 'users/'+self.user
        os.mkdir(self.userdir)
        os.mkdir(self.userdir+'/mails')
        os.mkdir(self.userdir+'/models')
        
        
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
        
    def sort_mails(self):
        '''Сортирует сообщения на помеченные и не помеченные'''
        self.unlabeled = self.mails[self.mails['label']==None]
        self.labeled = self.mails[self.mails['label']!=None]
       
    def label_all(self):
        X,y = DataTransformer.transform(DataCleaner.pack_data(self.unlabeled))
        labels = self.model.predict(X)   
        update = MassegeHeandler.CreateMsgLabels(list(self.unlabeled['id']),labels)
        self.service.users().messages().batchModify(userId='me',body = update).execute()
        
    