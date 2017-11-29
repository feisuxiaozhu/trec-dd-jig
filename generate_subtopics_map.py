import re
import json
import os
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
			q_number_of_subtopics = re.search(r'num_of_subtopics="(\d+)"',raw_query).group(1)
			
			raw_subtopics = re.split(r'</subtopic>', raw_query)
			for i in range(int(q_number_of_subtopics)):
				print (i+1)

		queires.append({'_number': q_number, 'topicname': q_topicname, 'num_of_subtopics': q_number_of_subtopics})
	return queires


with open(QUERIES_FP) as f:
	queires = parse_raw_queires(f.read())

print(queires)