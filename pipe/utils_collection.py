import re
from itertools import combinations, permutations, chain
from datetime import datetime, timedelta

def aggragate(df, group_on, column):
      '''
      Never forget your docstrings!
      Drop duplicate rows based on "group_on"
      Merges data in all "column" rows
      '''
      cmnts = {}
      for i, row in df.iterrows():
            while True:
                  try:
                        if row[column]:
                              cmnts[row[group_on]].append(row[column])
                        else:
                              cmnts[row[group_on]].append('n/a')
                        
                        break

                  except KeyError:
                        cmnts[row[group_on]] = []

      df.drop_duplicates(group_on, inplace=True)

      df[column] = [', '.join(v) for v in cmnts.values()]

      return df

def datetime_parse(x):
      '''
      Parse datetime out of a string
      More functionality should be added as issues encountered 
      Has some serious issues as it stands... not a hard fix, but time consuming 
      '''
      # Remove all non-alpha-numeric
      out = re.sub(r'[^0-9a-zA-Z:]+', ' ', x)

      ## Remove any starting tag with :
      # str.split('Updated: ', expand=True)
      
      # Remove time 
      out.replace(r'\b(([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?\s?([AaPp][Mm])?)', ' ')
      
      month_dict = {
      'January':'1', 'February':'2', 'March':'3', 'April':'4', 'May':'5', 'June':'6',
      'July':'7', 'August':'8', 'September':'9', 'October':'10', 'November':'11', 
      'December':'12', 'Jan':'1', 'Feb':'2', 'Mar':'3', 'Apr':'4', 'May':'5',
      'Jun':'6', 'Jul':'7', 'Aug':'8', 'Sep':'9', 'Oct':'10', 'Nov':'11', 'Dec':'12'
      }

      # Not needed, replaces months with number value, but strtime does that
      #out = [out.replace(key, value) for key, value in month_dict.items() if key in out][0]
      
      # Removing digits longer than 4 long 
      out = re.sub(r'[0-9]\d{4,}', ' ', out)
      #out = re.sub(r'[0-9]+:[0-9]+', ' ', out) # ???

      # Removing all non-digits and words not in months
      out = out.split(' ')
      out = [word for word in out if word.isdigit() or word in list(month_dict.keys())]
      out = ' '.join(out[:3])
      
      # Strip loose whitespace
      out = out.strip()
      
      # Lists for parsing
      month = ['%b', '%m', '%B']
      day = ['%d']
      year = ['%Y', '%y']

      varieties = list(permutations(chain(year, day, month), 3))
      for v in varieties:
            v = ' '.join(v)
            try:
                  date = [datetime.strptime(str(out), v)]# if d != 0 else d for d in out] #old tag used elsewhere, here for ref.
  
                  if date is not None:
                        print('Successfully parsed with format: ' + v)
                        return date
                        break
            except:
                  #print('Failed: ' + v)
                  pass