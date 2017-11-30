import os
from gensim.models import LdaModel
from gensim import corpora
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import enchant
import numpy as np 
import re
from config import *
import math

dictionary = corpora.Dictionary.load(DICTIONARY_PATH)
lda = LdaModel.load(LDA_MODEL_PATH)
d = enchant.Dict('en_US')
dimension = DIMENSION

topics_path = SUBTOPICS_PATH

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


for i in os.listdir(topics_path): #topic loop
	subtopics_path = topics_path+'/'+i
	out=''
	counter = 0
	vectors=[]
	for j in os.listdir(subtopics_path): #subtopic loop
		
		subtopics_fp = subtopics_path+'/'+j
		with open(subtopics_fp) as f:
			temp = f.read()
		j = re.sub('.txt','',j)
		if j.isdigit() == True:
			result = turnvector(dimension, run(temp))
			vectors.append(result)
			out = out+'<sub hiearchy number>'+ j +'</sub hiearchy number>\n'+\
					'<sub hiearchy vector>'+str(result)+'</sub hiearchy vector><spliter>\n'
		counter+=1

	if counter > 1: #if more than one subtopic exists, create powerset of subtopics:
		number_two_set = math.factorial(counter)/(2.0*math.factorial(counter-2.0)) #find the number of vectors that represents two subtopics
		number_two_set = int(number_two_set)
		number_of_subtopics = counter -1

		for i in range(counter-2):
			for j in range(i+1,counter-1):
				vector = (vectors[i]+vectors[j])/2
				out = out+'<sub hiearchy number>'+ str(number_of_subtopics+1) +'</sub hiearchy number>\n'+\
				 '<sub hiearchy vector>'+str(vector)+'</sub hiearchy vector><spliter>\n'
				number_of_subtopics+=1

		sum = vectors[0] #find the vector that represents all
		for i in range(1,counter-1):
			sum = vectors[i] + sum
		sum = sum / (counter-1)
		out = out+'<sub hiearchy number>'+ str(number_of_subtopics+1) +'</sub hiearchy number>\n'+\
				 '<sub hiearchy vector>'+str(sum)+'</sub hiearchy vector><spliter>\n'

	f = open(subtopics_path+'/'+"sub_hiearchy_map.txt", 'w')
	f.write(out)
	f.close	
		
