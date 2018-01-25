from env_lemur import environment
from dqn import DQNAgent
from config import *
import numpy as np
import os
from config import *
import re
import json

with open(TOPIC_FP) as f:
	topics = f.readlines()

#first create an agent for training
state_size = 300
action_size = 12
agent = DQNAgent(state_size, action_size)
print("DQN agent built")
done = False
batch_size = 32

#create an environment for training on different topics
EPISODES = 25
RESERVE= 150
ITERATION = 10
for i in topics:
	#for each new topic reset the exploration rate
	agent.epsilon = 1.0
	topic_number = i.split()[0]
	topic_id = 'dd17-'+str(topic_number)
	topic_name_tokens = i.split()[1:]
	topic_name =''
	for j in topic_name_tokens:
		topic_name = topic_name + j +' '

	env = environment(topic_name,topic_id, state_size,ITERATION, RESERVE)
	#train agent over this specific environment (topic)
	for e in range(EPISODES):
		state = env.reset()
		state = np.reshape(state, [1,state_size])
		#normalize the state vector:
		#state = state/env.num_of_on_topics
		for time in range(500):
			action = agent.act(state)+1
			action = str(action)
			next_state, reward, done = env.step(action)
			next_state = np.reshape(next_state, [1,state_size])
			#normalize the vecotr as well
			#next_state = next_state/env.num_of_on_topics
			action = int(action)-1
			agent.remember(state, action, reward, next_state, done)
			state = next_state
			if done:
				os.system('clear')
				print("topic under training: "+ topic_id+ " "+ topic_name)
				print("episode: {}/{}, # of interations: {}, e: {:.2}".format(e, EPISODES, time, agent.epsilon))
				#after each episode, run the agent on test system see if score improves:
				break
			if len(agent.memory) > batch_size:
				agent.replay(batch_size)


#another round of training (episode outter loop, topic inner loop)
# EPISODES=40
# RESERVE= 150
# ITERATION = 15
# for e in range(EPISODES):

# 	for i in topics:
# 		agent.epsilon = 1.0
# 		topic_number = i.split()[0]
# 		topic_id = 'dd17-'+str(topic_number)
# 		topic_name_tokens = i.split()[1:]
# 		topic_name =''
# 		for j in topic_name_tokens:
# 			topic_name = topic_name + j +' '

# 		env = environment(topic_name,topic_id, state_size,ITERATION, RESERVE)
# 		state=env.state
# 		state = np.reshape(state, [1,state_size])
# 		for time in range(500):
# 			action = agent.act(state)+1
# 			action = str(action)
# 			next_state, reward, done = env.step(action)
# 			next_state = np.reshape(next_state, [1,state_size])
# 			#normalize the vecotr as well
# 			#next_state = next_state/env.num_of_on_topics
# 			action = int(action)-1
# 			agent.remember(state, action, reward, next_state, done)
# 			state = next_state
# 			if done:
# 				os.system('clear')
# 				print("topic under training: "+ topic_id+ " "+ topic_name)
# 				print("episode: {}/{}, # of interations: {}, e: {:.2}".format(e, EPISODES, time, agent.epsilon))
# 				#after each episode, run the agent on test system see if score improves:
# 				break
# 			if len(agent.memory) > batch_size:
# 				agent.replay(batch_size)




reward_2 = 0
reward_3 = 0
reward_4 = 0
reward_5 = 0
reward_6 = 0
reward_7 = 0
reward_8 = 0
reward_9 = 0
reward_10 = 0

#Now run the trained agent and see how it works:
N = 10 #total of ten rounds
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
		action = agent.act(state)+1
		action = str(action)
		next_state, reward, done = env.step(action)
		if k == 0: reward_2 += reward
		if k == 1: reward_3 += reward
		if k == 2: reward_4 += reward
		if k == 3: reward_5 += reward
		if k == 4: reward_6 += reward
		if k == 5: reward_7 += reward
		if k == 6: reward_8 += reward
		if k == 7: reward_9 += reward
		if k == 8: reward_10 += reward
		reward_record.append(reward)
		if done:
			break
		# if reward_record[k-1]/reward_record[k]>=2: #huge drop of number of on topic docs
		#  	break
		next_state = np.reshape(next_state, [1,state_size])
		#next_state = next_state / env.num_of_on_topics
		action = int(action)-1
		state = next_state
	#after 10 rounds of interaction, save the search history into results for each topic
	results[topic_id] = env.search_history

#save the trained search result to .txt file:
json.dump(results, open('trained_search_doc.txt','w'))
print('search results has been saved in file trained_search_doc.txt')


reward_2 = reward_2/60
reward_3 = reward_3/60
reward_4 = reward_4/60
reward_5 = reward_5/60
reward_6 = reward_6/60
reward_7 = reward_7/60
reward_8 = reward_8/60
reward_9 = reward_9/60
reward_10 = reward_10/60

print('average reward 2: ' +str(reward_2))
print('average reward 3: ' +str(reward_3))
print('average reward 4: ' +str(reward_4))
print('average reward 5: '+ str(reward_5))
print('average reward 6: ' +str(reward_6))
print('average reward 7: ' +str(reward_7))
print('average reward 8: ' +str(reward_8))
print('average reward 9: ' +str(reward_9))
print('average reward 10: ' +str(reward_10))



















