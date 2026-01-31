
import pandas as pd
import numpy as np

df = pd.read_csv('sample.csv')

average_score = df['Score'].mean()
print(average_score)
