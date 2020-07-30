from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV 
import numpy as np
np.random.seed(42)
class Model:
       
    def __init__(self,main_transformer,small_transformer,alpha,beta):
        """
        Parameters
        ----------
        main_transformer : Instance of fitted transformer for "main" categories.
        small_transformer : Instance of fitted transformer for "small" categories.
        alpha : Confidence parameter for "main" categories from 0 to 1.
        beta : Confidence parameter for "small" categories from 0 to 1.
        
        """
        self.alpha = alpha
        self.beta = beta
        self.main_transformer = main_transformer
        self.small_transformer = small_transformer
        #Wrapper to add probability estimations of the predictions(OvR is set on default)
        self.model_main = CalibratedClassifierCV(LinearSVC(C=2.275,intercept_scaling=0.1),cv = 5)
        self.model_small = CalibratedClassifierCV(LinearSVC(C=1.55,intercept_scaling=0.1),cv = 3)
      
             
    def fit(self,X_main,y_main,X_small,y_small):
        """
        Fit the model.

        Parameters
        ----------
        X_main, y_main: Vectorized data and target for main categories.
        X_small,y_small : Vectorized data and target for main categories.
        
        Returns
        -------
        Self.
        
        """  
        if(self.main_transformer!=None):
            self.model_main.fit(X_main,y_main)
        if(self.small_transformer!=None):    
            self.model_small.fit(X_small,y_small)
        return self
        
        
    def predict(self,unlabeled):
        """
        Predict labels for unlabeled mails.

        Parameters
        ----------
        unlabeled : DataFrame with unlabeled mails
        
        Returns
        -------
        y_pred : List with predicted labels.Some mails might be left unlabeled 
        because of the confidence parameters.

        """
        y_pred = unlabeled['label']
        if(self.main_transformer!=None):
            X,y = self.main_transformer.transform(unlabeled)
            y_pred = self.model_main.predict(X)
            pred_probs = self.model_main.predict_proba(X)
            for i,probs in enumerate(pred_probs):
                if(max(probs)<self.alpha):
                    y_pred[i] = 'Unsorted'
        unsorted = unlabeled.loc[y_pred == 'Unsorted']
        if(self.small_transformer!=None and len(unsorted)!=0):
            X,y = self.small_transformer.transform(unsorted)
            y = self.model_small.predict(X)
            pred_probs = self.model_small.predict_proba(X)
            for i,probs in enumerate(pred_probs):
                if(max(probs)<self.beta):
                    y[i] = 'Unsorted'
            y_pred[y_pred=='Unsorted'] = y
        return y_pred
                
