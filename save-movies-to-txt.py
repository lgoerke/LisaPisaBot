import pandas as pd
import html
import codecs


docs = pd.read_csv("movie_db.csv")

with codecs.open("movie-text.txt", "w", "utf-8-sig") as temp:
    for index, sent in enumerate(docs["answer"]):
    	if index != 41:
    		sent = html.unescape(html.unescape(sent))
    		temp.write(sent+"\n")

