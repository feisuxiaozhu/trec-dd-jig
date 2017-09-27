import re
import os
import json
import subprocess
import elasticsearch
from config import *

def parse_raw_queires(raw_data):
	queires = []
	raw_queries = re.split(r'</topic>', raw_data)

	for raw_query in raw_queries:

		raw = re.search(r'topic name="([\s\w\W]+)" num_of_subtopics', raw_query)
		if bool(raw)==True:
			raw=raw.group(1)
			q_number = re.search(r'id="([\s\w\W]+)',raw).group(1)
			q_topicname = re.search(r'([\w\W]+)" id',raw).group(1)
			q_topicname = re.sub('[/]','',q_topicname)			
			queires.append({'_number': q_number, 'topicname': q_topicname})
	return queires

def make_query_dsl(s):
	query = {
		'query':{
			'bool':{
				'should':[
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

def search_queries(queries, index_name, es_host, es_port):
	es_client = elasticsearch.client.Elasticsearch(
		'http://{}:{}'.format(es_host, es_port), timeout=30)
	results={}
	for query in queries:
		query_dsl = make_query_dsl(query['topicname'])
		print('search on topic id: '+ query['_number'])
		print('search on topic: '+ query['topicname'])
		raw_results = es_client.search(index=index_name, body=query_dsl, size=50)

		temp = raw_results['hits']['hits']
		b=""
		counter=1
		for a in temp:
			b=b+str(a['_id']) + ":" + str(a['_score'])+" "
			if counter % 5 ==0:
				b=b+"</score>"
			counter = counter+1
		results[query['_number']] = b

	return results


def main():
	with open(QUERIES_FP) as f:
		queries = parse_raw_queires(f.read())

	results = search_queries(queries,INDEX_NAME, ES_HOST, ES_PORT)
	json.dump(results,open("base_search_doc.txt",'w'))
	print("search results has been saved in file base_search_doc.txt")

main()















