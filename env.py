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



class env:
	def __init__(self, topic_name, topic_id):
		self.topic_id = topic_id
		self.topic_name = topic_name
		self.reserve = self._build_reserve()
		self.hiearchy_map = read_hiearchy()

	#hold first 500 returned document from given query = topic_name
	#documents are represented by a docID and a topic vector
	def _build_reserve(self):
		es_client = elasticsearch.client.Elasticsearch(
			'http://{}:{}'.format(ES_HOST, ES_PORT), timeout=30)

		results = {}
		query_dsl = make_query_dsl(self.topic_name)
		raw_result = es_client.search(index=INDEX_NAME, body=query_dsl, size=50)
		temp = raw_result['hits']['hits']
		b=''
		for a in temp:
			b = b + str(a['_id']) + ":" + str(a['_score'])+" "
		results[self.topic_id] = b 

		return results

	#connect to MongoDB and add topic vector to each doc in reserve list
	#def vector_addto_reserve(self):





a = env('fuck off','dd1')
print (a.reserve)






