from Loader import Loader
import DataCleaner
import MessageHeandler
from Model import Model
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
from Transformer import MainTransformer,SmallTransformer


class User:
    def __init__(self,name):
        
        if(not os.path.exists('users')):
            os.mkdir('users')
        self.name = name
        self.directory = 'users/' + name
        self.label_names = []
        self.label_ids = []
        self.name_id = {}
        self.id_name = {'Unsorted':'Unsorted'}
        if(not User.exists(name)):
            self.create_user()
        self.authorize()
        
    def exists(user):
        """
        Check the existence of user.

        Parameters
        ----------
        user : Username.
        
        Returns
        -------
        True if user exists, in the other case returns False.
        """
        return os.path.exists('users/'+user)
        
    def create_user(self):
        """
        Create folders for a new user.
       
        """
        self.userdir = 'users/'+self.name
        os.mkdir(self.userdir)
        os.mkdir(self.userdir+'/mails')
        os.mkdir(self.userdir+'/spam')
                
    def load_mails_info(self):
        """
        Load user labels and mails.
        
        """
        self.load_labels()
        self.loader = Loader(self.service, self.directory,self.label_ids)
        self.load_mails()
        self.counts = self.mails['label'].value_counts()
        self.label_names.sort(key = lambda label : self.counts[label],reverse = True)
        DataCleaner.pack(self.mails)
        
        
    def set_learning_labels(self,learning_labels): 
        """
        Set labels to be automatically predicted and split them into main/small categories.
            
        Parameters
        ----------
        learning_labels : Indexes of learning labels, indexing starts from 1.
        
        Returns
        -------
        TODO: solve bug with one label per category.
        True if user set only one label for a category, False in the other case.
                
        """
        k = 10 # Number of mails for main category
        self.learning_labels = [self.label_names[int(i)-1] for i in learning_labels]
        self.main_categories = [label for label in self.learning_labels if self.counts[label]>=k] 
        self.small_categories = [label for label in self.learning_labels
                                 if 3<=self.counts[label] and self.counts[label]<k]
        self.sort_mails()
        return (len(self.main_categories)==1 or len(self.small_categories)==1) 
    
     
    def sort_mails(self):
        """
        Sort mails into metacategories: main/small/unsorted. 
      
        """
        self.unlabeled = self.mails[self.mails['label'] == 'Unsorted']
        self.main_cat_mails = pd.DataFrame()
        self.small_cat_mails = pd.DataFrame()
        for label in self.main_categories:
            self.main_cat_mails = self.main_cat_mails.append(self.mails[self.mails['label']==label])
        for label in self.small_categories:
            self.small_cat_mails = self.small_cat_mails.append(self.mails[self.mails['label']==label])
             
           
    def fit_model(self,alpha,beta): 
        """
        Vectorize user mials and fit the model.

        Parameters
        ----------
        alpha : Confidence parameter for "main" categories from 0 to 1.
        beta : Confidence parameter for "small" categories from 0 to 1.
        
        """
        self.X_main,self.y_main,self.X_small,self.y_small = None,None,None,None 
        if(len(self.main_categories)!=0):
            self.main_transformer = MainTransformer().fit(self.main_cat_mails)
            self.X_main,self.y_main = self.main_transformer.transform(self.main_cat_mails)
        else:
            self.main_transformer = None
        if(len(self.small_categories)!=0):    
            self.small_transformer = SmallTransformer().fit(self.small_cat_mails)
            self.X_small,self.y_small = self.small_transformer.transform(self.small_cat_mails)    
        else:
            self.small_transformer = None
        self.model = Model(self.main_transformer,self.small_transformer,alpha,beta)
        self.model.fit(self.X_main,self.y_main,self.X_small,self.y_small)
        
    
    def predict(self):
        """
        Predict labels for unsorted mails and update them on GMail.

        """
        y_pred = self.model.predict(self.unlabeled)
        for i,msg_id in enumerate(self.unlabeled['id']):
            update = MessageHeandler.create_msg_label(self.name_id[y_pred[i]])
            self.service.users().messages().modify(userId='me', id=msg_id,body=update).execute()
             
           
    def load_labels(self):
        """
        Load user labels.

        """
        response = self.service.users().labels().list(userId='me').execute()
        for lab in response['labels']:
            if(lab['type'] == 'user'):
                if(lab['name']=='Unsorted'):
                     self.name_id[lab['name']] = lab['id']
                     self.id_name[lab['id']] = lab['name']
                else:     
                    self.label_names.append(lab['name'])
                    self.label_ids.append(lab['id'])
                    self.name_id[lab['name']] = lab['id']
                    self.id_name[lab['id']] = lab['name']
        #On the firts run creates special label "Unsorted"     
        if('Unsorted' not in self.name_id.keys()):        
            resp = self.CreateLabel(User.MakeLabel('Unsorted'))
            self.name_id['Unsorted'] = resp['id']
            self.id_name[resp['id']] = 'Unsorted'
            
    def authorize(self):
        """
        Authorize user in GMail account.
        Note: file credentials.json should be in the root directory of the project.
        
        """
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
        """
        Load user's mails into DataFrame.
        Note: Refresh folder with downloaded mails before load them to DataFrame.
        It might work slowly on the first run.  

        """
        self.loader.save_all()
        self.mails = self.loader.load_all()
        #Conver label_ids to label_names 
        self.mails['label'] = [self.id_name[label] for label in self.mails['label']]
        
    
    