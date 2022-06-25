import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

def make_graph(port_folio_df):
  category_df = pd.read_csv('./categories.csv', index_col=1)

  pf_array = port_folio_df.to_numpy()
  dict = {}
  sum = 0

  for arr in pf_array:
    sum += arr[3]
    code = int(arr[0])
    category = category_df.loc[code, 'category']
    if category in dict:
      dict[category] += arr[3]
    else:
      dict[category] = arr[3]

  keys = np.array(list(dict.keys()))
  values = np.array(list(dict.values()))
  plt.figure(dpi=200)
  plt.title("総額%d円"%sum, fontsize=18)
  plt.pie(values, labels=keys, autopct="%1.1f%%", textprops={'size': 'small'},)
  plt.show()
