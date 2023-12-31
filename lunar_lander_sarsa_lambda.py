import numpy as np
import gymnasium as gym
import random
import math
import time
import matplotlib.pyplot as plt

env = gym.make('LunarLander-v2',render_mode='rgb_array')

number_of_buckets = (10,10,10,10,10,10,2,2)

num_actions = env.action_space.n
state_size = env.observation_space.shape[0]

state_value_bounds = list(zip(env.observation_space.low,env.observation_space.high))


state_value_bounds[0] = [-1,1]
state_value_bounds[1] = [-1,1]
state_value_bounds[2] = [-1,1]
state_value_bounds[3] = [-1,1]
state_value_bounds[4] = [-1,1]
state_value_bounds[5] = [-1,1]
state_value_bounds[6] = [0,1]
state_value_bounds[7] = [0,1]

upperBounds=env.observation_space.high
lowerBounds=env.observation_space.low

alpha = 0.1
gamma = 0.95
epsilon = 0.2
lam = 0.8
num_episodes = 20000
max_steps = 10

with tf.device('/GPU:0'):

  class SARSA:
      def __init__(self, env, alpha, gamma, epsilon, numberEpisodes, numberOfBins, lowerBounds, upperBounds, lam):
          import numpy as np

          self.env = env
          self.alpha = alpha
          self.gamma = gamma
          self.epsilon = epsilon
          self.actionNumber = env.action_space.n
          self.numberEpisodes = numberEpisodes
          self.numberOfBins = numberOfBins
          self.lowerBounds = lowerBounds
          self.upperBounds = upperBounds
          self.lam = lam

          self.sumRewardsEpisode = []

          self.Qmatrix = np.random.uniform(low=0, high=1, size=(numberOfBins[0],
                                                                numberOfBins[1],
                                                                numberOfBins[2],
                                                                numberOfBins[3],
                                                                numberOfBins[4],
                                                                numberOfBins[5],
                                                                numberOfBins[6],
                                                                numberOfBins[7],
                                                                self.actionNumber))

      def returnIndexState(self, state):
          x_position = state[0]
          y_position = state[1]
          x_velocity = state[2]
          y_velocity = state[3]
          angle = state[4]
          angular_velocity = state[5]
          l_legcontact = state[6]
          r_legcontact = state[7]


          luna_x_pos_bin = np.linspace(self.lowerBounds[0],self.upperBounds[0],self.numberOfBins[0])
          luna_y_pos_bin = np.linspace(self.lowerBounds[1],self.upperBounds[1],self.numberOfBins[1])
          luna_x_vel_bin = np.linspace(self.lowerBounds[2],self.upperBounds[2],self.numberOfBins[2])
          luna_y_vel_bin = np.linspace(self.lowerBounds[3],self.upperBounds[3],self.numberOfBins[3])
          luna_angle_bin = np.linspace(self.lowerBounds[4],self.upperBounds[4],self.numberOfBins[4])
          luna_angular_bin = np.linspace(self.lowerBounds[5],self.upperBounds[5],self.numberOfBins[5])
          luna_l_leg_bin = np.linspace(self.lowerBounds[6],self.upperBounds[6],self.numberOfBins[6])
          luna_r_leg_bin = np.linspace(self.lowerBounds[7],self.upperBounds[7],self.numberOfBins[7])

          index_x_position = np.maximum(np.digitize(state[0], luna_x_pos_bin)-1,0)
          index_y_position = np.maximum(np.digitize(state[1], luna_y_pos_bin)-1,0)

          index_x_velocity = np.maximum(np.digitize(state[2], luna_x_vel_bin)-1,0)
          index_y_velocity = np.maximum(np.digitize(state[3], luna_y_vel_bin)-1,0)

          index_angle = np.maximum(np.digitize(state[4], luna_angle_bin)-1,0)
          index_angularvelocity = np.maximum(np.digitize(state[5], luna_angular_bin)-1,0)

          index_l_legcontact = np.maximum(np.digitize(state[6], luna_l_leg_bin)-1,0)
          index_r_legcontact = np.maximum(np.digitize(state[7], luna_r_leg_bin)-1,0)
          return tuple([index_x_position,index_y_position,index_x_velocity, index_y_velocity, index_angle, index_angularvelocity,
                    index_l_legcontact, index_r_legcontact])

      def selectAction(self, state, index):


          if index < 500:
              return np.random.choice(self.actionNumber)

          randomNumber = np.random.random()

          if index > 7000:
              self.epsilon = 0.999 * self.epsilon


          if randomNumber < self.epsilon:
              return np.random.choice(self.actionNumber)
          else:
              return np.random.choice(np.where(self.Qmatrix[self.returnIndexState(state)] == np.max(self.Qmatrix[self.returnIndexState(state)]))[0])

      def simulateEpisodes(self):

          for indexEpisode in range(self.numberEpisodes):

              rewardsEpisode = []

              (stateS, _) = self.env.reset()
              stateS=list(stateS)

              print("Simulating episode {}".format(indexEpisode+1))

              E = np.zeros_like(self.Qmatrix)

              terminalState = False

              step = 0

              while not terminalState and step < max_steps:

                  stateSIndex = self.returnIndexState(stateS)

                  actionA = self.selectAction(stateS, indexEpisode)


                  (stateSprime, reward, terminalState, _, _) = self.env.step(actionA)

                  rewardsEpisode.append(reward)

                  stateSprime=list(stateSprime)
                  stateSprimeIndex = self.returnIndexState(stateSprime)

                  actionAprime = self.selectAction(stateSprime, indexEpisode)

                  QPrime = self.Qmatrix[stateSprimeIndex + (actionAprime,)]

                  E = E*self.lam * self.gamma
                  E[stateSIndex + (actionA,)] = E[stateSIndex + (actionA,)] + 1


                  if terminalState:
                      error=reward-self.Qmatrix[stateSIndex+(actionA,)]
                      self.Qmatrix[stateSIndex+(actionA,)]=self.Qmatrix[stateSIndex+(actionA,)]+self.alpha*error*E[stateSIndex + (actionA,)]
                      break

                  else:
                      error=reward+self.gamma*QPrime-self.Qmatrix[stateSIndex+(actionA,)]
                      self.Qmatrix[stateSIndex+(actionA,)]=self.Qmatrix[stateSIndex+(actionA,)]+self.alpha*error*E[stateSIndex + (actionA,)]

                  step = step + 1

                  stateS = stateSprime


              print("Sum of rewards {}".format(np.sum(rewardsEpisode)))
              self.sumRewardsEpisode.append(np.sum(rewardsEpisode))

      def simulateLearnedStrategy(self):

          (currentState, _) = self.env.reset()

          timeSteps = 1000

          obtainedRewards = []

          for timeIndex in range(timeSteps):

              print(timeIndex)

              actionInStateS = np.random.choice(np.where(self.Qmatrix[self.returnIndexState(currentState)] == np.max(self.Qmatrix[self.returnIndexState(currentState)]))[0])

              currentState, reward, terminated, truncated, info = self.env.step(actionInStateS)

              obtainedRewards.append(reward)

              time.sleep(0.05)

              if (terminated):
                  time.sleep(1)
                  break

          return obtainedRewards, self.env

  sarsa = SARSA(env,alpha,gamma,epsilon,num_episodes,number_of_buckets,lowerBounds,upperBounds, lam)
  sarsa.simulateEpisodes()
  (obtainedRewardsOptimal,env) = sarsa.simulateLearnedStrategy()

plt.figure(figsize=(12, 5))
# plot the figure and adjust the plot parameters
plt.plot(sarsa.sumRewardsEpisode,color='blue',linewidth=1)
plt.xlabel('Episode')
plt.ylabel('Reward')
plt.show()

env.close()
np.sum(obtainedRewardsOptimal)
