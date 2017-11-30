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
			q_number = q_number[5:]
			raw_subtopics = re.split(r'</subtopic>', raw_query)
			counter = 1
			for raw_subtopic in raw_subtopics:
				if counter > int(q_number_of_subtopics): break
				extracted=''
				subtopic_number = counter
				passages = re.split(r'</passage>', raw_subtopic)
				for passage in passages:
					text = re.search(r'<text>([\s\w\W]+)</text>', passage)
					if bool(text)==True:
						text=text.group(1)
						text=text[9:-3]
						extracted = extracted + text + '\n'
				filename=SUBTOPIC_FP
				
				subtopic_number = str(counter)
				filename=filename+'/'+q_number+'/'+subtopic_number+'.txt'
				os.makedirs(os.path.dirname(filename), exist_ok=True)
				with open(filename, "w") as f:
					f.write(extracted)
				counter += 1
				

with open(QUERIES_FP) as f:
	queires = parse_raw_queires(f.read())
