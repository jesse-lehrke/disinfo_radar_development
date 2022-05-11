# Imports
import requests
from bs4 import BeautifulSoup as soup
import lxml

import pandas as pd

from os import listdir, path
from datetime import datetime, timedelta
import json
import re
import time

# prep for import of own scripts
# #this only needs to be done because module not in same place as this py
import sys
sys.path.insert(0, '.')

# Importing functions from our own modules
from utils.collection_utils import datetime_parse


def date_from_url(x):
      # Define regex pattern to get date from url
      pat = r"(20[0-2][0-9]([-_/]?)[0-9]{2}(?:\2[0-9]{2})?)"
      dates = re.compile(pat)

      res = dates.search(x)
      res = datetime_parse(res[0])

      return res[0]
      
def get_response(API_Link, pages=1):
      # Get re
    with requests.get(API_Link + '&page=' + str(pages)) as response:
        page_soup = soup(response.content, 'lxml')
        return page_soup

def mit_searcher(API_Link, search_terms, days_back=7):
      # MIT defined topic tags to search
      topic_tags = ['artificial-intelligence', 'humans-and-technology', 'computing'] 

      ## The topic search approach is not used at present, we use the API instead
      # base_url = sources['MIT_Technology_Review']
      # topic_designator = 'topic/'
      # final_url = base_url + topic_designator + topic_tags[0]
      
      # List to save response for each topic tag
      responses = []

      # Getting responses
      for tag in topic_tags:
            response = get_response(API_Link + tag, pages=str(1))

            j_response = json.loads(response.text)
            # Just adding response in list, not appending list
            responses = responses + j_response
      
      # This df not needed anymore, but waiting to delete
      # collected_df = pd.DataFrame(columns=['title', 'url', 'date', 'summary'])

      # Keys we need to extract from json
      needed_keys = ['title', 'permalink', 'postDate', 'excerpt']

      # Preping a list to save data to
      entries = []
      entries.append(['title', 'url', 'date', 'summary'])

      # Getting data we need
      for item in responses:
            entry = [item['config'][key] for key in needed_keys]
            entries.append(entry)      

      # Putting data in dataframe
      new_df = pd.DataFrame(entries[1:],columns=entries[0])     
      
      new_df['date'] = new_df['url'].apply(lambda x: date_from_url(x))

      # Getting list of texts with keywords therein
      relevant_text = []
      relevant_text.append(['title', 'url', 'date', 'summary', 'text'])
      
      # Gettin text and saving if our search terms appear in it
      for index, row in new_df.iterrows():
            if row.date >= today - timedelta(days_back):
                  print('Fetching: ' + row.url)
                  response = requests.post(row.url)
                  html = soup(response.text, 'lxml')

                  objects = html.find_all('div', id="content--body")
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

      new_df = pd.DataFrame(relevant_text[1:],columns=relevant_text[0])
      
      # Saving data
      save_path = DATA_PATH + 'mit_data.csv'
      
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
      
      API_Link = sources['MIT_Technology_Review_API']

      # Getting search terms from json
      load_file = IN_DATA_PATH + 'collection_searchterms.json'
      with open(load_file) as handle:
            search_terms = json.loads(handle.read())

      # Run
      mit_searcher(API_Link, search_terms, days_back=7)