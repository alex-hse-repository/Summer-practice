from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import pandas as pd

def transform(data):
    '''Transfor data('text','label') to X,y'''
    tfidf_vectorizer = TfidfVectorizer()
    label_encoder = LabelEncoder()
    labels = label_encoder.fit_transform(data['label'])
    texts = tfidf_vectorizer.fit_transform(data['text'])
    feature_names = tfidf_vectorizer.get_feature_names()    
    X = pd.DataFrame(texts.toarray(),columns = feature_names)
    y = labels
    return X,y


