import pandas as pd

from os import listdir
from os.path import isfile, join

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
      cleaned_text = text.lower() # lower case
      cleaned_text = cleaned_text.replace("\n", " ")
      cleaned_text = cleaned_text.replace("\t", " ")
      cleaned_text = cleaned_text.replace('\r', '')

      cleaned_text = re.sub('[^\S\r\n]{2,}', ' ', cleaned_text) # extra spaces
      cleaned_text = cleaned_text.rstrip()
      
      return cleaned_text

def remove_punctuation(txt):
      txt_nopunct = ''.join([c for c in txt if c not in final_punctuation])
      
      return txt_nopunct

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
      """https://spacy.io/api/annotation"""
      doc = nlp("".join(texts)) #nlp(sent) #" ".join(sent)) 
      texts_out = [token.lemma_ for token in doc if token.pos_ in allowed_postags or token.text in to_keep]
      return texts_out

def remove_stopwords(txt):
      txt_nostops = [w for w in txt if not w in final_stop_words]
      #txt_nostops = ' '.join([w for w in txt if not w in stop_words]) # Alternate
      return txt_nostops

def remove_numbers(txt):
      '''
      TO-DO Not checked 
      '''
      result = ''.join([i for i in txt if not i.isdigit()])    
      return result

def get_tag(x):
      '''
      For ArXiv only
      '''
      tag = x[0]['term']
      # TO DO - scrape https://arxiv.org/category_taxonomy to translate codes to plain english
      return tag

def pre_process(df, action_col = 'text', filetype = 'csv', load = False):
      if load == True:
            if filetype == 'json':
                  df = pd.read_json(DATA_PATH + load_file, convert_dates=True, lines=True, orient='records')
            else:
                  CONVERTERS = {'tags': eval, 'arxiv_primary_category': eval,"published_parsed": eval}
                  df = pd.read_csv(OUTPUT_PATH + load_file, converters=CONVERTERS)
      
      df['cleaning'] = df[action_col].dropna().apply(lambda x: cleaning(x))

      special_punctuation = '：，,《。》“„:一・«»”“]'
      final_punctuation = string.punctuation + special_punctuation

      df['cleaning'] = df['cleaning'].dropna().apply(lambda x: remove_punctuation(x))

      df['lemma_text'] = df['cleaning'].dropna().apply(lambda x:  lemmatization(x, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']))

      lang = 'english'
      stop_words = list(stopwords.words(lang))
      # add in anything else we need to remove, eg. for some analysis, any search tags would be dropped from text
      new_stop_words = [] 
      final_stop_words = stop_words + new_stop_words
      
      # TO-DO move before lemmatization?
      df['tokens'] = df['lemma_text'].dropna().apply(lambda x:  remove_stopwords(x))

      # TO-DO make some try-except or conditional "if"
      df['category'] = df['tags'].dropna().apply(lambda x:  get_tag(x))

if __name__ == '__main__':
      # Paths
      dir_path = path.dirname(path.realpath(__file__))
      DATA_PATH = dir_path + '/data/'
      IN_DATA_PATH = dir_path + '/data/input_data/'
      OUTPUT_PATH = dir_path + '/data/raw/'

      nlp = spacy.load("en_core_web_sm") # disable=['parser', 'ner']) ## if you need efficiency

      # TO-DO: Move to json and load
      to_keep = ["GAN", "GPT-3", "fake news", "disinformation"]

