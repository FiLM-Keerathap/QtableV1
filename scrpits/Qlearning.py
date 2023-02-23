#! /usr/bin/env python

import numpy as np
from math import *
from std_msgs.msg import String
from itertools import product
from sensor_msgs.msg import LaserScan
import time

STATE_SPACE_IND_MAX = 27648 - 1
STATE_SPACE_IND_MIN = 1 - 1
ACTIONS_IND_MAX = 3
ACTIONS_IND_MIN = 0

ANGLE_MAX = 360 - 1
ANGLE_MIN = 1 - 1
# HORIZON_WIDTH = 75 original
HORIZON_WIDTH = [9, 16, 56, 9]

T_MIN = 0.001

# Create actions
def createActions(n_actions_enable):
    # actions = np.array([0,1,2,3,4,5,6,7])
    actions = np.arange(n_actions_enable)
    return actions
# forward, left, right,  superForward, backward, stop, CW, CCW

# Create state space for Q table
def createStateSpace():
    x1 = set((0,1))
    x2 = set((0,1))
    x3 = set((0,1,2))
    x4 = set((0,1,2,3))
    x5 = set((0,1,2,3))
    x6 = set((0,1,2))
    x7 = set((0,1))
    x8 = set((0,1))
    x9 = set((0,1,2))
    x10 = set((0,1,2,3))
    state_space = set(product(x1,x2,x3,x4,x5,x6,x7,x8,x9,x10))
    return np.array(list(state_space))

# Create Q table, dim: n_states x n_actions
def createQTable(n_states, n_actions):
    # Q_table = np.random.uniform(low = -1, high = 1, size = (n_states,n_actions) )
    Q_table = np.zeros((n_states, n_actions))
    return Q_table

# Read Q table from path
def readQTable(path):
    Q_table = np.genfromtxt(path, delimiter = ' , ')
    return Q_table

# Write Q table to path
def saveQTable(path, Q_table):
    np.savetxt(path, Q_table, delimiter = ' , ')

# Select the best action a in state
def getBestAction(Q_table, state_ind, actions):
    if STATE_SPACE_IND_MIN <= state_ind <= STATE_SPACE_IND_MAX:
        status = 'getBestAction => OK'
        a_ind = np.argmax(Q_table[state_ind,:])
        a = actions[a_ind]
    else:
        status = 'getBestAction => INVALID STATE INDEX'
        a = getRandomAction(actions)

    return ( a, status )

# Select the second best action a in state
def getSecondBestAction(Q_table, state_ind, actions):
    if STATE_SPACE_IND_MIN <= state_ind <= STATE_SPACE_IND_MAX:
        status = 'getSecondBestAction => OK'
        A = Q_table[state_ind,:]
        # print(A)
        b = sorted(set(A))[-2]
        a = actions[list(A).index(b)]

        # print(b)
        # print(a)
    else:
        status = 'getSecondBestAction => INVALID STATE INDEX'
        a = getRandomAction(actions)

    return ( a, status )

# Select random action from actions
def getRandomAction(actions):
    n_actions = len(actions)
    a_ind = np.random.randint(n_actions)
    return actions[a_ind]

# Epsilog Greedy Exploration action chose
def epsiloGreedyExploration(Q_table, state_ind, actions, epsilon, prev_action):
    if np.random.uniform() > epsilon and STATE_SPACE_IND_MIN <= state_ind <= STATE_SPACE_IND_MAX:
        status = 'epsiloGreedyExploration => OK'
        ( a, status_gba ) = getBestAction(Q_table, state_ind, actions)
        # print(a)
        if (prev_action == 1 and a == 2) or (prev_action == 2 and a == 1): 
            (a,status) = getSecondBestAction(Q_table, state_ind, actions)
            # print(a)

        if status_gba == 'getBestAction => INVALID STATE INDEX':
            status = 'epsiloGreedyExploration => INVALID STATE INDEX'
    else:
        status = 'epsiloGreedyExploration => OK'
        a = getRandomAction(actions)

    return ( a, status )

