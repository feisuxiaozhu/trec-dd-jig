import os
from time import time
from pymongo import MongoClient
from nltk.stem.wordnet import WordNetLemmatizer
from settings import *

tags_collection = MongoClient(MONGO_CONNECTION_STRING)[TAGS_DATABASE][TAGS_COLLECTION]
nns_collection = MongoClient(MONGO_CONNECTION_STRING)[TAGS_DATABASE][NNS_COLLECTION]

news_cursor = tags_collection.find()
newsCount = news_cursor.count()
news_cursor.batch_size(5000)

lem = WordNetLemmatizer()
done = 0

start= time()
for new in news_cursor:
	nouns = []
	words = [word for word in new["words"] if word["pos"] in ["NN","NNS"]]

	for word in words:
		temp = lem.lemmatize(word["word"])
		temp = temp.replace("'","")
		if temp != "lead":
			nouns.append(temp)

	nns_collection.insert({
		"docId": new["docId"],
		"fulltext" : new["fulltext"],
		"words": nouns
		})

	done += 1

	if done % 100 ==0:
		end = time()
		os.system('clear')
		print('Done ' + str(done) + ' out of '+ str(newsCount) + ' in '+ str((end-start)))