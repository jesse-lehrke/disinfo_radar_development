import pandas as pd

from os.path import isfile, join
from os import listdir, path

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import string
import spacy
import re

# INSTALL FIRST:
# nltk.download('stopwords')
# python -m spacy download en_core_web_sm

def cleaning(text):
      cleaned_text = text.replace("\n", " ")
      cleaned_text = cleaned_text.replace("\t", " ")
      cleaned_text = cleaned_text.replace('\r', '')

      cleaned_text = re.sub('[^\S\r\n]{2,}', ' ', cleaned_text) # extra spaces
      cleaned_text = cleaned_text.rstrip()
      
      return cleaned_text

def lower_case(text):
      cleaned_text = text.lower() # lower case
      return cleaned_text

def delete_hyperlinks(text):
      '''
      Only with http (so not e.g www.cna.org), but could add easily
      Note if hyperlink breaks accross a page, it misses it and leaves long messy tokens
      These should somehow be dealt with
      '''
      #cleaned_text = re.sub(r"http\S+", "", text)
      cleaned_text = re.sub("(?P<url>https?://[^\s]+)", "", text)
      return cleaned_text

def remove_punctuation(txt):
      special_punctuation = '：，,《。》“„:一・«»”“]'
      final_punctuation = string.punctuation + special_punctuation
      txt_nopunct = ''.join([c for c in txt if c not in final_punctuation])
      
      return txt_nopunct

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
      """https://spacy.io/api/annotation"""
      doc = nlp("".join(texts)) #nlp(sent) #" ".join(sent)) 
      texts_out = [token.lemma_ for token in doc if token.pos_ in allowed_postags or token.text in to_keep]
      return texts_out

def remove_stopwords(txt):
      # add in anything else we need to remove, eg. for some analysis, any search tags would be dropped from text
      new_stop_words = [] 

      lang = 'english'
      stop_words = list(stopwords.words(lang))
      final_stop_words = stop_words + new_stop_words

      txt_nostops = [w for w in txt if not w in final_stop_words]
      #txt_nostops = ' '.join([w for w in txt if not w in stop_words]) # Alternate
      return txt_nostops

def remove_numbers(txt):
      '''
      TO-DO Not checked as likely dropped for lemmatization, POS tagging
      '''
      result = ''.join([i for i in txt if not i.isdigit()])    
      return result

def get_tag(x):
      '''
      For ArXiv only, no implemented
      '''
      tag = x[0]['term']
      # TO DO - scrape https://arxiv.org/category_taxonomy to translate codes to plain english
      return tag

def pre_process(df, key, action_col = 'text', filetype = 'csv', load = False):
      if load == True:
            if filetype == 'json':
                  df = pd.read_json(DATA_PATH + load_file, convert_dates=True, lines=True, orient='records')
            else:
                  CONVERTERS = {'tags': eval, 'arxiv_primary_category': eval,"published_parsed": eval}
                  df = pd.read_csv(OUTPUT_PATH + load_file, converters=CONVERTERS)
      
      df['cleaning'] = df[action_col].dropna().apply(lambda x: cleaning(x))

      df['processing'] = df['cleaning'].dropna().apply(lambda x: lower_case(x))
      
      df['processing'] = df['processing'].dropna().apply(lambda x: delete_hyperlinks(x))

      df['processing'] = df['processing'].dropna().apply(lambda x: remove_punctuation(x))

      df['processing'] = df['processing'].dropna().apply(lambda x:  lemmatization(x, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']))

      # move before lemmatization?
      df['tokens'] = df['processing'].dropna().apply(lambda x:  remove_stopwords(x))
      
      df.drop(columns=['processing'], inplace=True)
      
      # Not needed, if used make a try-except clause
      #df['category'] = df['tags'].dropna().apply(lambda x:  get_tag(x))
      
      # Saving, as new if not exists, concating if file exists already
      #ATTN - IMO do not want to do this! Just save, only merge the archives
      save_path = OUTPUT_PATH + key + '.csv'
      
      if path.isfile(save_path):
            old_df = pd.read_csv(save_path)
            combined_df = pd.concat([df, old_df])
            combined_df.drop_duplicates(subset='links', inplace=True)
            combined_df.to_csv(save_path, index=False)
      else:
            df.to_csv(save_path, index=False)
            
      return df

if __name__ == '__main__':
      # Paths
      dir_path = path.dirname(path.realpath(__file__))
      DATA_PATH = dir_path + '/data/'
      IN_DATA_PATH = dir_path + '/data/input_data/'
      OUTPUT_PATH = dir_path + '/data/final/'

      nlp = spacy.load("en_core_web_sm") # disable=['parser', 'ner']) ## if you need efficiency

      # TO-DO: Move to json and load 
      # But first ? Do we need it? I recommend this be our search_terms...maybe, thus load here
      to_keep = []

      onlyfiles = [f for f in listdir(DATA_PATH) if isfile(join(DATA_PATH, f))]

      # Loads all files in folder into dataframes

      files = [f.split('.')[0] for f in listdir(DATA_PATH) if isfile(join(DATA_PATH, f))]
      print(files)

      dataframe = {}

      for file in files:
            #try:
            dataframe[file] = pd.read_csv(DATA_PATH + file + '.csv', lineterminator='\n') 
            #except:
            #      pass

      dataframe_final= {}
      for key, value in dataframe.items():
            dataframe[key] = pre_process(dataframe[key], key, action_col = 'text', filetype = 'csv', load = False)

      # Get new dfs in new dictionary, merge and export
      df_compiled = pd.concat([v for k,v in dataframe.items()])
      # May prefer to send to a seperate analysis folder
      df_compiled.to_csv(OUTPUT_PATH + 'daily_compiled.csv', index=False)
      
      # REMINDER, archive this before overwriting, and yes, I prefer overwriting
