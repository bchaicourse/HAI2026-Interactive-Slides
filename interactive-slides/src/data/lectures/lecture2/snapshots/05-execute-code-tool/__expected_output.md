```
Step 1: QueryMovieDB
Code: df.nlargest(5, 'IMDB Rating')[['Title', 'IMDB Rating']]
Result: No output. Did you forget to use print()?
Step 2: QueryMovieDB
Code: print(df.nlargest(5, 'IMDB Rating')[['Title', 'IMDB Rating']])
Result:                Title  IMDB Rating
706        Inception          9.1
639  The Dark Knight          8.9
183       Fight Club          8.8
151       The Matrix          8.7
708         The Town          8.7

Final answer:
The top 5 highest-rated movies by IMDB Rating are:

1. Inception - 9.1
2. The Dark Knight - 8.9
3. Fight Club - 8.8
4. The Matrix - 8.7
5. The Town - 8.7
```
