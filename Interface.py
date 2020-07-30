from User import User
import os
import numpy as np
from sys import exit

def get_username():
    print("Welcom to Mail Classifier!")
    return input('login : ')

def download():
    user.load_mails_info()
    
def set_learning_labels(learning_labels):
    while(len(learning_labels)==0 or user.set_learning_labels(learning_labels)):
        print('Choose at least 2 labes for big(> 10 mails) and small(3 < mails < 10) categories!')
        ans = input('Indexes : ')
        if(ans=='all'):
            learning_labels = np.arange(len(user.label_names))
        else:
            learning_labels = ans.split()
       
def fit(alpha,beta):
    user.fit_model(alpha,beta)
    
def predict():
    user.predict()   
    
def check():
    return os.path.exists('credentials.json')
    
if(check()):    
    user = User(get_username())
    ans = input('Logined! Download Messages?(y/n) : ')
    if(ans=='y'):
        download()
    else:
        print('Good by!')
        exit()
    print('Done! Choose labels to be automatically predicted(space separated indexes or all)')    
    for i,label in enumerate(user.label_names):
        print(str(i+1)+'. '+label+' '+str(user.counts[label]))
    ans = input('Indexes : ')
    if(ans=='all'):
        set_learning_labels(np.arange(len(user.label_names)))
    else:
        set_learning_labels(ans.split())
    print('Done! Choose the confidance leavel for classification(float from 0 to 1).')
    alpha = float(input('For big categories : '))
    beta = float(input('For small categories : '))
    ans = input('Fit the model?(y/n) : ')  
    if(ans=='y'):
        fit(alpha,beta)
    else:
        print('Good by!')
        exit()
    ans = input('Done!Predict?(y/n) : ')
    if(ans=='y'):
        predict()
    else:
        print('Good by!')
        exit()
    print('Done! Good by!')     
    
else:
    print('File credentials.json is missing. Put it in the project root folder!')