# SoftMax Selection
def softMaxSelection(Q_table, state_ind, actions, T):
    if STATE_SPACE_IND_MIN <= state_ind <= STATE_SPACE_IND_MAX:
        status = 'softMaxSelection => OK'
        n_actions = len(actions)
        P_ac = np.zeros(n_actions)

        # Boltzman distribution
        P_ac = np.exp(Q_table[state_ind,:] / T) / np.sum(np.exp(Q_table[state_ind,:] / T))

        if T < T_MIN or np.any(np.isnan(P_ac)):
            ( a, status_gba ) = getBestAction(Q_table, state_ind, actions)
            if status_gba == 'getBestAction => INVALID STATE INDEX':
                status = 'softMaxSelection => INVALID STATE INDEX'
        else:
            # rnd = np.random.uniform()
            status = 'softMaxSelection => OK'
            try:
                a = np.random.choice(n_actions, 1, p = P_ac)
            ###################################    
            except:
                status = 'softMaxSelection => Boltzman distribution error => getBestAction '
                status = status + '\r\nP = (%f , %f , %f, %f, %f, %f, %f, %f) ' % (P_ac[0],P_ac[1],P_ac[2],P_ac[3],P_ac[4],P_ac[5], P_ac[6], P_ac[7])
                status = status + '\r\nQ(%d,:) = ( %f , %f , %f, %f, %f, %f, %f, %f) ' % (state_ind, Q_table[state_ind,0], Q_table[state_ind,1], Q_table[state_ind,2], Q_table[state_ind,3], Q_table[state_ind,4], Q_table[state_ind,5], Q_table[state_ind,6], Q_table[state_ind,7])
                ( a, status_gba ) = getBestAction(Q_table, state_ind, actions)
                if status_gba == 'getBestAction => INVALID STATE INDEX':
                    status = 'softMaxSelection => INVALID STATE INDEX'
    else:
        status = 'softMaxSelection => INVALID STATE INDEX'
        a = getRandomAction(actions)

    return ( a, status )

