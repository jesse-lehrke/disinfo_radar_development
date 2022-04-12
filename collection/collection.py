import arxiv
import json
import pandas as pd
from os import listdir, path
from os.path import isfile, join
from pandas import json_normalize

import sys
sys.path.insert(0, '.')

from utils.collection_utils import aggragate

DATA_PATH = './data/'
OUTPUT_PATH = './data/raw/'
CREDS_PATH = './collection/credentials/'

def arxiv_searcher(QUERY, results):
    '''
    function that turns an arxiv query into a df

    '''
    search = arxiv.Search(
      query = QUERY,
      max_results = results,
      sort_by = arxiv.SortCriterion.SubmittedDate
    )
    dir_path = path.dirname(path.realpath(__file__))

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

    return df


if __name__ == '__main__':
    
    # for the future
    dir_path = path.dirname(path.realpath(__file__))

    ### keyword list we can mix into the final dataframe
    keywords = ["GAN", "GPT-3", "fake news", "disinformation"]

    ####turn list of keywords into a list of dataframes with respective queries
    list_of_dataframes = [arxiv_searcher(x, 1000) for x in keywords]

    ##### concatenate the list of dataframes into a common frame
    df = pd.concat(list_of_dataframes)

    ### drop duplicate rows
    aggragate(df, 'summary', 'search_term')
    
    ### saving the final df
    #df.to_excel(DATA_PATH + "results.xlsx",index=False)
    df.to_csv(DATA_PATH + "results.csv", index=False)


