# Imports

import requests
from bs4 import BeautifulSoup as soup
import lxml
import pandas as pd

from datetime import datetime, timedelta
import json
import time
from os import listdir, path
from os.path import isfile, join
import os


# prep for import of own scripts
import sys
sys.path.insert(0, '.')

# Own scripts and their dependencies
from utils.collection_utils import datetime_parse
#from itertools import combinations, permutations, chain
#import re

def importai_searcher(base_url, search_terms):
      # Lists for saving collected data

      title_list = []
      url_list = []
      dates = []

      response = requests.post(base_url) #headers=header)

      html = soup(response.text, 'lxml')

      objects = html.find_all('li', class_="campaign")
      for obj in objects:
            print(obj.text)
            print(obj.a['href'])
            title_list.append(obj.text)
            url_list.append(obj.a['href'])
            for item in title_list:
                  date_sequence = datetime_parse(item)
                  dates.append(date_sequence[0])

      df_collected = pd.DataFrame(list(zip(title_list, url_list, dates)), 
            columns=['title', 'url', 'date'])           

      # List to save to
      relevant_text = []

      #preping list fo dictionary conversion
      relevant_text.append(['title', 'url', 'date', 'text'])

      # Gets text for results within timedelta window
      #     This is probably best changed to a "last scraped" date from a json

      for index, row in df_collected.iterrows():
            if row.date >= today - timedelta(days=30):
                  print('Fetching: ' + row.url)
                  response = requests.post(row.url) #headers=header)

                  html = soup(response.text, 'lxml')

                  objects = html.find_all('p')#, class_="campaign")
                  issue_text = []
                  for obj in objects:
                        issue_text.append(obj.text)
                  issue_text = ' '.join(issue_text)
                  
                  for word in search_terms['search_term']:
                        if word in issue_text:
                              save = list(row)
                              save.append(issue_text)
                              relevant_text.append(save)                  
                              print('Search term found: ' +  word)
                              break
                        else: 
                              pass
                  time.sleep(5)
            else:
                  pass
      new_df = pd.DataFrame(relevant_text[1:],columns=relevant_text[0])
      
      #########
      save_path = DATA_PATH + 'importai_data.csv'
      
      if path.isfile(save_path):
            old_df = pd.read_csv(save_path)
            combined_df = pd.concat([new_df, old_df])
            combined_df.drop_duplicates(subset='url', inplace=True)
            combined_df.to_csv(save_path, index=False)
      else:
            new_df.to_csv(save_path, index=False)

if __name__ == '__main__':
      # for the future
      dir_path = path.dirname(path.realpath(__file__))
      DATA_PATH = './data/'
      IN_DATA_PATH = './data/input_data/'
      
      today = datetime.now()

      load_file = IN_DATA_PATH + 'collection_urls_dict.json'

      with open(load_file) as handle:
            sources = json.loads(handle.read())
      
      base_url = sources['Import_AI']

      load_file = IN_DATA_PATH + 'collection_searchterms.json'

      with open(load_file) as handle:
            search_terms = json.loads(handle.read())

      importai_searcher(base_url, search_terms)