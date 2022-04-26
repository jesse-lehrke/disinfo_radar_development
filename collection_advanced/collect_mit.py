
# Imports

import requests
from bs4 import BeautifulSoup as soup
import lxml
import pandas as pd

from os import listdir, path
from datetime import datetime, timedelta
import json

#from fake_useragent import UserAgent

import re
import time

# prep for import of own scripts
import sys
sys.path.insert(0, '.')

# Own scripts and their dependencies
from utils.collection_utils import datetime_parse
#from itertools import combinations, permutations, chain
#import re

def date_from_url(x):
      #def regex(x):
      pat = r"(20[0-2][0-9]([-_/]?)[0-9]{2}(?:\2[0-9]{2})?)"
      dates = re.compile(pat)

      res = dates.search(x)
      res = datetime_parse(res[0])

      return res[0]
      # dates = df['url'].apply(lambda x: regex(x))
      # return dates
      
def get_response(API_Link, pages=1):
    with requests.get(API_Link + '&page=' + str(pages)) as response:
        page_soup = soup(response.content, 'lxml')
        return page_soup

def mit_searcher(API_Link, search_terms):
      # base_url = sources['MIT_Technology_Review']
      # topic_designator = 'topic/'
      topic_tags = ['artificial-intelligence', 'humans-and-technology', 'computing'] 
      # final_url = base_url + topic_designator + topic_tags[0]
   
      responses = []

      for tag in topic_tags:
            response = get_response(API_Link + tag, pages=str(1))

            #parse
            j_response = json.loads(response.text)
            responses = responses + j_response
      
      collected_df = pd.DataFrame(columns=['title', 'url', 'date', 'summary'])

      needed_keys = ['title', 'permalink', 'postDate', 'excerpt']

      entries = []
      entries.append(['title', 'url', 'date', 'summary'])

      for item in responses:
            entry = [item['config'][key] for key in needed_keys]
            entries.append(entry)      

      new_df = pd.DataFrame(entries[1:],columns=entries[0])     
      
      new_df['date'] = new_df['url'].apply(lambda x: date_from_url(x))

      # Getting list of texts with keywords therein
      relevant_text = []
      relevant_text.append(['title', 'url', 'date', 'summary', 'text'])
      
      for index, row in new_df.iterrows():
            if row.date >= today - timedelta(days=7):
                  print('Fetching: ' + row.url)
                  response = requests.post(row.url)#, headers=header)

                  html = soup(response.text, 'lxml')

                  objects = html.find_all('div', id="content--body")
                  article_text = []
                  for obj in objects:
                        paragraph_text = obj.find_all('p')
                        for p in paragraph_text:
                              article_text.append(p.text)
                        #print(obj.text)
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

      new_df = pd.DataFrame(relevant_text[1:],columns=relevant_text[0])
      
      #########
      save_path = DATA_PATH + 'mit_data.csv'
      
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
      print(dir_path)
      DATA_PATH = './data/'
      IN_DATA_PATH = './data/input_data/'
      
      today = datetime.now()

      load_file = IN_DATA_PATH + 'collection_urls_dict.json'

      with open(load_file) as handle:
            sources = json.loads(handle.read())
      
      API_Link = sources['MIT_Technology_Review_API']

      load_file = IN_DATA_PATH + 'collection_searchterms.json'

      with open(load_file) as handle:
            search_terms = json.loads(handle.read())

      mit_searcher(API_Link, search_terms)