import os
from gensim.models import LdaModel
from gensim import corpora
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import enchant
import numpy as np 
import re

dictionary_path = "models/dictionary.dict"
lda_model_path = "models/lda_model_50_topics.loggingda"
dictionary = corpora.Dictionary.load(dictionary_path)
lda = LdaModel.load(lda_model_path)
d = enchant.Dict('en_US')

TOPIC_1_FP = "/classify_subtopic/1/"

def run(new_review):
	nouns = extract_lemmatized_nouns(new_review)
	new_review_bow = dictionary.doc2bow(nouns)
	new_review_lda = lda[new_review_bow]

	return new_review_lda

def turnvector(size,list):
	temp = np.zeros(size)
	for i,j in list:
		temp[i-1] = j
	return temp