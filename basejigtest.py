import re
import json
import os
from subprocess import call
from config import *
RUN_ID = "test1"
N = 5
basedocresults = json.load(open(BASE_RESULT_FP))
for topic in basedocresults:
	print (topic)
	temp = re.split(r'</score>',basedocresults[topic])
	counter = 1
	for i in temp:
		if bool(i)==True:
			i = i.split()
			docscore={}
			counterb=0
			for j in i:
				docscore[counterb]=j
				counterb=counterb+1
			call(["python", JIG_FP, "-runid", RUN_ID, "-topic", topic, "-docs",docscore[0], docscore[1],docscore[2],docscore[3], docscore[4]])
		counter = counter +1
			
		if counter >N:
			break
