from tube_setup import *
from game_setup import *

#testing

#Level 2
# tube1 = Tube(["YELLOW", "YELLOW", "YELLOW", "GREEN"], "tube1")
# tube2 = Tube(["BLUE", "BLUE", "BLUE", "YELLOW"], "tube2")
# tube3 = Tube(["GREEN", "GREEN", "GREEN", "BLUE"], "tube3")
# tube4 = Tube([None, None, None, None], "tube4")
# tube5 = Tube([None, None, None, None], "tube5")
# list_of_tubes = [tube1, tube2, tube3, tube4, tube5]


#Level 10
# tube1 = Tube(["PINK", "BLUE", "GREEN", "BLUE"], "Tube1")
# tube2 = Tube(["ORANGE", "GREY", "PINK", "RED"], "Tube2")
# tube3 = Tube(["BLUE", "LIGHT_BLUE", "LIGHT_BLUE", "GREEN"], "Tube3")
# tube4 = Tube(["PINK", "ORANGE", "ORANGE", "GREEN"], "Tube4")
# tube5 = Tube(["GREY", "GREY", "GREEN", "RED"], "Tube5")
# tube6 = Tube(["BLUE", "RED", "LIGHT_BLUE", "LIGHT_BLUE"], "Tube6")
# tube7 = Tube(["RED", "PINK", "ORANGE", "GREY"], "Tube7")
# tube8 = Tube([None, None, None, None], "Tube8")
# tube9 = Tube([None, None, None, None], "Tube9")
# list_of_tubes = [tube1, tube2, tube3, tube4, tube5, tube6, tube7, tube8 , tube9]

# #Level 145
# tube1 = Tube(["BROWN", "LIGHT_GREEN", "BLUE", "GREY"], "Tube1")
# tube2 = Tube(["GREEN", "RED", "RED", "GREEN"], "Tube2")
# tube3 = Tube(["PINK", "BLUE", "MEHENDI", "LIGHT_BLUE"], "Tube3")
# tube4 = Tube(["MEHENDI", "GREY", "BROWN", "ORANGE"], "Tube4")
# tube5 = Tube(["BLUE", "ORANGE", "LIGHT_BLUE", "PURPLE"], "Tube5")
# tube6 = Tube(["YELLOW", "YELLOW", "LIGHT_GREEN", "LIGHT_BLUE"], "Tube6")
# tube7 = Tube(["MEHENDI", "BLUE", "PURPLE", "GREY"], "Tube7")
# tube8 = Tube(["PINK", "RED", "GREEN", "ORANGE"], "Tube8")
# tube9 = Tube(["LIGHT_BLUE", "YELLOW", "GREY", "BROWN"], "Tube9")
# tube10 = Tube(["PURPLE", "PINK", "BROWN", "MEHENDI"], "Tube10")
# tube11 = Tube(["RED", "LIGHT_GREEN", "GREEN", "PURPLE"], "Tube11")
# tube12 = Tube(["YELLOW", "ORANGE", "LIGHT_GREEN", "PINK"], "Tube12")
# tube13 = Tube([None, None, None, None], "Tube13")
# tube14 = Tube([None, None, None, None], "Tube14")
# list_of_tubes = [tube1, tube2, tube3, tube4, tube5, tube6, tube7, tube8 , tube9, tube10, tube11, tube12, tube13, tube14]


# Level 309
# tube1 = Tube(["GREY", "BLUE", "BLUE", "LIGHT_BLUE"], "Tube1")
# tube2 = Tube(["YELLOW", "MEHENDI", "BLUE", "LIGHT_GREEN"], "Tube2")
# tube3 = Tube(["GREEN", "GREEN", "GREEN", "BROWN"], "Tube3")
# tube4 = Tube(["LIGHT_GREEN", "PURPLE", "BROWN", "GREY"], "Tube4")
# tube5 = Tube(["MEHENDI", "YELLOW", "LIGHT_BLUE", "RED"], "Tube5")
# tube6 = Tube(["LIGHT_BLUE", "PINK", "PURPLE", "GREY"], "Tube6")
# tube7 = Tube(["LIGHT_BLUE", "GREEN", "ORANGE", "PINK"], "Tube7")
# tube8 = Tube(["RED", "PURPLE", "ORANGE", "LIGHT_GREEN"], "Tube8")
# tube9 = Tube(["YELLOW", "GREY", "LIGHT_GREEN", "PINK"], "Tube9")
# tube10 = Tube(["ORANGE", "MEHENDI", "BLUE", "MEHENDI"], "Tube10")
# tube11 = Tube(["RED", "YELLOW", "BROWN", "BROWN"], "Tube11")
# tube12 = Tube(["PURPLE", "RED", "ORANGE", "PINK"], "Tube12")
# tube13 = Tube([None, None, None, None], "Tube13")
# tube14 = Tube([None, None, None, None], "Tube14")
# list_of_tubes = [tube1, tube2, tube3, tube4, tube5, tube6, tube7, tube8 , tube9, tube10, tube11, tube12, tube13, tube14]
# return list_of_tubes

#get all movements for S0 -> [M1, M2]

#start loop for S0:

# system_state_M1 = (original_tube_state, M1)
# movements = [M1]
#No dead end

# For S1 -> M2' and M2''
#Start another loop within S1 

# system_state_M2 = (system_state_M1, M2)
# movements = [M1, M2]
#if dead end
# dead_ends.append([M1,M2])
# movements = movements-1 => [M1]
# system_state_M2'' = (system_state_M1, M2'')
#No dead end
#movements = [M1,M3]

# For M3 -> M4 and M5
# system_state_M4 = (system_state_M3, M4)
#If dead end
# dead_ends.append([M1,M3,M4])


# realised dead end => go back and add new element with [2,3]

# newer_movement = []
# newer_movement.append(first)
# newer_movement.append(third)


# Initialize the tubes
# Define movement_list to be None
# While (system is NOT in end_state)
# Pick any from_tube and check if it not in the movement_list as [from, None]
    # Now find all the to_tubes it can move to
    # If there are no to_tubes
        #Call this a dead end, add it to the movement_list as [from, None]
    # Calculate and store "Movements possible" + "Completed tubes" score for each to_tube
    # Check if this move has not already been tried
    # Go the tube with the best score
    # Add this movement into the movelist
    # Check if this is dead end or complete
        #If dead end, then save this movement list
# Do a recursion on this, keep saving every movement in the movement list
