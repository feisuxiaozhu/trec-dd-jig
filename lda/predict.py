from pymongo import MongoClient
from gensim.models import LdaModel
from gensim import corpora
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from settings import *
from time import time
import os

dictionary_path = "models/dictionary.dict"
lda_model_path = "models/lda_model_50_topics.loggingda"

dictionary = corpora.Dictionary.load(dictionary_path)
lda = LdaModel.load(lda_model_path)


def extract_lemmatized_nouns(new_review): #will not be used here
	stopwords = {}
	with open('stopwords.txt', 'rU') as f:
		for line in f:
			stopwords[line.strip()] = 1	
	words = []


	sentences = nltk.sent_tokenize(new_review.lower())
	for sentence in sentences:
		tokens = nltk.word_tokenize(sentence)
		text = [word for word in tokens if word not in stopwords]
		tagged_text = nltk.pos_tag(text)

		for word,tag in tagged_text:
			words.append({"word": word, "pos": tag})

	lem=WordNetLemmatizer()
	nouns=[]
	for word in words:
		if word["pos"] in ["NN", "NNS"]:
			nouns.append(lem.lemmatize(word["word"]))

	return nouns

def run(new_review): #will not be used here
	nouns = extract_lemmatized_nouns(new_review)
	new_review_bow = dictionary.doc2bow(nouns)
	new_review_lda = lda[new_review_bow]

	return new_review_lda

def ezrun(nouns): #input nouns only from database
	new_review_bow = dictionary.doc2bow(nouns)
	new_review_lda = lda[new_review_bow]

	return new_review_lda

nns_collection = MongoClient(MONGO_CONNECTION_STRING)[TAGS_DATABASE][NNS_COLLECTION]
lda_collection = MongoClient(MONGO_CONNECTION_STRING)[TAGS_DATABASE][LDA_COLLECTION]

news_cursor = nns_collection.find()
newsCount = news_cursor.count()
news_cursor.batch_size(5000)

done = 0
start = time()
for new in news_cursor:
	nouns = new["words"]
	result = ezrun(nouns)

	lda_collection.insert({
		"docId": new["docId"],
		"fulltext": new["fulltext"],
		"lda": result
		})

	done+=1

	if done % 100 ==0:
		end = time()
		os.system('clear')

		print('Done ' + str(done) + ' out of '+ str(newsCount) + ' in '+ str((end-start)))













