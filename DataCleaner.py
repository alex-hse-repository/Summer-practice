import numpy as np
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import string
#Note: Uncomment to first time usage
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('stopwords')
np.random.seed(42)

def pack(data):
    """
    Perform data preprocessing and add some features.

    Parameters
    ----------
    data : DataFrame with Messages.
   
    """
    data['length'] = [len(text) for text in data['text']] 
    data['longest_word_len'] =  [longest_word_len(text) for text in data['text']] 
    data['mean_word_len'] = [mean_word_len(text) for text in data['text']] 
    data['subject_len'] = [len(subject) for subject in data['subject']]
    data['stop_words_num'] = [stop_words_count(text) for text in data['text']]
    data['pounctuation_num'] = [punctuation_count(text) for text in data['text']]
    data['text'] = [clean_text(text) for text in data['text']]
    
def clean_text(text):
    """
    Perform text normalisation.

    Parameters
    ----------
    text : Text.

    Returns
    -------
    Normalized Text.

    """
    words = tokenization(text)
    words = lowercasing(words)
    words = clean(words)
    words = stemming(words)
    return ' '.join(words)

def longest_word_len(text):
    """
    Find length of the longest word in text.

    Parameters
    ----------
    text : Text.
    
    Returns
    -------
    Length of the longest word.

    """
    return np.max(np.array([len(word) for word in tokenization(text)]))

def mean_word_len(text):
    """
    Find mean length of word in text.

    Parameters
    ----------
    text : Text.
    
    Returns
    -------
    Mean length of word.

    """
    return np.mean(np.array([len(word) for word in tokenization(text)]))  
  
def punctuation_count(text):
    """
    Count the number of punctuations.

    Parameters
    ----------
    text : Text.
    
    Returns
    -------
    Number of punctuations.

    """
    return sum([1 if text[i] in string.punctuation else 0 for i in range(len(text))])

def stop_words_count(text):
    """
    Count the number of stop-words in text.

    Parameters
    ----------
    text : Text.
    
    Returns
    -------
    Number of stop-words.

    """
    words = tokenization(text)
    stop_words = stopwords.words('english')
    return len([word for word in words if word not in stop_words])
    
def clean(words):
    """
    Remove non-literal symbols from tokenized text.
    
    Parameters
    ----------
    words : List of words.
    
    Returns
    -------
    tockens: List of processed words.
    """
    tokens = []
    try:
        for token in words:
            token = re.sub(r'[\W\d_]', " ", token)
            tokens.append(token)
    except:
        token = ""
        tokens.append(token)
    
    return tokens

    
def lowercasing(words):
    """
    Lowercase words.

    Parameters
    ----------
    words : List of words.

    Returns
    -------
    List of lowercased words.
    """
    return [word.lower() for word in words]

def tokenization(text):
    """
    Tokenize Text.

    Parameters
    ----------
    text : Text.
    
    Returns
    -------
    Tokenized Text.
    """
    return nltk.word_tokenize(text)

def stemming(words):
    """
    Perform stemming.

    Parameters
    ----------
    words : List of words.

    Returns
    -------
    List of stemmed words.
    """
    stemmer = SnowballStemmer('english')
    return [stemmer.stem(word) for word in words]
