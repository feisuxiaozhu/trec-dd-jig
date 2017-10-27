import re
import os
import json
import subprocess
import elasticsearch
from config import *
from pymongo import MongoClient
import sys
sys.path.append('/Users/shuchenzhu/Desktop/es_dd/trec-dd-jig/lda')
from settings import *
import numpy as np
from subprocess import call

def make_query_dsl(s):
	query = {
		'query':{
			'bool':{
				'must':[
					{
						"query_string":{
							"default_field": "_all",
							"query": s
						}
					}
				]
			}
		}

	}

	return query

def make_query_mongo(s):

	query = {"docId": s}
	return query

def turnvector(size,list):
	temp = np.zeros(size)
	for i,j in list:
		temp[i-1] = j
	return temp

#read hiearchy from .txt file prepared by ../generate_hiearchy_rep.py, return a dictionary
def read_hiearchy():
	dic = {}
	with open(HIEARCHY_MAP_FP,'r') as f:
		temps = f.read()
	temps = re.split(r'<spliter>', temps)
	for temp in temps:
		id = re.search(r'<hiearchy number>([\d]+)</hiearchy number>',temp)
		if bool(id) == True:
			id = id.group(1)
			vector = re.search(r'<hiearchy vector>([\d\s\w\W]+)</hiearchy vector>',temp).group(1)
			vector = vector.split()
			vector.pop(0) #get rid of [
			vector.pop(-1) #get rid of ]
			vector = list(map(float,vector)) #convert the list from string to float
			dic[id]=vector		
	return dic

#given docid return a list of products between doc_vector and hiearchy_vectors




class env:
	def __init__(self, topic_name, topic_id, dimension):
		self.topic_id = topic_id
		self.topic_name = topic_name
		self.dimension = dimension
		self.hiearchy_map = read_hiearchy()
		self.reserve = self._build_reserve() #a dictionary of returned doc, key=docid, value=search score
		self.reserve_vector = self.build_vector_reserve() #a dicionary of returned doc, key=docid, value=hiearchy vector
		self.state = self.find_initial_state() # max value key in the running sum between on topic docs and hiearchy map

	#hold first 500 returned document from given query = topic_name
	#documents are represented by a docID and a topic vector
	def _build_reserve(self):
		es_client = elasticsearch.client.Elasticsearch(
			'http://{}:{}'.format(ES_HOST, ES_PORT), timeout=30)

		results = {}
		query_dsl = make_query_dsl(self.topic_name)
		raw_result = es_client.search(index=INDEX_NAME, body=query_dsl, size=100)
		temp = raw_result['hits']['hits']
		b=''
		for a in temp:
			results[a['_id']] = a['_score']

		return results

	#connect to MongoDB and add topic vector to each doc in reserve list
	#def vector_addto_reserve(self):
	def build_vector_reserve(self):
		result = {}

		lda_collection = MongoClient(MONGO_CONNECTION_STRING)[TAGS_DATABASE][LDA_COLLECTION]
		for i, j in self.reserve.items():
			a = make_query_mongo(i)
			#make sure you indexex the mongoDB, otherwise so slow
			lda_cursor = lda_collection.find_one(a)
			result[i] = lda_cursor['lda']
			result[i] = turnvector(self.dimension,result[i])
		return result

	def reset(self):
		self.reserve = self._build_reserve()

	def dot_with_hiearchy(self,docid):
		results={}
		docid = docid
		doc_vector = self.reserve_vector[docid]
		for i,j in self.hiearchy_map.items():
			result = sum(k[0]*k[1] for k in zip(doc_vector,j))
			results[i] = result
		return results

	def find_initial_state(self):
		#shall run the jig using any runID, say score_only
		counter = 0
		docscore={}
		run_id = 'initialization'
		temp = self.reserve.items()
		for i,j in temp:
			docscore[counter] = i+':'+str(j)
			counter += 1
			if counter >= 5:
				break
		
		a=["python", JIG_FP, "-runid", run_id, "-topic", self.topic_id, "-docs",docscore[0], docscore[1],docscore[2],docscore[3], docscore[4]]
		os.remove(JIG_LOG_FP)
		subprocess.check_output(a)

		with open(JIG_LOG_FP) as f:
			contents = f.readlines()
			

			on_topic = False
			on_topic_docs=[]
			for i in contents:
				judge = i.split()[4]
				if judge == '1': 
					on_topic= True
					on_topic_docs.append(i.split()[2])
				#remove searched docs from reserve
				used_doc = i.split()[2]
				self.reserve.pop(used_doc)

			#if no doc is on topic, the initial state is null
			if on_topic == False: return 'NULL'
			#if there is on topic docs, find the initial state:
			
			#initialize a running sum:
			running_sum = {}
			for i in range(12):
				running_sum[str(i+1)] = 0.0
			#update the running sum over all on topic docs	
			for i in on_topic_docs:
				dot_products = self.dot_with_hiearchy(i)
				for j,k in dot_products.items():					
					running_sum[j] = k + running_sum[j]
			
			#the initial state is determined by which topic has largest running sum value of dot products
			return running_sum

	#given the action (topic from 1 to 12), return the top 5 docs that are most related to such topic
	def step(self,action)：
			



a = env('Eggs actually are good for you','dd17-16',75)
print(a.state)
# print(a.reserve_vector)
#print(a.reserve)
#a.reset()
#print(a.hiearchy_map)







