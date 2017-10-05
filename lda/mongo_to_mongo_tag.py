import os
from time import time

from pymongo import MongoClient
import nltk
from settings import *

news_collection = MongoClient(MONGO_CONNECTION_STRING)[NYT_DATABASE][NEWS_COLLECTION]
tags_collection = MongoClient(MONGO_CONNECTION_STRING)[TAGS_DATABASE][TAGS_COLLECTION]

news_cursor = news_collection.find()
newsCount = news_cursor.count()
news_cursor.batch_size(1000)

stopwords={}
with open('stopwords.txt','rU') as f:
	for line in f:
		stopwords[line.strip()]=1

done = 0
start = time()

for new in news_cursor:
	words=[]
	sentences = nltk.sent_tokenize(new["fulltext"].lower())

	for sentence in sentences:
		tokens = nltk.word_tokenize(sentence)
		text = [word for word in tokens if word not in stopwords]
		tagged_text = nltk.pos_tag(text)

		for word, tag in tagged_text:
			words.append({"word": word, "pos": tag})


	tags_collection.insert({
		"docId": new["docId"],
		"fulltext" : new["fulltext"],
		"words": words
		})

	#print("finished working on DocId: " + new["docId"])

	done += 1
	if done % 100 == 0:
		end = time()
		os.system('clear')
		print('Done '+ str(done) + ' out of ' + str(newsCount) + ' in '+ str((end - start)))