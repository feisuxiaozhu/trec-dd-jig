import os
from time import time
import json
import re

from pymongo import MongoClient
from settings import *

dataset_file_DIR = DATASET_FILE_DIR 
news_collection = MongoClient(MONGO_CONNECTION_STRING)[NYT_DATABASE][NEWS_COLLECTION]
opts=[]
cnt_opts = 0
start_time=time()
bulk_max_ops_cnt=BULK_MAX_OPS_CNT

#read through data DIR and send into database
for i in os.listdir(DATASET_FILE_DIR):
	fp = DATASET_FILE_DIR+'/'+i
	with open(fp) as f:
		temp=f.read()

	doc_id = re.search(r'<DOCNO>(\d+)</DOCNO>',temp).group(1)

	doc_full_text = re.search(r'<block class="full_text">([\w\s\W]*)</block>',temp)
	if bool(doc_full_text) == True:
		doc_full_text = doc_full_text.group(1)
		doc_full_text = doc_full_text.replace('<p>', '').replace('</p>', '')
	else:
		doc_full_text=''

	
	opts.append({
		"docId": doc_id,
		"fulltext": doc_full_text
		})
	cnt_opts+=1
	if cnt_opts == bulk_max_ops_cnt:
		news_collection.insert((i for i in opts))
		del opts[:]
		cnt_opts = 0
		os.system('clear')
		print('Inserting document id:' +i)


news_collection.insert((i for i in opts))
end_time=time()
print(end_time-start_time)

