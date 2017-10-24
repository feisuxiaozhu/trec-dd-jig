import re
import os
import json
import subprocess
import elasticsearch
from config import *

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

class env:
	def __init__(self, topic_name, topic_id):
		self.topic_id = topic_id
		self.topic_name = topic_name
		self.reserve = self._build_reserve()


	#hold first 500 returned document from given query = topic_name
	#documents are represented by a docID and a topic vector
	def _build_reserve(self):
		es_client = elasticsearch.client.Elasticsearch(
			'http://{}:{}'.format(ES_HOST, ES_PORT), timeout=30)

		results = {}
		query_dsl = make_query_dsl(self.topic_name)
		print (query_dsl)
		raw_result = es_client.search(index=INDEX_NAME, body=query_dsl, size=50)
		temp = raw_result['hits']['hits']
		b=''
		for a in temp:
			b = b + str(a['_id']) + ":" + str(a['_score'])+" "
		results[self.topic_id] = b 

		return results

a = env('Munch Scream Recovered','dd-1')
print(a.reserve)