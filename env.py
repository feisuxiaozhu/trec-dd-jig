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

class environment:
	def __init__(self, topic_name, topic_id, dimension, iteration, reserve):
		self.topic_id = topic_id
		self.topic_name = topic_name
		self.dimension = dimension
		self.num_of_on_topics = 0
		self.reward_quantum = 100
		self.number_of_iteration = 1
		self.number_of_max_iteration = iteration
		self.reserve_size = reserve
		self.search_history='' #store the returned docs for this session
		self.hiearchy_map = read_hiearchy()
		self.reserve = self._build_reserve() #a dictionary of returned doc, key=docid, value=search score
		self.reserve_vector = self.build_vector_reserve() #a dicionary of returned doc, key=docid, value=hiearchy vector
		self.state = self.find_initial_state() # max value key in the running sum between on topic docs and hiearchy map
		
		

	#hold first 500 returned document from given query = topic_name
	#documents are represented by a docID and a topic vector
	def _build_reserve(self):
		self.topic_name = re.sub('[/]','',self.topic_name)
		es_client = elasticsearch.client.Elasticsearch(
			'http://{}:{}'.format(ES_HOST, ES_PORT), timeout=30)

		results = {}
		query_dsl = make_query_dsl(self.topic_name)
		raw_result = es_client.search(index=INDEX_NAME, body=query_dsl, size=self.reserve_size)
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
		self.num_of_on_topics = 0
		self.number_of_iteration = 1
		self.reserve = self._build_reserve()
		self.state = self.find_initial_state()

		return self.state

	def dot_with_hiearchy(self,docid):
		results={}
		docid = docid
		doc_vector = self.reserve_vector[docid]
		for i,j in self.hiearchy_map.items():
			result = sum(k[0]*k[1] for k in zip(doc_vector,j))
			results[i] = result
		return results

	#return the state vector associated with the on topic docs in first round of interaction
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
		try:
			os.remove(JIG_LOG_FP)
		except OSError:
			pass
		subprocess.check_output(a)
		#after run the jig, update self.search_history
		self.search_history = docscore[0]+' '+docscore[1]+' '+docscore[2]+' '+docscore[3]+' '+docscore[4]+' </score>'



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
			null = np.zeros(self.dimension)
			if on_topic == False: return null
			#if there is on topic docs, find the initial state, which is the sum of on topic docs' vectors
			running_sum = np.zeros(self.dimension)
			for i in on_topic_docs:
				vector = self.reserve_vector[i]
				running_sum = vector + running_sum

			#normalize state vector later, just store the number of on topic docs
			self.num_of_on_topics = len(on_topic_docs) + self.num_of_on_topics
			self.number_of_iteration += 1
			return running_sum

	#given the action (topic from 1 to 12), return the top 5 docs that are most related to such topic to simulated user
	def step(self, action):
			#given action, the returned doc is the top 5 
			#first find the dot product between docs in reserve with topic vector
			result={} # a dicionary later to store the doc products
			topic_vector = self.hiearchy_map[action] #note the action is a string between 1 to 12
			for i,j in self.reserve.items():
				doc_vector = self.reserve_vector[i]
				result[i] = sum(k[0]*k[1] for k in zip(topic_vector,doc_vector))
			top_five = sorted(result, key=result.get, reverse=True)[:5] # a list of doc_id of top five docs in the reserve related to topic_vector
			
			#second remove these docs from both self.reserve, notice we will never delete anything from self.reserve_vector
			for i in top_five:
				self.reserve.pop(i)

			#third send top five docs to jig, find out reward
			#notice the reward is just ontopic/offtopic. Very straightforward.
			docscore={}
			counter=0
			for i in top_five:
				docscore[counter] = i+":"+str(5-counter)
				counter +=1
			#if there is not sufficient returned docs, then fill in with empty docs
			if counter <4:
				for k in range(counter,5):
					docscore[counter] = '0000000:0'
					counter+=1

			run_id = 'initialization'
			a=["python", JIG_FP, "-runid", run_id, "-topic", self.topic_id, "-docs",docscore[0], docscore[1],docscore[2],docscore[3], docscore[4]]
			os.remove(JIG_LOG_FP)
			subprocess.check_output(a)
			#after check with jig, update search history
			self.search_history= self.search_history+ docscore[0]+' '+docscore[1]+' '+docscore[2]+' '+docscore[3]+' '+docscore[4]+' </score>'

			with open(JIG_LOG_FP) as f:
				contents = f.readlines()
			on_topic_docs=[]
			reward = 0
			for i in contents:
				judge = i.split()[4]
				if judge == '1':
					on_topic_docs.append(i.split()[2])
					reward = reward + self.reward_quantum

			
			#fourth find the new state vector and update the number of total on topic docs
			for i in on_topic_docs:
				vector = self.reserve_vector[i]
				self.state = self.state + vector
			self.num_of_on_topics = len(on_topic_docs) + self.num_of_on_topics
			self.number_of_iteration += 1
			done = False #need to return done to be compatible with the DQN model we use
			if reward == 0:
				done = True #if reward is zero then done
			if self.number_of_iteration >= self.number_of_max_iteration:
				done = True
			return self.state, reward, done




# a = environment('Dwarf Planets','dd17-6',75)
# a.step('1')
# a.step('2')
# a.reset()
# print(a.state)
#print(a.num_of_on_topics)
#print(a.reserve_vector)
#(a.reserve)
#a.reset()
#print(a.hiearchy_map['1'])
# print(a.search_history)







