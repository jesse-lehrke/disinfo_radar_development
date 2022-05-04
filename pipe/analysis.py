import pandas as pd
from os import path, listdir
from os.path import isfile, join

# To load models
import joblib

# For new columns
from datetime import datetime

#from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

from collections import Counter


# Paths, DO - send compiled data to seperate folder
dir_path = path.dirname(path.realpath(__file__))
DATA_PATH = dir_path + '/data/final/'
IN_DATA_PATH = dir_path + '/data/input_data/'
MODEL_PATH = dir_path + '/data/models/'


# load test_compiled.csv
# Load dataframe
filename = 'test_compiled.csv'
CONVERTERS = {'tokens': eval}

df = pd.read_csv(DATA_PATH + filename, converters=CONVERTERS)

# Load vectorizers, selectors, model etc.
## Check files in data folder - will develop into something for py script
models = [f for f in listdir(MODEL_PATH) if isfile(join(MODEL_PATH, f))]

print('Index, Model Name')
print(list(zip([index for index, value in enumerate(models)], models)))

vector_name = models[1]
model_name = models[0]

## Load
vectorizer = joblib.load(MODEL_PATH + vector_name)
model = joblib.load(MODEL_PATH + model_name)

# transform data and run data through model
categories = []

for index, row in df.iterrows():
      
      print('Transform-Predict: Index ' + str(index) + ' / ' + row.url + ' @ ' + str(datetime.now()))

      row_data = [' '.join(row.tokens)]
      #row_data = [' '.join(df.hard_tokens[index])]

      # If selector used (and load it of course!)
      #transformed_row = selector.transform(vectorizer.transform(row_data))
      transformed_row = vectorizer.transform(row_data)
      
      predicted = model.predict(transformed_row) # 0:feature, 2:feature
      
      print("Predicted Value:", predicted[0])
      categories.append(predicted[0])

      print("---------------------------")

print(Counter(categories))

# For sigmoid models or similar

# categories_sig = [] 
# probabilities = []
# max_probability = []

# for index, row in df.iterrows():
      
#       print('Transform-Predict: Index ' + str(index) + ' / ' + row.url + ' @ ' + str(datetime.now()))

#       row_data = [' '.join(row.tokens)]

#       # Note different from other models here with .toarray
#       transformed_row = selector.transform(vectorizer.transform(row_data)).toarray()
      
#       predicted = sig_model.predict(transformed_row)
#       predicted_proba = sig_model.predict_proba(transformed_row)

#       print("Predicted Value:", predicted[0])
#       categories_csb.append(predicted[0])
#       print("Predicted Value:", list(predicted_proba[0]))
#       probabilities.append(list(predicted_proba[0]))
      
#       max_probability.append(max(list(predicted_proba[0])))

#       print("---------------------------")

# Save results - new csv, likely persist, include "date_classified" columns = datetime.now

df['category'] = categories
# df['category_sig'] = categories_sig
# df['probabilities'] = probabilities
# df['max_probability'] = max_probability

# likely should rename, with date and put in new folder with all dated csv files
df.to_csv(DATA_PATH + 'test_output.csv', index=False)