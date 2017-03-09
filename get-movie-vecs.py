import gensim
import gensim.models.doc2vec as d2v
import collections
import pandas as pd
import html
import codecs

def load_movies(fname):
	docs = pd.read_csv(fname)
	for i, line in enumerate(docs["answer"]):
		if i != 41:
			line = html.unescape(html.unescape(line))
			yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])

# def read_text(fname, tokens_only=False):
#     with codecs.open(fname, "r", "utf-8-sig") as f:
#         for i, line in enumerate(f):
#             yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])

documents = list(load_movies("movie_db.csv"))
# documents = list(load_movies("movie-text.txt"))

# documents = d2v.TaggedLineDocument('movie_text.txt')
model = d2v.Doc2Vec(documents, size=100, window=8, min_count=2, workers=4)

assert gensim.models.doc2vec.FAST_VERSION > -1, "this will be painfully slow otherwise"

alpha, min_alpha = (0.025, 0.001)
# alpha_delta = (alpha - min_alpha) / passes

model.alpha, model.min_alpha = alpha, alpha

new_movie = ["A","group","of","POWs", "try", "to", "escape", "their", "prison"]
reps = 10
for i in range(reps):
	model.train(documents)

	new_vec = model.infer_vector(new_movie)
	most_sim = model.docvecs.most_similar([new_vec],topn = 5)
	# print(most_sim)

	print(documents[most_sim[0][0]])

# for i in range(len(most_sim)):
	# print(documents[most_sim[i][0]])

ranks = []
second_ranks = []
for doc_id in range(len(documents)):
    inferred_vector = model.infer_vector(documents[doc_id].words)
    sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
    rank = [docid for docid, sim in sims].index(doc_id)
    ranks.append(rank)
    
    second_ranks.append(sims[1])

print(documents[116])

print(collections.Counter(ranks))