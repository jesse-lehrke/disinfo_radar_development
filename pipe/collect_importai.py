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

def importai_searcher(base_url, search_terms, scraped_times):
      # Lists for saving collected data
      title_list = []
      url_list = []
      dates = []

      # Making request and getting html
      response = requests.post(base_url) #headers=header)
      html = soup(response.text, 'lxml')

      # Getting the data we need
      objects = html.find_all('li', class_="campaign")
      for obj in objects:
            #print(obj.text)
            #print(obj.a['href'])
            title_list.append(obj.text)
            url_list.append(obj.a['href'])
      
      for item in title_list:
            date = item.split(' -')[0]
            date_parsed = datetime.strptime(date, '%m/%d/%Y')
            #print(date_parsed)
            dates.append(date_parsed)

      # Saving to dataframe
      df_collected = pd.DataFrame(list(zip(title_list, url_list, dates)), 
            columns=['title', 'url', 'date'])           
      
      # List to save next data and preping list for dictionary conversion
      relevant_text = []
      relevant_text.append(['title', 'url', 'date', 'text'])
      
      # Getting last collection time, if none, getting oldest date in results
      try:
            last_collected = datetime.strptime(scraped_times[base_url],'%Y-%m-%dT%H:%M:%SZ')
      except:
            last_collected = min(list(df_collected.date))
            #print(last_collected)

      # Gets text for results within timedelta window
      for index, row in df_collected.iterrows():
            if row.date > last_collected:
                  print('Fetching: ' + row.url)
                  response = requests.post(row.url)

                  html = soup(response.text, 'lxml')

                  objects = html.find_all('p')#, class_="campaign")
                  issue_text = []
                  for obj in objects:
                        issue_text.append(obj.text)
                  issue_text = ' '.join(issue_text)

                  # Saving that text only if our search term appears in it                  
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
      
      # Final dataframe
      new_df = pd.DataFrame(relevant_text[1:],columns=relevant_text[0])
      
      # Saving, as new if not exists, concating if file exists already
      save_path = DATA_PATH + 'importai_data.csv'
      
      if path.isfile(save_path):
            old_df = pd.read_csv(save_path)
            combined_df = pd.concat([new_df, old_df])
            combined_df.drop_duplicates(subset='url', inplace=True)
            combined_df.to_csv(save_path, index=False)
      else:
            new_df.to_csv(save_path, index=False)
     
      # Saving collection time
      scraped_times[base_url] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') 
      with open(IN_DATA_PATH + 'scraped_times.json', 'w', encoding='utf8') as f:
            json.dump(scraped_times, f)

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
      
      # Getting base url from json
      load_file = IN_DATA_PATH + 'collection_urls_dict.json'
      with open(load_file) as handle:
            sources = json.loads(handle.read())
      
      base_url = sources['Import_AI']
      
      # Getting search terms from json
      load_file = IN_DATA_PATH + 'collection_searchterms.json'
      with open(load_file) as handle:
            search_terms = json.loads(handle.read())

      # Run
      importai_searcher(base_url, search_terms, scraped_times)