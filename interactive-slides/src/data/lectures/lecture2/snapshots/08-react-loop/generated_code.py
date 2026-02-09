import pandas as pd
import numpy as np

df = pd.read_csv('temp_data.csv')

print(df['IMDB Rating'].mean())