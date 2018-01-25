from env_subtopics_lemur import environment
from dqn import DQNAgent
from config import *
import numpy as np
import os
from config import *
import re
import json

with open(TOPIC_FP) as f:
	topics = f.readlines()

EPISODES = 20
RESERVE= 150
ITERATION = 15
batch_size = 32
state_size = 300
agent={}
for i in topics: # create an agent and an env for each topic
	topic_number = i.split()[0]
	topic_id = 'dd17-'+str(topic_number)
	topic_name_tokens = i.split()[1:]
	topic_name =''
	for j in topic_name_tokens:
		topic_name = topic_name + j +' '

	env = environment(topic_name,topic_id, state_size,ITERATION, RESERVE)
	agent[topic_number] = DQNAgent(state_size, int(env.number_of_actions)) #create a specific agent for each topic

	for e in range(EPISODES):
		state = env.reset()
		state = np.reshape(state, [1,state_size])
		#normalize the state vector:
		#state = state/env.num_of_on_topics
		for time in range(500):
			action = agent[topic_number].act(state)+1
			action = str(action)
			next_state, reward, done = env.step(action)
			next_state = np.reshape(next_state, [1,state_size])
			#normalize the vecotr as well
			#next_state = next_state/env.num_of_on_topics
			action = int(action)-1
			agent[topic_number].remember(state, action, reward, next_state, done)
			state = next_state
			if done:
				os.system('clear')
				print("topic under training: "+ topic_id+ " "+ topic_name)
				print("episode: {}/{}, # of interations: {}, e: {:.2}".format(e, EPISODES, time, agent[topic_number].epsilon))
				#after each episode, run the agent on test system see if score improves:
				break
			if len(agent[topic_number].memory) > batch_size:
				agent[topic_number].replay(batch_size)

N=10
results={}
for i in topics:
	reward_record = []
	topic_number = i.split()[0]
	topic_id = 'dd17-'+str(topic_number)
	topic_name_tokens = i.split()[1:]
	topic_name =''
	for j in topic_name_tokens:
		topic_name = topic_name + j +' '
		topic_name = re.sub('[/]','',topic_name)
	env = environment(topic_name,topic_id,state_size,ITERATION, RESERVE)
	os.system('clear')
	print('testing agent on topic: '+ topic_id+' '+topic_name)
	#start 10 interactions between search engine and user
	state = env.state
	state = np.reshape(state,[1,state_size])
	#state = state / env.num_of_on_topics
	for k in range(N):
		action = agent[topic_number].act(state)+1
		action = str(action)
		next_state, reward, done = env.step(action)
		reward_record.append(reward)
		if done:
			break
		if reward_record[k-1]/reward_record[k]>=2: #huge drop of number of on topic docs
			break
		next_state = np.reshape(next_state, [1,state_size])
		#next_state = next_state / env.num_of_on_topics
		action = int(action)-1
		state = next_state
	#after 10 rounds of interaction, save the search history into results for each topic
	results[topic_id] = env.search_history

#save the trained search result to .txt file:
json.dump(results, open('trained_search_doc.txt','w'))
print('search results has been saved in file trained_search_doc.txt')