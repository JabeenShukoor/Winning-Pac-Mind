# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/

#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
#REFERENCES : 
#1. The Class Grid and the functions for manipulating maps here are taken from the code written by Simon Parsons, based on the code in pacmanAgents.py
#2. Jay Down, MDP-PacMan-Agent (2019), GitHub Repository (https://github.com/Jay-Down/MDP-PacMan-Agent) for creating the ghost radius 


from pacman import Directions
from game import Agent
import api
import random
import game
import util
import itertools

#for creating the map, and manipulating the grid values easily 
class Grid:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)
        self.grid = subgrid
        
    def setValue(self,x,y,value):
            self.grid[y][x] = value
            
    def getValue(self,x,y):
            return self.grid[y][x]
            
    def getHeight(self):
            return self.height
            
    def getWidth(self):
            return self.width
            
        #print the grid 
    def display(self):
            for i in range(self.height):
                for j in range(self.width):
                    print self.grid[i][j],
                print
            print 
            
    def prettyDisplay(self):
            for i in range(self.height):
                for j in range(self.width):
                    #printing elements with no new line 
                    print self.grid[self.height - (i + 1)][j],
                print
            print
         
          
class MDPAgent(Agent):

    #creating a constructor
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
        
        #creating dictionaries to store reward, utility and possible values(state) for each square in the grid 
        self.reward_dict = {}
        self.utility_dict = {}
        self.walls = set()
        self.grid = set()
        self.state_dict = {}
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"
        self.reward_dict = {}
        self.utility_dict = {}
        self.walls = set()
        self.grid = set()
        self.state_dict = {}
        
        
    def registerInitialState(self, state):
        #creating a state dictionary, which will have the values of possible states for each square in the map
        self.stateMapping(state)

        #creating a map similar to the pacman layout
        self.makeMap(state) 
        self.addWallsToMap(state)
        
        #creating grid to store reward values 
        self.walls = set(api.walls(state))
        corners = api.corners(state)
        BL = (0, 0) #Bottom Left corner
        BR = corners[1]  #Bottom right corner
        TL = corners[2]  #Top Left corner
        width = range(BL[0], BR[0])
        height = range(BL[1], TL[1])
        #storing the coordinate values of the grid
        self.grid = set((x, y) for x in width for y in height)

    #To make the map
    def makeMap(self, state):
        corners = api.corners(state)
        height = self.getLayoutHeight(corners)
        width = self.getLayoutWidth(corners)
        self.map = Grid(width, height)
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1
    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '#')
            
    #Function to decide the next move of pacman       
    def getAction(self, state):
        #where is pacman ?
        pacman = api.whereAmI(state)
        
        #finding the legal actions pacman can make and removing STOP from it 
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        
        #generating the reward map for pacman based on the defined reward conditions 
        self.reward_funtion(state)

        #state dictionary contains the possible moves for each coordinate positions in the grid
        if not self.state_dict:
            self.stateMapping(state)

        #starting the value iteration process
        square_values = self.valueIteration(state)

        #finding the best policy, which is the best move for pacman based on the maximum utility of the surrounding cells
        best_policy = self.best_move(state, square_values)

        #Finding out the direction deduced from the optimal policy
        direction = self.whereTo(pacman,best_policy)
        #Making PacMan move
        return api.makeMove(direction, legal)
        
    #understainding which direction to make from  the best policy information
    def whereTo(self, pacman, neighbour):
        #difference between pacman and neighbouring cell(which is the cell having max utility)
        direction = tuple(x - y for x, y in zip(pacman, neighbour))
        if direction == (-1, 0):
            return Directions.EAST
        if direction == (1, 0):
            return Directions.WEST
        if direction == (0, -1):
            return Directions.NORTH
        if direction == (0, 1):
            return Directions.SOUTH
            
    #to get the best move using the iterated map from valueIteration method and finding 
    #the bets move with max utility
    def best_move(self, state, values):
        walls = set(api.walls(state))
        pacman = api.whereAmI(state)
        
        pacman_neighbour = self.neighbours(pacman)
        possible_moves = []
        for coordinates in pacman_neighbour:
            if coordinates not in walls:
                possible_moves.append(coordinates)        
        #getting the utitlies at these points
        utility_moves = []
        for moves in possible_moves:
            utility_moves.append(values[moves])           
        
        #maximum utility
        max_index = utility_moves.index(max(utility_moves))
        best_policy = possible_moves[max_index]
        return best_policy

    #creating a reward function that assigns rewards to each square in the map
    def reward_funtion(self, state): 
        #info about the state
        walls = self.walls
        food = set(api.food(state))
        
        #this gives us the location of the ghost as well as the state, 
        #if state is 1 then it is scared, if not then 0
        ghostStates = api.ghostStates(state)
        capsules = set(api.capsules(state))
        corners = api.corners(state)
        
        #getting the width and height
        BL = (0, 0) #bottom left corner
        BR = corners[1] #bottom right corner
        TL = corners[2] #topleft corner
        width = range(BL[0], BR[0])
        height = range(BL[1], TL[1])
        
        '''
        Reward settings :
            FOOD REWARD : 20
            CAPSULE REWARD : 40
            GHOST PENALTY : -100
            NEIGHBOURING GHOST PENALTY : -50
            EMPTY SPACE REWARD = -1
        '''
       
        #all squares except walls
        for coordinate in self.grid:
            if coordinate not in walls:
                self.reward_dict[coordinate] = -1

        #rewards fro food and capsules
        for coordinate in self.grid:
            if coordinate in food:
                self.reward_dict[coordinate] = 20
            elif coordinate in capsules:
                self.reward_dict[coordinate] = 40
                
        #creating the penalty for ghost pos and neighbouring cells of the ghost pos
        for s in ghostStates:
            if s[0] in self.reward_dict.keys():
                #checking if ghost is not scared 
                if s[1] == 0:
                    self.reward_dict[s[0]] = -100
                    
                    #checking if the grid is medium
                    if width[1] > 10 and height[1]>10:
                        ghost_neighbours = self.ghostRadius(state,s[0],3)
                    else: #for smallGrid
                        ghost_neighbours = self.ghostRadius(state,s[0],2)
                    #penalty
                    for coordinate, reward in self.reward_dict.items():
                        if coordinate in ghost_neighbours:
                            self.reward_dict[coordinate] = -50
        
        #setting the utilities to 0
        for coordinate in self.grid:
            if coordinate not in walls:
                self.utility_dict[coordinate] = 0
        
    
    #This function creates a dictionary for the possible square movements for each squares in the grid 
    def stateMapping(self, state):
        walls = set(api.walls(state))
        state_dict = dict.fromkeys(self.reward_dict.keys())

        for i in state_dict.keys():
            tmp = self.neighbours(i) #the neighbours function returns the list as E,S,W,N
            state_dict[i] = {'North': [tmp[3], tmp[0], tmp[2]], #NORTH, EAST,WEST
                             'South': [tmp[1], tmp[0], tmp[2]],
                             'East': [tmp[0], tmp[3], tmp[1]],
                             'West': [tmp[2], tmp[3], tmp[1]],
                            }
            #checking if a state is wall, if it is then choose to stay at the position
            for coordinate, value in state_dict[i].items():
                for direction in value:
                    if direction in walls:
                        value[value.index(direction)] = i

        self.state_dict = state_dict

    #value iteration function
    def valueIteration(self, state):
        #variables required for bellmann equation
        gamma = 0.7
        states = self.state_dict 
        reward_values = self.reward_dict 
        utils_dict = self.utility_dict 
        iterations = 100
        #loop indefinitely until convergence
        while iterations>0:          
            for square, utility in utils_dict.items():
                u = utility
                tmp_utils = {} #dict to store temperory utitlities
                for direction, state in states[square].items():
                    #bellamann eqaution
                    utitlity_state = reward_values[square] + gamma * (
                                0.8 * utils_dict[state[0]] + 0.1 * utils_dict[state[1]] + 0.1 * utils_dict[state[2]])
                    tmp_utils[direction] = utitlity_state
                utils_dict[square] = max(tmp_utils.values())
            iterations = iterations -1          
        return utils_dict

    #to get the neighbouring cells of an input coordinate
    def neighbours(self, coordinate):
        (x, y) = coordinate
        #[east,south, west, north]
        result = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]
        return result


    #Getting the neighbourhood of the ghost locations 
    def ghostRadius(self, state, ghost, r, next=None):
        ghosts = api.ghosts(state)
        walls = set(api.walls(state))

        if next is None:
            next = []
            ghost_n = self.neighbours(ghost)
            ghost_n = []
            for i in ghost_n:
                if i not in walls or i not in ghosts:
                    ghost_n.append(i)

        # generate neighbours from the results of the function's previous pass
        if next:
            ghost_n = [self.neighbours(i) for i in ghost]
            ghost_n = itertools.chain.from_iterable(ghost_n)
            ghost_n = [i for i in ghost_n if i not in walls]
            ghost_n = [i for i in ghost_n if i not in ghosts]

        if r == 1:
            next.append(set(ghost_n))
            final = [list(i) for i in next]
            final = set(itertools.chain.from_iterable(final))
            return final
        else:
            r = r-1
            next.append(set(ghost_n))
            return self.ghostRadius(state, set(ghost_n), r, next) #calls the function again, recursive


    
