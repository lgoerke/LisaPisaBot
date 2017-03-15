import gensim
import gensim.models.doc2vec as d2v
import collections
import pandas as pd
import html
import codecs

# load the movies into the gensim format
def load_movies(fname):
	docs = pd.read_csv(fname, encoding = 'utf-8')
	for i, line in enumerate(docs["plot"]):
		line = html.unescape(html.unescape(line))
		yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])

# save the Gensim formatted documents in a list
documents = list(load_movies("movie_db.csv"))
# define the model
model = d2v.Doc2Vec(documents, size=100, window=8, min_count=2, workers=4)
# make sure we have the fast version of gensim's doc2vec!
assert gensim.models.doc2vec.FAST_VERSION > -1, "this will be painfully slow otherwise"
# set the learning rate
alpha = 0.025
# set the model to use that learning rate
model.alpha, model.min_alpha = alpha, alpha
# train the model! Should take around 5 minutes
model.train(documents)
# save the trained model to disk, for loading into the bot
model.save("doc2vec_ge5_model")