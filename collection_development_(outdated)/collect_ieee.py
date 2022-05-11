# Imports
import pandas as pd
import re
from datetime import datetime, timedelta
import time
import json
from os import listdir, path
from os.path import isfile, join

import requests
from bs4 import BeautifulSoup as soup
import lxml
from fake_useragent import UserAgent

# prep for import of own scripts
# #this only needs to be done because module not in same place as this py
import sys
sys.path.insert(0, '.')

# Importing functions from our own modules
from utils.collection_utils import datetime_parse

def ieee_searcher(base_url, search_terms, days_back=30):
      '''
      Collects from IEEE spectrum using search terms
      Only returns first ~4 entries so must be run regularily
      '''
      # Further URL parts
      query_url = 'search/?q='
      C = "&"
      sort_criteria = "order=newest"

      # Lists for saving to
      title_list = []
      url_list = []
      date_list = []

      for term in search_terms['search_term']:
            
            # Putting together final url
            final_url = base_url + query_url + term + C + sort_criteria
            print(final_url)

            # Setting up fake user agent to have a proper header
            ua = UserAgent(verify_ssl=False, cache=False)
            user_agent = ua.random
            header = {'User-Agent': user_agent}

            # Making request and saving HTML of request
            ######################
            # TO DO - why am I posting? maybe just tired
            ######################
            response = requests.post(final_url, headers=header)
            html = soup(response.text, 'lxml')
            
            #Getting all stories
            objects = html.find_all('div',  class_='section_column')#elid=True)#class_= 'clearfix')

            for obj in objects:
                  #going down a level for actual content of interest (possible we would move this to "objects" and skip)
                  items = obj.find_all('div', id='col-right')

                  # Looping through stories to get details
                  for i in items:
                        title_list.append(i.h2.text)
                        url_list.append(i.h2.a['href'])
                        date = i.find_all('div', class_="social-date")
                  
                        for d in date:
                              # Parsing date
                              try: 
                                    # Not working well
                                    d_parsed = datetime_parse(d.text)
                                    date_list.append(d_parsed[0])
                              except:
                                    date_list.append('None')
      # Putting lists in Dataframe                        
      df_collected = pd.DataFrame(list(zip(title_list, url_list, date_list)), 
                  columns=['title', 'url', 'date',])      
      
      # List to save text to
      relevant_text = []

      # Preping above list fo dictionary conversion
      relevant_text.append(['title', 'url', 'date', 'text'])
      
      # Looping through Dataframe to get text 
      for index, row in df_collected.iterrows():
            # Only getting text from articles within timedelta = your search frequency
            if row.date >= today - timedelta(days_back):
                  print('Fetching: ' + row.url)

                  response = requests.post(row.url) #headers=header)
                  html = soup(response.text, 'lxml')

                  objects = html.find_all('div', id="col-center")
                  article_text = []

                  # Getting all the text from the 'p' tags
                  for obj in objects:
                        paragraph_text = obj.find_all('p')
                        for p in paragraph_text:
                              article_text.append(p.text)
                  article_text = ' '.join(article_text)

                  # Saving that text only if our search term appears in it
                  # In principle for IEEE this is not needed, given the original collection uses search url
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
      
      # Making a new DataFrame with only relavant texts
      new_df = pd.DataFrame(relevant_text[1:],columns=relevant_text[0])
      
      # Saving, as new if not exists, concating if file exists already
      save_path = DATA_PATH + 'ieee_data.csv'
      
      if path.isfile(save_path):
            old_df = pd.read_csv(save_path)
            combined_df = pd.concat([new_df, old_df])
            combined_df.drop_duplicates(subset='url', inplace=True)
            combined_df.to_csv(save_path, index=False)
      else:
            new_df.to_csv(save_path, index=False)

if __name__ == '__main__':
      # Paths, dir_path currently not needed
      dir_path = path.dirname(path.realpath(__file__))
      DATA_PATH = './data/'
      IN_DATA_PATH = './data/input_data/'
      
      # Getting today's date to compute how far back to collect
      today = datetime.now()

      # Getting base url from json
      load_file = IN_DATA_PATH + 'collection_urls_dict.json'
      with open(load_file) as handle:
            sources = json.loads(handle.read())
      base_url = sources['IEEE_spectrum']

      # Getting search terms from json
      load_file = IN_DATA_PATH + 'collection_searchterms.json'
      with open(load_file) as handle:
            search_terms = json.loads(handle.read())

      # Run
      ieee_searcher(base_url, search_terms, days_back=30)