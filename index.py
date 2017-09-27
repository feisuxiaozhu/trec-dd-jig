import os
import re
import json
import codecs
from time import time
import elasticsearch
from config import *

def create_index(index_name, index_settings, es_host, es_port):
	es_client = elasticsearch.client.Elasticsearch('http://{}:{}'.format(es_host, es_port))

	if es_client.indices.exists(index=index_name):
		es_client.indices.delete(index=index_name)

	es_client.indices.create(index=index_name, body=index_settings)

def main():
	with open(INDEX_SETTINGS_FP) as f:
	 	index_settings = json.load(f)

	create_index(INDEX_NAME, index_settings, ES_HOST, ES_PORT)
	es_client = elasticsearch.client.Elasticsearch('http://{}:{}'.format(ES_HOST, ES_PORT),timeout=120)

	documents = {}
	start_time=time()
	cnt_ops = 0
	opts = []
	for i in os.listdir(DATA_DIR):
		fp = DATA_DIR+'/'+i
		with open(fp) as f:
			temp = f.read()

		doc_id = re.search(r'<DOCNO>(\d+)</DOCNO>',temp).group(1)

		doc_title = re.search(r'<title>([\w\s\W]*)</title>',temp)
		if bool(doc_title) == True:
			doc_title = doc_title.group(1)
		else:
			doc_title=''		

		doc_hedline = re.search(r'<hl1>([\w\s\W]*)</hl1>',temp)
		if bool(doc_hedline) == True:
			doc_hedline = doc_hedline.group(1)
		else:
			doc_hedline=''		

		doc_abstract = re.search(r'<abstract>([\w\s\W]*)</abstract>',temp)
		if bool(doc_abstract) == True:
			doc_abstract = doc_abstract.group(1)
		else:
			doc_abstract=''	
		
		doc_lead_paragraph = re.search(r'<block class="lead_paragraph">([\w\s\W]*)</block>',temp)
		if bool(doc_lead_paragraph) == True:
			doc_lead_paragraph = doc_lead_paragraph.group(1)
			doc_lead_paragraph = doc_lead_paragraph.replace('<p>', '').replace('</p>', '')
		else:
			doc_lead_paragraph=''

		doc_full_text = re.search(r'<block class="full_text">([\w\s\W]*)</block>',temp)
		if bool(doc_full_text) == True:
			doc_full_text = doc_full_text.group(1)
			doc_full_text = doc_full_text.replace('<p>', '').replace('</p>', '')
		else:
			doc_full_text=''		
		

		bulk_max_ops_cnt=BULK_MAX_OPS_CNT
		opts.append({'create':
							{'_index': INDEX_NAME, '_type': 'paper', '_id': doc_id}})
		opts.append({'title': doc_title, 'hedline': doc_hedline, 'abstract': doc_abstract, 'leadparagraph':doc_lead_paragraph, 
								  'fulltext': doc_full_text})
		cnt_ops+=1

		if cnt_ops == bulk_max_ops_cnt:
			es_client.bulk(body=opts)
			del opts[:]
			cnt_ops = 0
			print('Indexing document id:'+i)

	es_client.bulk(body=opts)
	end_time=time()
	print(end_time - start_time)

if __name__ == '__main__':
	main()