import arxiv
import json
import pandas as pd
from os import listdir, path
from os.path import isfile, join
from pandas import json_normalize
from datetime import datetime

from utils_collection import aggragate

DATA_PATH = './data/'
OUTPUT_PATH = './data/raw/'
CREDS_PATH = './collection/credentials/'

def str_to_datetime(x):
      y = datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')
      return y

def arxiv_searcher(QUERY, results, scraped_times):
      '''
      Function that turns an arxiv query into a df
      Parameters:
        QUERY = term to search for
        results = max results to return
        scraped_times = json of last scrape, TO-DO: load this in main as string time
                    so string time can be entered here for special search
      '''
      
      search = arxiv.Search(
        query = QUERY,
        max_results = results,
        sort_by = arxiv.SortCriterion.SubmittedDate,
        #sort_order = arxiv.SortOrder.descending
      )

      # Save data to
      # overwrite 'w' or append 'a'
      action = 'a'

      #save as
      save_as = 'arxiv_' + QUERY

      file = OUTPUT_PATH + save_as + '.jsonl'

      for result in search.results():
            with open (file, action) as f:
                  json.dump(result._raw, f, default=str) # use raw as __dict__ has raw in it, thus more data
                  f.write('\n')

      df = pd.read_json(file, convert_dates=True, lines=True, orient='records')
      
      # Add column with search term used to locate article
      df['search_term'] = QUERY
      
      # Reducing data to only what we need, matching format to other csv files
      df['published'] = df['published'].apply(lambda x: str_to_datetime(x))
      df = df[['title', 'links', 'published']] # 'summary' 'search_term'
      df = df.rename(columns={'links': 'url', 'published': 'date'})
      
      # Getting last collection time, if none, getting oldest date in results
      base_url = 'arxiv'
      try:
            last_collected = datetime.strptime(scraped_times[base_url],'%Y-%m-%dT%H:%M:%SZ')
      except:
            last_collected = min(list(df.published))
      print(last_collected)
      # Filter to just since last search
      new_df = df[df.published > last_collected]
      print(len(new_df))

      '''
      HERE TO
      '''

      # # consider another subfolder then change PATHs
      # get_pdfs(DATA_PATH, QUERY, df_collected)
      
      # bulk_pdf_to_text(DATA_PATH, QUERY)
      # #pdf_to_text(DATA_PATH, QUERY)
      
      # df_temp = text_to_csv(DATA_PATH, QUERY)

      # #new_df = df_collected[df_collected['date'] >= datetime.now() - timedelta(days=60)]

      # #try:
      # new_df['text'] = df_temp
      
      '''
      HERE!
      '''
      
      # Saving, as new if not exists, concating if file exists already
      save_path = DATA_PATH + 'arxiv_data.csv'
      
      if path.isfile(save_path):
            old_df = pd.read_csv(save_path)
            combined_df = pd.concat([new_df, old_df])
            combined_df.drop_duplicates(subset='links', inplace=True)
            combined_df.to_csv(save_path, index=False)
      else:
            new_df.to_csv(save_path, index=False)
     

      # Saving collection time
      scraped_times[base_url] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') 
      with open(IN_DATA_PATH + 'scraped_times.json', 'w', encoding='utf8') as f:
            json.dump(scraped_times, f)
      
      return new_df

if __name__ == '__main__':
      # Paths
      dir_path = path.dirname(path.realpath(__file__))
      DATA_PATH = dir_path + '/data/'
      IN_DATA_PATH = dir_path + '/data/input_data/'
      OUTPUT_PATH = dir_path + '/data/raw/'

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
      
      # Getting search terms from json
      load_file = IN_DATA_PATH + 'collection_searchterms.json'
      with open(load_file) as handle:
            search_terms = json.loads(handle.read())


###############
      ### keyword list we can mix into the final dataframe
      # CHANGE TO USE :
      # search_terms['search_term']:
      keywords = ["GAN"]#, "GPT-3", "fake news", "disinformation"]

      ####turn list of keywords into a list of dataframes with respective queries
      list_of_dataframes = [arxiv_searcher(x, 1000, scraped_times) for x in keywords]

      ##### concatenate the list of dataframes into a common frame
      df = pd.concat(list_of_dataframes)

      ### drop duplicate rows
      # only needed for full dataset work
      #aggragate(df, 'summary', 'search_term')
      
      ### saving the final df
      #df.to_excel(DATA_PATH + "results.xlsx",index=False)
      df.to_csv(DATA_PATH + "results.csv", index=False)


