from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.preprocessing import MinMaxScaler,OneHotEncoder
import pandas as pd
import numpy as np

class MainTransformer:
    """
    Vectorizer for mails in "main" categories.
    
    """
    def __init__(self):
        self.transformer = TfidfVectorizer()
        
    def fit(self,data):
        """
        Fit transformer on "text" column of data.

        Parameters
        ----------
        data : DataFrame with "text" column.

        Returns
        -------
        Self.
        
        """
        self.transformer.fit(data['text'])
        return self
    
    def transform(self,data):
        """
        Vectorize "text" column of the data and split data 

        Parameters
        ----------
        data : DataFrame with "text" column.

        Returns
        -------
        X : Vectorized text(data).
        y : Labels(target).
        """
        
        X = self.transformer.transform(data['text']).toarray()
        y = data['label']
        return X,y

class SmallTransformer:
    """
    Vectorizer for mails in "small" categories.
    
    """
    
    def __init__(self):
        self.transformer = TfidfVectorizer()
        self.scaler = MinMaxScaler()
        self.encoder = OneHotEncoder()
        
    def fit(self,data):
        """
        Fit transformers on "text" column and 
        columns with additional featuresof data.

        Parameters
        ----------
        data : DataFrame with "text" column and columns with additional features.

        Returns
        -------
        Self.
        
        """
       
        self.transformer.fit(data['text'])
        self.scaler.fit(data[['length','longest_word_len','mean_word_len','subject_len',
                    'stop_words_num','pounctuation_num']])
        self.encoder.fit(np.array(data['sender']).reshape(-1,1))
        return self 
    
    def transform(self,data):
        """
        Vectorize "text" column of the data,scale the additional features, 
        perform one-hot-encoding for "sender" feature and split data.

        Parameters
        ----------
        data : DataFrame with "text" column and columns with additional features.

        Returns
        -------
        X : Vectorized data(data).
        y : Labels(target).
        """
        
        text = self.transformer.transform(data['text']).toarray()
        additional_features = self.scaler.transform(data[['length','longest_word_len','mean_word_len','subject_len',
                    'stop_words_num','pounctuation_num']])
        senders = self.encoder.transform(np.array(data['sender']).reshape(-1,1)).toarray()
        X = pd.DataFrame(np.concatenate((text,additional_features,senders),axis = 1))
        y = data['label']
        return X,y
    
    
 