import Loader
import DataCleaner
import DataTransformer
import pandas as pd
import numpy as np
import matplotlib as mpl
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix,auc

data = Loader.load_all()
data = DataCleaner.pack_data(data)
X,y = DataTransformer.transform(data)

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size = 0.2,random_state = 42)

linear_clf = LogisticRegression()

linear_clf.fit(X_train,y_train)
y_pred = linear_clf.predict(X_test)
confm = confusion_matrix(y_test, y_pred)
print(cross_val_score(linear_clf, X, y,cv = 3))


