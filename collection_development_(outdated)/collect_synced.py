# Imports

import requests
from bs4 import BeautifulSoup as soup
import lxml
from fake_useragent import UserAgent

import pandas as pd

from os import listdir, path
from datetime import datetime, timedelta
import json
import time

# prep for import of own scripts
# #this only needs to be done because module not in same place as this py
import sys
sys.path.insert(0, '.')

# Importing functions from our own modules
from utils_collection import datetime_parse
#from itertools import combinations, permutations, chain


def synced_searcher(base_url,search_terms, scraped_times):
      # Dates to build current url
      year = datetime.now().year
      month = datetime.now().month
      current_url = base_url + str(year) + '/' +  str(month) + '/'

      # lists for saving
      title_list = []
      url_list = []
      summary_list = []
      date_list = []

      # Create fake user agent
      ua = UserAgent(verify_ssl=False, cache=False)
      user_agent = ua.random
      header = {'User-Agent': user_agent}

      # Making request and saving html
      response = requests.post(current_url, headers=header)
      html = soup(response.text, 'lxml')

      # Getting the data we need
      obj = html.find('div',id= "primary")       

      dates = obj.find_all(class_='entry-date')
      for d in dates:
            print(d)
            d_parsed = datetime_parse(d.text)
            date_list.append(d_parsed[0])

      titles = obj.find_all(class_='entry-title')
      for t in titles:
            title_list.append(t.text)
            url_list.append(t.a['href'])

      summaries = obj.find_all(class_='entry-summary')
      for s in summaries:
            summary_list.append(s.text)

      # Saving to dataframe
      df_collected = pd.DataFrame(list(zip(title_list, url_list, date_list, summary_list)), 
                  columns=['title', 'url', 'date', 'summary'])

      # Making list to store new data and preping for dict conversion      
      relevant_text = []
      relevant_text.append(['title', 'url', 'date', 'summary', 'text'])
      
      # Getting last collection time, if none, getting oldest date in results
      try:
            last_collected = datetime.strptime(scraped_times[base_url],'%Y-%m-%dT%H:%M:%SZ')
      except:
            last_collected = min(list(df_collected.date))

      # Getting texts if date in range then checking for search terms      
      for index, row in df_collected.iterrows():
            if row.date >= last_collected:
                  print('Fetching: ' + row.url)
                  response = requests.post(row.url) #headers=header)

                  html = soup(response.text, 'lxml')

                  objects = html.find_all('div', class_="entry-content")
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
      
      #Creating final dataframe
      new_df = pd.DataFrame(relevant_text[1:],columns=relevant_text[0])

      # Saving, as new if not exists, concating if file exists already
      save_path = DATA_PATH + 'synced_data.csv'
      
      if path.isfile(save_path):
            old_df = pd.read_csv(save_path)
            combined_df = pd.concat([new_df, old_df])
            combined_df.drop_duplicates(subset='url', inplace=True)
            combined_df.to_csv(save_path, index=False)
      else:
            new_df.to_csv(save_path, index=False)

if __name__ == '__main__':
      # Paths
      dir_path = path.dirname(path.realpath(__file__))
      DATA_PATH = dir_path + '/data/'
      IN_DATA_PATH = dir_path + '/data/input_data/'
      
      # Getting last collection date, if none initializing dictionary
      try:
            with open(IN_DATA_PATH + 'scraped_times.json') as f:
                  scraped_times = json.load(f)     
      except:
            with open(IN_DATA_PATH + 'scraped_times.json', 'w', encoding='utf8') as f:
                  init_dict = {}
                  json.dump(init_dict, f)
            with open(IN_DATA_PATH + 'scraped_times.json') as f:
                  scraped_times = json.load(f)        
      # Getting today's date to compute url and how far back to collect
      #today = datetime.now()

      # Getting base url from json
      load_file = IN_DATA_PATH + 'collection_urls_dict.json'

      with open(load_file) as handle:
            sources = json.loads(handle.read())
      
      base_url = sources['Synced']

      # Getting search terms from json
      load_file = IN_DATA_PATH + 'collection_searchterms.json'

      with open(load_file) as handle:
            search_terms = json.loads(handle.read())
      
      # Run
      synced_searcher(base_url, search_terms, scraped_times)