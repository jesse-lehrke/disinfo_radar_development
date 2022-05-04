'''
Add search term/ filter check
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

# Importing functions from our own modules
from utils_conversion import get_pdfs, pdf_to_text, text_to_csv, bulk_pdf_to_text

# Paths
dir_path = path.dirname(path.realpath(__file__))
DATA_PATH = dir_path + '/data/'
IN_DATA_PATH = dir_path + '/data/input_data/'

def cna_searcher(base_url, scraped_times, search_terms):
      '''
      Doc string here
      '''
      # Create fake user agent
      ua = UserAgent(verify_ssl=False, cache=False)
      user_agent = ua.random
      header = {'User-Agent': user_agent}
      
      # This can help get through some security
      # Have not used everywhere, but no reason you cannot      
      ssl._create_default_https_context = ssl._create_unverified_context

      response = requests.get(base_url, headers=header)

      html = soup(response.text, 'lxml')

      title_list = []
      url_list = []
      date_list = []

      objects = html.find_all('div', id='newsletters')

      for obj in objects:
            items = obj.find_all('li')
            for i in items:
                  title_list.append(i.text)
                  urls = i.find_all('a', href=True)

                  url_list.append('https://www.cna.org' + urls[0]['href'])

                  date = i.text
                  date = date.split(': ')[1]
                  date = date.split(' [')[0]
                  date_parsed = datetime.strptime(date, '%B %d, %Y')
                  date_list.append(date_parsed)

      df_collected = pd.DataFrame(list(zip(title_list, url_list, date_list)), 
                  columns=['title', 'url', 'date'])

      # Getting last collection time, if none, getting oldest date in results
      try:
            last_collected = datetime.strptime(scraped_times[base_url],'%Y-%m-%dT%H:%M:%SZ')
      except:
            last_collected = min(list(df_collected.date))
      
      # Filtering dates here, could be done after collection but would need good reason
      new_df = df_collected[df_collected.date >= last_collected]
      
      # PDF Work
      QUERY = 'CNA' # should we seperate Russia and China?

      get_pdfs(DATA_PATH, QUERY, new_df)
      
      bulk_pdf_to_text(DATA_PATH, QUERY)
      #pdf_to_text(DATA_PATH, QUERY)
      
      df_temp = text_to_csv(DATA_PATH, QUERY)

      #try:
      new_df['text'] = df_temp
      
      save_path = DATA_PATH + 'cna' + '_data.csv'
      
      if path.isfile(save_path):
            old_df = pd.read_csv(save_path)
            combined_df = pd.concat([new_df, old_df])
            combined_df.drop_duplicates(subset='url', inplace=True)
            combined_df.to_csv(save_path, index=False)
      else:
            new_df.to_csv(save_path, index=False)
      # except:
      #       print('No new PDFs')

      # Saving collection time
      scraped_times[base_url] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') 
      with open(IN_DATA_PATH + 'scraped_times.json', 'w', encoding='utf8') as f:
            json.dump(scraped_times, f, indent=2, ensure_ascii=False)

      # TO DO Should we filter for keywords then? Or want it all?

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
      
      base_url_1 = sources['CNA_Russia']
      base_url_2 = sources['CNA_China']

      # NOT YET NEEDED
      load_file = IN_DATA_PATH + 'collection_searchterms.json'
      with open(load_file) as handle:
            search_terms = json.loads(handle.read())

      cna_searcher(base_url_1, scraped_times, search_terms)
      cna_searcher(base_url_2, scraped_times, search_terms)