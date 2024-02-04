from depth_search import find_all_legal_movements, get_subset_states_with_score_and_previous_movements, recursion
from tube_setup import Tube


#Initializing the system
def initialize_tubes():
    tube1 = Tube(["GREY", "BLUE", "BLUE", "LIGHT_BLUE"], "Tube1")
    tube2 = Tube(["YELLOW", "MEHENDI", "BLUE", "LIGHT_GREEN"], "Tube2")
    tube3 = Tube(["GREEN", "GREEN", "GREEN", "BROWN"], "Tube3")
    tube4 = Tube(["LIGHT_GREEN", "PURPLE", "BROWN", "GREY"], "Tube4")
    tube5 = Tube(["MEHENDI", "YELLOW", "LIGHT_BLUE", "RED"], "Tube5")
    tube6 = Tube(["LIGHT_BLUE", "PINK", "PURPLE", "GREY"], "Tube6")
    tube7 = Tube(["LIGHT_BLUE", "GREEN", "ORANGE", "PINK"], "Tube7")
    tube8 = Tube(["RED", "PURPLE", "ORANGE", "LIGHT_GREEN"], "Tube8")
    tube9 = Tube(["YELLOW", "GREY", "LIGHT_GREEN", "PINK"], "Tube9")
    tube10 = Tube(["ORANGE", "MEHENDI", "BLUE", "MEHENDI"], "Tube10")
    tube11 = Tube(["RED", "YELLOW", "BROWN", "BROWN"], "Tube11")
    tube12 = Tube(["PURPLE", "RED", "ORANGE", "PINK"], "Tube12")
    tube13 = Tube([None, None, None, None], "Tube13")
    tube14 = Tube([None, None, None, None], "Tube14")
    list_of_tubes = [tube1, tube2, tube3, tube4, tube5, tube6, tube7, tube8 , tube9, tube10, tube11, tube12, tube13, tube14]
    return list_of_tubes

initial_state = initialize_tubes()

# Running with recursion
movements, final_movements  = recursion(initial_state, [])
print("Total movements needed = {}".format(len(movements)))


# master = [[initial_state,[],0]]
# Find all movements from state 0 -> new-states with old movements and score logic
# subset_states, dead_states, final_state = get_subset_states_with_score_and_previous_movements(initial_state)

# update the master list - state_details, movements_needed, state_score
# Check if any of the state is dead_end -> save to dead_end list & remove from master
# Select the top state, and repeat
# Everytime -> update the master to remove the with new-states