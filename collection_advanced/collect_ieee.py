# Imports
import pandas as pd
import re
from datetime import datetime, timedelta
from fake_useragent import UserAgent
import time
from os import listdir, path
from os.path import isfile, join

import requests
from bs4 import BeautifulSoup as soup
import lxml

import json

# prep for import of own scripts
import sys
sys.path.insert(0, '.')

from utils.collection_utils import datetime_parse

def ieee_searcher(base_url, search_terms):
      query_url = 'search/?q='
      C = "&"
      sort_criteria = "order=newest"

      title_list = []
      url_list = []
      date_list = []

      for term in search_terms['search_term']:
      
            final_url = base_url + query_url + term + C + sort_criteria
            print(final_url)
            #search_terms['search_term']
            ua = UserAgent(verify_ssl=False, cache=False)

            user_agent = ua.random
            header = {'User-Agent': user_agent}

            response = requests.post(final_url, headers=header)

            html = soup(response.text, 'lxml')
            
            objects = html.find_all('div',  class_='section_column')#elid=True)#class_= 'clearfix')

            for obj in objects:
                  items = obj.find_all('div', id='col-right')
                  for i in items:

                        #print(i.h2.text)
                        title_list.append(i.h2.text)

                        #print(i.h2.a['href'])
                        url_list.append(i.h2.a['href'])

                        #date = i.div.span
                        date = i.find_all('div', class_="social-date")
                        for d in date:
                              print(d.text)
                              try: 
                                    #not working well
                                    d_parsed = datetime_parse(d.text)
                                    date_list.append(d_parsed[0])
                              except:
                                    date_list.append('None')
                              
      df_collected = pd.DataFrame(list(zip(title_list, url_list, date_list)), 
                  columns=['title', 'url', 'date',])      
      
      print(df_collected.head())
      # List to save to
      relevant_text = []

      #preping list fo dictionary conversion
      relevant_text.append(['title', 'url', 'date', 'text'])
      
      for index, row in df_collected.iterrows():
            if row.date >= today - timedelta(days=30):
                  print('Fetching: ' + row.url)
                  response = requests.post(row.url) #headers=header)

                  html = soup(response.text, 'lxml')

                  objects = html.find_all('div', id="col-center")
                  article_text = []
                  for obj in objects:
                        paragraph_text = obj.find_all('p')
                        for p in paragraph_text:
                              article_text.append(p.text)
                  article_text = ' '.join(article_text)
      
                  for word in search_terms['search_term']:
                        if word in article_text:
                              save = list(row)
                              save.append(article_text)
                              relevant_text.append(save)                  
                              print('Search term found: ' +  word)
                              break
                  else: 
                        pass

                  time.sleep(5)
            else:
                  pass
      ####   
      new_df = pd.DataFrame(relevant_text[1:],columns=relevant_text[0])
      save_path = DATA_PATH + 'ieee_data.csv'
      
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
      
      base_url = sources['IEEE_spectrum']

      load_file = IN_DATA_PATH + 'collection_searchterms.json'

      with open(load_file) as handle:
            search_terms = json.loads(handle.read())

      ieee_searcher(base_url, search_terms)