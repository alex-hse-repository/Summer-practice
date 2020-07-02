import Loader
import pandas as pd
import numpy as np
import matplotlib as mpl

service = Loader.Authorize()
message_list = Loader.ListMessages(service)
df = pd.DataFrame()
test = Loader.load_message(service,message_list[0]['id'])
df = df.append(test,ignore_index = True)
print(df)

