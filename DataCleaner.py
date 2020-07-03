import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer,WordNetLemmatizer
import pandas as pd
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('stopwords')
def clean_labels(labels):
    ignore = ['UNREAD','INBOX','IMPORTANT']
    label = [label for label in labels if label not in ignore]
    #Костыль
    if(len(label)==0):
        return 'CATEGORY_UPDATES'
    return label[0]
def clean_text(text):
    words = tokenization(text)
    words = clean(words)
    words = lowercasing(words)
    words = remove_stop_words(words)
    words = stemming(words)
    #words = lemmatisation(words)
    return ' '.join(words)

def pack_data(dataframe):
    data = dataframe[['text','labels']]
    data['labels'] = [clean_labels(labels) for labels in data['labels']]
    data['text'] = [clean_text(text) for text in data['text']] 
    return data                 
    
def clean(words):
    #TODO
    return words
    
def lowercasing(words):
    return [word.lower() for word in words]

def tokenization(text):
    return nltk.word_tokenize(text)

def remove_stop_words(words):
    stop_words = stopwords.words('english')
    return [word for word in words if word not in stop_words]

def stemming(words):
    stemmer = PorterStemmer()
    return [stemmer.stem(word) for word in words]

def lemmatisation(words):
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(word) for word in words]
    
