import random as random
import numpy as np
import copy
import board as b
from copy import deepcopy

"""
Monte Carlo Algorithim implementation for Watch your back game
Implemented by Harrison Liu 2018 for COMP30024 AI This code in its current form will not work

Base Functionality As follows:

0. Intercept Input 
1. Selection
2. Simulation
3. Expansion
4. Back Propergation 

The pipeline of the functions as follows:

Read input->Selection
Selection (calls) Expansion then returns to selection
Selection (calls) Simulation right after
Simulation calls Back Propergation and returns to Selection
Selection does Selection/Repeat



BLACK IS FIRST NODE, WHITE IS SECOND BTW
"""


def Monte_Carlo_Input(agent):
    """
    Function which initializes the selection process

    :param data: A dictionary payload containing the data and Monte-Carlo Specific Data
    :param rootloc: The location of the starting location
    :return:
    """

    data = {
        0: {"data": {agent.board}, "child": [], "move": None, "leaf": True, "value": 0, "white": agent.team, "win": 0,
            "play": 0,
            "parent": None}}

    data = Generate_node(data, 0, False)
    data = Monte_Carlo_Simulation_Back_Propergate(data, 0)

    return Monte_Carlo_Selection(data, 0, 0, [0])  # Begin monte_carlo


def Monte_Carlo_Selection(data, move, e_depth, path):
    e_depth += 1  # Max Depth of the search tree

    """
    TODO: Need to find a way to properly reccoemdn a move after a set amount of iterations
    -
    :param data: 
    :param move: 
    :return: 
    """

    goal = 49  # This is the placeholder checkvictory, we're hoping that monte carlo would reach this goal

    if len(data[move]["child"]) == 0:
        data = Monte_Carlo_Expansion(data, move, data[move]["white"])  # Exapnd the node if we're at the leaf
        data = Monte_Carlo_Simulation_Back_Propergate(data,
                                                      move)  # Simulate using DFS or something until we get a win.

    if (data[move]["value"] == goal):
        """
        This is where you would put check v  File "/home/harrison/PycharmProjects/untitled2/venv/Monte_Carlo_Algorithim.py", line 83, in Monte_Carlo_Selection
ictory condition and break simulation
        """
        print(data[move]["white"])
        print("Simulation complete")
        return True

    next_move = move  # assign the next potential move
    max_i = move

    for i in data[move]["child"]:
        print("value:")
        print(data[i]["value"])

        if len(data[i]["child"]) == 0:
            # data = Monte_Carlo_Expansion(data, i, data[i]["white"])
            data = Monte_Carlo_Simulation_Back_Propergate(data,
                                                          i)  # Simulate using DFS or something until we get a win.

        if abs(goal - data[move]["value"]) >= abs(
                goal - data[i]["value"]):  # This line is where you compare the heurstic
            print("Win1")

            if (abs((data[move]["win"] / data[move]["play"])) <= abs(
                    (data[i]["win"] / data[i]["play"]))):  # This line checks for wins/loss
                print("Win2")

                if abs(goal - data[i]["value"]) <= abs(
                        goal - data[max_i]["value"]):
                    max_i = i
    next_move = max_i

    if (e_depth == 50):
        # print the group it belongs to
        # reccoemend move here

        return path[1]

    path.append(next_move)
    print()
    print(goal - data[next_move]["value"])
    return Monte_Carlo_Selection(data, next_move, e_depth, path)


def Monte_Carlo_Expansion(data, move, colour):
    return Generate_node(data, move, colour)


def Monte_Carlo_Simulation_Back_Propergate(data, move):
    Games = 5  # You can change the number of games simulated here
    #
    # print("back propergation/Simulation")
    for i in range(Games):
        data = Propergate(data, move, Simulate(data, move))

    return data


def Propergate(data, move, white):
    """
    Propergate moves back to the parent node, adding 1 to the moves played
    And victory if the victory is from the same piece
    :param data:
    :param move:
    :param white:
    :return:
    """
    # print("incrementing1")
    # print(move)
    # print(data[move])

    while (data[move]["parent"] != None):
        data = increment(data, white, move)
        move = data[move]["parent"]  # Move up a level
    data = increment(data, white, move)
    return data


def increment(data, colour, move):
    #  print("incrementing2")
    #  print(data[move])
    if (data[move]["white"] == colour):

        data[move]["win"] += 1
        data[move]["play"] += 1

    else:
        data[move]["play"] += 1
    return data


def Simulate(data, loc):
    """
    You can either put your greedy agent or some other simple agent here for the simulation part.
    It is up to you on how to you want to implement this, Ideally we want to play the game till the end, but if that
    is impossible just do heurstics again
    True for a white win, false for a black win
    :param data:
    :param move:
    :return:
    """

    if (int(np.random.randint(2, size=1)) == 1):
        return True
    else:
        return False


def Generate_node(data, rootloc, colour):
    # print(rootloc)

    agent = data[rootloc]["data"]

    num_children = agent.board.get_all_actions(
        agent.team)  # You can change this to the get all actions move if you like

    data[rootloc]["leaf"] = False  # This node is no longer a leaf node

    # Flip the team around, cuz we are now predicting for the opposing team there should be a more pythonic way of doing this

    if (colour):
        colour = False
    else:
        colour = True



    for i in range(len(num_children)):
        loc = int(np.random.randint(1000, size=1))  # The unique identification of each node, in this case is an randint
        board = deepcopy(agent.board)
        board.do_action(num_children[i], not agent.team)

        """ 
        Practically you want to make it a unique Identification based upon a unique hash value.
        You can also just check all the pieces to make sure that they are not the same Up to you
        """
        if loc in data:  # Check for duplicates here if generated node is duplicate skip it
            continue
        else:
            # Value is the heurstic of the next potential state
            data[loc] = {"data": {board}, "child": [], "move": num_children[i], "leaf": True,
                         "value": board.value_board(not agent.team), "white": colour, "win": 0, "play": 0,
                         "parent": rootloc}  # Otherwise you create a new node

            data[rootloc]["child"] = data[rootloc]["child"] + [loc]

    return data


def get_data():
    """
    Put your board state here :D
    :return:
    """

    return 0


def generate_value(loc, data):
    """

      Dummy Function, put Heurstic here
      :param loc: Key to the node
      :param data: The data
      :return:

      """
    return np.random.randint(100, size=1)


def branching_factor(data, loc):
    """
    Implementation of the reccomended branching for Monte Carlo Functions

    :param data:
    :param loc:
    :return:
    """

    return 20