# Reward function for Q-learning - table
def getReward(  action, 
                prev_action,
                lidar, 
                prev_lidar, 
                crash, 
                current_position, 
                goal_position, 
                max_radius, 
                radius_reduce_rate, 
                nano_start_time, 
                nano_current_time, 
                goal_radius, 
                angle_state,
                win_count):

    terminal_state = False
    # init reward
    reward = 0

    # to do in learning_node file
    # add time start for each episode
    # add position start for each episode
    # add current position for each step
    # add goal position for each episode
    # add max radius for each episode
    # add radius reduce rate for each episode
    
    # time penalty 
    dist = np.linalg.norm(np.array(current_position) - np.array(goal_position))
    #  nano time diff
    time_diff = (nano_current_time - nano_start_time)
    radius = max_radius - radius_reduce_rate * (time_diff)
    if radius/max_radius < 0.1:
        radius = max_radius * 0.1
    if dist < radius:
        reward += .1
    else:
        reward += - .69

    # Crash panelty
    if crash:
        reward += -500

    # avoid facing wall panelty/rewards
    lidar_horizon = np.concatenate((lidar[(ANGLE_MIN + sum(HORIZON_WIDTH[:2])):(ANGLE_MIN):-1],lidar[(ANGLE_MAX):(ANGLE_MAX - sum(HORIZON_WIDTH[:2])):-1]))
    prev_lidar_horizon = np.concatenate((prev_lidar[(ANGLE_MIN + sum(HORIZON_WIDTH[:2])):(ANGLE_MIN):-1],prev_lidar[(ANGLE_MAX):(ANGLE_MAX - sum(HORIZON_WIDTH[:2])):-1]))
    W = np.linspace(1, 1.1, len(lidar_horizon) // 2)
    W = np.append(W, np.linspace(1.1, 1, len(lidar_horizon) // 2))
    if np.sum( W * ( lidar_horizon - prev_lidar_horizon) ) < 0:
        reward += -5
    # else:
    #     reward += 5

    #too close to wall panelty
    alpha = 20 #penelty weight
    beta = .25 #start panelty at this distant in meters    
    gamma = 0.125 #collision distant
    length_lidar = len(lidar)
    ratio = length_lidar / 360 

    if min(lidar_horizon) < beta: #lidar_horizon is define above

        reward += -alpha* (np.exp(-(min(lidar_horizon)-gamma)) - np.exp(-(beta-gamma))) / (1 - np.exp(-(beta-gamma)))

        lidar_x1 = min(lidar[round(ratio*(ANGLE_MIN + HORIZON_WIDTH[1] + HORIZON_WIDTH[2])): round(ratio*(ANGLE_MIN + HORIZON_WIDTH[1] + HORIZON_WIDTH[2] + HORIZON_WIDTH[3])) ])
        lidar_x8 = min(lidar[round(ratio*(ANGLE_MAX - HORIZON_WIDTH[1] - HORIZON_WIDTH[2] - HORIZON_WIDTH[3])):round(ratio*(ANGLE_MAX - HORIZON_WIDTH[1] - HORIZON_WIDTH[2])) ])
        #keep center
        if lidar_x1 < gamma and lidar_x8 > gamma:
            reward += -alpha* (np.exp(-(lidar_x1-gamma)) - np.exp(-(beta-gamma))) / (1 - np.exp(-(beta-gamma)))
        if lidar_x8 < gamma and lidar_x1 > gamma:
            reward += -alpha* (np.exp(-(lidar_x8-gamma)) - np.exp(-(beta-gamma))) / (1 - np.exp(-(beta-gamma)))

    # action and prev_action is same and action is left or right
    # if (prev_action == 1 and action == 2) or (prev_action == 2 and action == 1):
    #         reward += -20

    # repeat stop penelty
    # if prev_action == 2 and action == 2:
    #         reward += -1

    #reach goal
    if dist<goal_radius:
        reward += 100
        terminal_state = True
        win_count += 1
    
    #away from goal panelty
    if angle_state == 0:
        reward += -2

    #facing goal reward
    elif angle_state == 1:
        reward += 4

    elif angle_state == 2:
        reward += 1

    elif angle_state == 3:
        reward += 1

    # calculate distance reward
    reward +=  3* (np.exp(-dist) - np.exp(-max_radius)) / (1 - np.exp(-max_radius))

    return (reward, terminal_state, win_count,)
    
    # if crash:
    #     terminal_state = True
    #     reward = -100
    # else:
    #     lidar_horizon = np.concatenate((lidar[(ANGLE_MIN + HORIZON_WIDTH):(ANGLE_MIN):-1],lidar[(ANGLE_MAX):(ANGLE_MAX - HORIZON_WIDTH):-1]))
    #     prev_lidar_horizon = np.concatenate((prev_lidar[(ANGLE_MIN + HORIZON_WIDTH):(ANGLE_MIN):-1],prev_lidar[(ANGLE_MAX):(ANGLE_MAX - HORIZON_WIDTH):-1]))
    #     terminal_state = False
    #     # Reward from action taken = fowrad -> +0.2 , turn -> -0.1
    #     if action == 0:
    #         r_action = +0.2
    #     else:
    #         r_action = -0.1
    #     # Reward from crash distance to obstacle change
    #     W = np.linspace(0.9, 1.1, len(lidar_horizon) // 2)
    #     W = np.append(W, np.linspace(1.1, 0.9, len(lidar_horizon) // 2))
    #     if np.sum( W * ( lidar_horizon - prev_lidar_horizon) ) >= 0:
    #         r_obstacle = +0.2
    #     else:
    #         r_obstacle = -0.2
    #     # Reward from turn left/right change
    #     if ( prev_action == 1 and action == 2 ) or ( prev_action == 2 and action == 1 ):
    #         r_change = -0.8
    #     else:
    #         r_change = 0.0

    #     # Cumulative reward
    #     reward = r_action + r_obstacle + r_change
    # return ( reward, terminal_state )

# Update Q-table values
def updateQTable(Q_table, state_ind, action, reward, next_state_ind, alpha, gamma):
    if STATE_SPACE_IND_MIN <= state_ind <= STATE_SPACE_IND_MAX and STATE_SPACE_IND_MIN <= next_state_ind <= STATE_SPACE_IND_MAX:
        status = 'updateQTable => OK'
        Q_table[state_ind,action] = ( 1 - alpha ) * Q_table[state_ind,action] + alpha * ( reward + gamma * max(Q_table[next_state_ind,:]) )
    else:
        status = 'updateQTable => INVALID STATE INDEX'
    return ( Q_table, status )
