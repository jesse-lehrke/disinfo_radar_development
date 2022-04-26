import pandas as pd
import os
from  urllib.request import urlopen
import shutil

from collections import defaultdict
from pathlib import Path
from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta
import time

def get_pdfs(DATA_PATH, QUERY, df):
      QUERY = QUERY #'CNA'
      pdf_dir = DATA_PATH + QUERY + '_pdfs'

      if not os.path.exists(pdf_dir): 
            os.makedirs(pdf_dir)

      have = set(os.listdir(pdf_dir))

      # Time out for requests
      timeout_secs = 10 

      for index, row in df.iterrows():
            if row.date >= datetime.now() - timedelta(days=14):

                  basename = row.url.split('/')[-1]
                  basename = basename.split('.')[0]
                  fname = os.path.join(pdf_dir, basename + '.pdf')
                  print(fname)

                  # try:
                  if not basename in have:
                        print('fetching %s into %s' % (row.url, fname))
                        req = urlopen(row.url, None, timeout_secs)
                        with open(fname, 'wb') as fp:
                              shutil.copyfileobj(req, fp)
                  else:
                        print('%s exists, skipping' % (fname, ))

def pdf_to_text(DATA_PATH, QUERY):
      # Checking for a program and a folder
      if not shutil.which('pdftotext'): # needs Python 3.3+
            print('ERROR: you don\'t have pdftotext installed. Install it first before calling this script')
            sys.exit()

      if not os.path.exists(DATA_PATH + QUERY + '_txt'):
            os.makedirs(DATA_PATH + QUERY + '_txt')
      
      # Specifying paths
      txt_dir = DATA_PATH + QUERY + '_txt'
      pdf_dir = DATA_PATH + QUERY + '_pdfs'

      have = set(os.listdir(txt_dir))
      files = os.listdir(pdf_dir)

      for i,f in enumerate(files):

            txt_basename = f + '.txt'
      
            if txt_basename in have:
                  print('%d/%d skipping %s, already exists.' % (i, len(files), txt_basename, ))
                  continue

            pdf_path = os.path.join(pdf_dir, f)
            txt_path = os.path.join(txt_dir, txt_basename)
            
            cmd = "pdftotext %s %s" % (pdf_path, txt_path)
            os.system(cmd)

            print('%d/%d %s' % (i, len(files), cmd))

            # check output was made
            if not os.path.isfile(txt_path):
                  # there was an error with converting the pdf
                  print('there was a problem with parsing %s to text, creating an empty text file.' % (pdf_path, ))
                  os.system('touch ' + txt_path) # create empty file, but it's a record of having tried to convert

            time.sleep(0.01) #  for ctrl+c termination

def text_to_csv(DATA_PATH, QUERY):

      txt_dir = DATA_PATH + QUERY + '_txt'
      pdf_dir = DATA_PATH + QUERY + '_pdfs'

      #results = defaultdict(list)
      results = []

      for file in Path(txt_dir).iterdir():
            with open(file, "r") as file_open:
                  filename = file.name
                  #results["title"] = filename.split('.txt')[0]
                  #results["text"].append(file_open.read())
                  results.append(file_open.read())

      #df_temp = pd.DataFrame(results)

      # !!! WARNING - DELETE DIR
      shutil.rmtree(txt_dir)
      shutil.rmtree(pdf_dir)

      return results