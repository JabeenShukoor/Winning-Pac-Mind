# Winning-Pac-Mind
Implementing an AI agent capable of winning the classic Pac-Man arcade game using a Markov Decision Process solver that follows a value iteration policy

*Please note that
The implementation of the Pacman agent is a part of 6CCS3AIN coursework and has used UC Berkley's open-source Pacman project http://ai.berkeley.edu/ 
mdpAgents.py is the file that contains the MDP solver and is meant to be used with the UC Berkley's Pacman game. (I claim no credit for that part of the code)*

UC Berkley Pacman Game: http://ai.berkeley.edu/project_overview.html
The code only supports Python 2.7

# Introduction
The Pacman agent is situated in a non-deterministic world. This means that there is free will for Pacman to choose which direction to move. Using an MDP solver, we can compute the action to take which is achieved by value iteration. This allows the agent to make the right decisions and eventually win the game. To win games Pacman has to eat all the food. 

#MDP Solver 
For each move, the Markov Decision Process consists of
1. Finite set of states denoted by S
2. Finite set of actions denoted by A
3. A state transition function P(s'|s,a)
4. Reward function R
5. and a Discount factor from the range [0,1]

Following this, the value iteration process is applied to the Bellman equation and the process is iterated until the value converges and we get an optimal policy. 





