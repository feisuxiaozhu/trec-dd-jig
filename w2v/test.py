import krovetzstemmer
import gensim
import numpy as np
import json
import nltk

stemmer = krovetzstemmer.Stemmer()
global word2stem
word2stem = json.load(open("word2stem.json"))

def stem(word):
	
	if word not in word2stem:
		stemmed = stemmer.stem(word)
		word2stem[word] = stemmed
	return word2stem[word]

word2vec = gensim.models.Word2Vec.load("word2vec.100")

def get_word2vec(word, return_none_allowed=False):
	if word in word2vec.wv.vocab:
		return np.array(word2vec.wv.word_vec(word))

	else:
		if return_none_allowed:
			return None
		else:
			return np.zeros((100,))

stopwords={}
with open('stopwords.txt','rU') as f:
	for line in f:
		stopwords[line.strip()]=1

#input a paragraph and output a single w2v vector
def turn_to_w2v(a):
	words = []
	sentences = nltk.sent_tokenize(a.lower())
	vector = np.zeros(100)
	for sentence in sentences:
		tokens = nltk.word_tokenize(sentence)
		text = [word for word in tokens if word not in stopwords]

		for word in text:
			words.append(word)

	for i in words:
		temp = get_word2vec(stem(i),return_none_allowed=False)
		vector += temp
		
	return vector





b='apple tree hotel' 
a=turn_to_w2v(b)
print(a)
