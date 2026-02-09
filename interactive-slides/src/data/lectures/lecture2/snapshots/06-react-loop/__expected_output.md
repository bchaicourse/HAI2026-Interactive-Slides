```
Thought: I need to query the movie database to find out which movies have the top 5 highest IMDB ratings.

Action: QueryMovieDB
Code: df.nlargest(5, 'IMDB Rating')
Observation: No output. Did you forget to use print()?

Thought: I forgot to print the results. I need to run the query again with print().

Action: QueryMovieDB
Code: print(df.nlargest(5, 'IMDB Rating'))
Observation:                Title  Worldwide Gross  ...  IMDB Rating
706        Inception        753830280  ...          9.1
639  The Dark Knight       1022345358  ...          8.9
183       Fight Club        100853753  ...          8.8
151       The Matrix        460279930  ...          8.7
708         The Town         33180607  ...          8.7

Thought: I now have the data. I can provide the final answer.

Answer: 1. Inception - IMDB Rating: 9.1
2. The Dark Knight - IMDB Rating: 8.9
3. Fight Club - IMDB Rating: 8.8
4. The Matrix - IMDB Rating: 8.7
5. The Town - IMDB Rating: 8.7
```
