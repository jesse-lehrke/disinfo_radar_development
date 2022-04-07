
def aggragate(df, group_on, column):
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