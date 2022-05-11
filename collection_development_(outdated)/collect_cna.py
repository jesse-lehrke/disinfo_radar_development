'''
FIX PDF parsing for China!
Also search term/ filter check
'''

# Imports
import requests
from bs4 import BeautifulSoup as soup
import lxml
from  urllib.request import urlopen
import ssl
from fake_useragent import UserAgent

import pandas as pd

import shutil
from collections import defaultdict
from pathlib import Path
from os import listdir, path
from datetime import datetime, timedelta
import json


# prep for import of own scripts
# #this only needs to be done because module not in same place as this py
import sys
sys.path.insert(0, '.')

# Importing functions from our own modules
from utils.conversion_utils import get_pdfs, pdf_to_text, text_to_csv
from utils.collection_utils import datetime_parse

def cna_searcher(base_url):
      '''
      Currently gets all issues from CNA
      TO DO: add date functionality
      '''
      # Create fake user agent
      ua = UserAgent(verify_ssl=False, cache=False)
      user_agent = ua.random
      header = {'User-Agent': user_agent}

      response = requests.get(base_url, headers=header)

      html = soup(response.text, 'lxml')

      title_list = []
      url_list = []
      date_list = []

      objects = html.find_all('div', id='newsletters')#elid=True)

      for obj in objects:
            items = obj.find_all('li')
            for i in items:
                  title_list.append(i.text)
                  urls = i.find_all('a', href=True)

                  url_list.append('https://www.cna.org' + urls[0]['href'])

                  date = i.text
                  print(date)
                  try:
                        d_parsed = datetime_parse(date)
                        print(d_parsed)
                        date_list.append(d_parsed[0])
                  except:
                        date_list.append('None')
      
      df_collected = pd.DataFrame(list(zip(title_list, url_list, date_list)), 
                  columns=['title', 'url', 'date'])

      # PDF Work
      QUERY = 'CNA' # should we seperate Russia and China?

      # consider another subfolder then change PATHs
      get_pdfs(DATA_PATH, QUERY, df_collected)
      pdf_to_text(DATA_PATH, QUERY)
      df_temp = text_to_csv(DATA_PATH, QUERY)

      new_df = df_collected[df_collected['date'] >= datetime.now() - timedelta(days=60)]

      new_df['text'] = df_temp
      #new_df = pd.merge(df_collected, df_temp, on='title', how='outer')
        
      save_path = DATA_PATH + 'cna_' + QUERY + '_data.csv'
      
      if path.isfile(save_path):
            old_df = pd.read_csv(save_path)
            combined_df = pd.concat([new_df, old_df])
            combined_df.drop_duplicates(subset='url', inplace=True)
            combined_df.to_csv(save_path, index=False)
      else:
            new_df.to_csv(save_path, index=False)

      # Should we filter for keywords then? Or want it all?

if __name__ == '__main__':
      # for the future
      dir_path = path.dirname(path.realpath(__file__))
      
      DATA_PATH = './data/'
      IN_DATA_PATH = './data/input_data/'
      
      #today = datetime.now()
      #back_to = today.date() - timedelta(days=30)

      # Getting base url from json
      load_file = IN_DATA_PATH + 'collection_urls_dict.json'

      with open(load_file) as handle:
            sources = json.loads(handle.read())
      
      base_url_1 = sources['CNA_Russia']
      base_url_2 = sources['CNA_China']

      # NOT YET NEEDED
      # load_file = IN_DATA_PATH + 'collection_searchterms.json'
      # with open(load_file) as handle:
      #       search_terms = json.loads(handle.read())

      # This can help get through some security
      # Have not used everywhere, but no reason you cannot
      ssl._create_default_https_context = ssl._create_unverified_context

      cna_searcher(base_url_1)
      #cna_searcher(base_url_2) # PDF converter getting syntax errors