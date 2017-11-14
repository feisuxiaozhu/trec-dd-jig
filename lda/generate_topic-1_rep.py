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

TOPIC_1_FP = "classify_subtopic/1"

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
			if d.check(word):
				words.append({"word": word, "pos": tag})

	lem=WordNetLemmatizer()
	nouns=[]
	for word in words:
		if word["pos"] in ["NN", "NNS"]:
			nouns.append(lem.lemmatize(word["word"]))
	#print (nouns)
	return nouns

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

dimension = 75
out=''
for i in os.listdir(TOPIC_1_FP):
	fp = TOPIC_1_FP+'/'+i
	with open(fp) as f:
		temp = f.read()
	i = re.sub('.txt','',i)
	result = turnvector(dimension, run(temp))
	out = out + '<sub hiearchy number>'+ i +'</sub hiearchy number>\n'+ \
			'<sub hiearchy vector>'+str(result)+'</sub hiearchy vector><spliter>\n'

f = open(TOPIC_1_FP+'/'+"sub_hiearchy_map.txt", 'w')
f.write(out)
f.close()


















