import re
import json
import os
from subprocess import call
from config import *
RUN_ID = 'test9'
N=1
basedocresults = json.load(open(TRAINED_RESULT_FP))
for topic in basedocresults:
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
			if counterb==5:
				call(["python", JIG_FP, "-runid", RUN_ID, "-topic", topic, "-docs",docscore[0], docscore[1],docscore[2],docscore[3], docscore[4]])
		counter = counter +1
			
		if counter >N:
			break
filename = RUN_ID+'.txt'
N=str(N)
call(["python", CUBE_TEST_FP, '--runfile', filename, '--topics', QUERIES_FP, '--params', PARAM_FP, '--cutoff', N])