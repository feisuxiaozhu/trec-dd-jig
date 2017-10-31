from env import environment
from dqn import DQNAgent
from config import *
import numpy as np
import os
from config import *

with open(TOPIC_FP) as f:
	topics = f.readlines()

#first create an agent for training
state_size = 75
action_size = 12
agent = DQNAgent(state_size, action_size)
done = False
batch_size = 32

#create an environment for training on different topics
EPISODES = 10
for i in topics:
	#for each new topic reset the exploration rate
	agent.epsilon = 1.0
	topic_number = i.split()[0]
	topic_id = 'dd17-'+str(topic_number)
	topic_name_tokens = i.split()[1:]
	topic_name =''
	for j in topic_name_tokens:
		topic_name = topic_name + j +' '

	env = environment(topic_name,topic_id, state_size)

	#train agent over this specific environment (topic)
	for e in range(EPISODES):
		state = env.reset()
		state = np.reshape(state, [1,state_size])
		for time in range(500):
			action = agent.act(state)+1
			action = str(action)
			next_state, reward, done = env.step(action)
			next_state = np.reshape(next_state, [1,state_size])
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


#Not run the trained agent and see how it works:
N = 10
results={}
for i in topics:
	topic_number = i.split()[0]
	topic_id = 'dd17-'+str(topic_number)
	topic_name_tokens = i.split()[1:]
	topic_name =''
	for j in topic_name_tokens:
		topic_name = topic_name + j +' '
	env = environment(topic_name,topic_id,state_size)

	#start 10 interactions between search engine and user

