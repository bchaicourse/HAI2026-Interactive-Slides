
import pandas as pd
import numpy as np

df = pd.read_csv('temp_data.csv')

average_rating = df['IMDB Rating'].mean()
print(average_rating)
