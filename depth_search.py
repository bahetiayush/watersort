from game_setup import *
from tube_setup import *


def find_all_legal_movements(list_of_tubes):
    legal_movements = []
    for from_tube in list_of_tubes:
        for to_tube in list_of_tubes:
            if is_movement_possible(from_tube, to_tube):
                legal_movements.append([from_tube, to_tube])
    return legal_movements
    
def get_new_state(list_of_tubes, movement_tubes):
    new_list_of_tubes = copy.deepcopy(list_of_tubes)
    original_from_tube, original_to_tube = movement_tubes
    from_tube = [tube for tube in new_list_of_tubes if original_from_tube.name == tube.name][0]
    to_tube = [tube for tube in new_list_of_tubes if original_to_tube.name == tube.name][0]

    if is_movement_possible(from_tube, to_tube):
        movement(from_tube, to_tube)
    else:
        print("This should NOT happen!")
    return new_list_of_tubes

def get_score_by_movement(list_of_tubes):
    score = net_possible_movements(list_of_tubes)
    return score

def sort_states_by_score(states_with_previous_movements, state_scores):
    paired_lists = list(zip(states_with_previous_movements, state_scores))
    sorted_pairs = sorted(paired_lists, key=lambda pair: pair[1], reverse=True)
    sorted_states_with_previous_movements= [pair[0] for pair in sorted_pairs]

    return sorted_states_with_previous_movements

def get_subset_states_with_score_and_previous_movements(initial_state, movement_list = []):
    possible_movements = find_all_legal_movements(initial_state)
    subset_states = []
    dead_states = []
    final_state = []

    for movement in possible_movements:
        new_tube_state = get_new_state(initial_state, movement)
        tube_state_score = get_score_by_movement(new_tube_state)
        movement_list.append(movement)
        # combining all 3
        combined = [new_tube_state,movement_list, tube_state_score]
        
        if tube_state_score == 0:
            if is_game_completed(new_tube_state):
                final_state.append(combined)
            else:
                dead_states.append(combined)
        else:
            subset_states.append(combined)

    return subset_states, dead_states, final_state

dead_end_movement_list = []

def recursion(list_of_tubes, movement_list):
    final_moves_found = False

    states_with_previous_movements = []
    state_scores = []
    possible_movements = find_all_legal_movements(list_of_tubes)

    # Get the new states with previous movements saved

    for movement in possible_movements:
        tube_state = get_new_state(list_of_tubes, movement)
        tube_state_movements = net_possible_movements(tube_state)
        tube_state_score = get_score_by_movement(tube_state)

        if tube_state_movements == 0:
            movement_list.append(movement)
            if is_game_completed(tube_state):
                final_moves_found = True
                return movement_list, final_moves_found
            else:
                dead_end_movement_list.append(movement_list)
                movement_list = movement_list[:-1]
                continue
        else:
            states_with_previous_movements.append([tube_state, movement])
            state_scores.append(tube_state_score)
            
    sorted_states_with_previous_movements = sort_states_by_score(states_with_previous_movements, state_scores)

    for state in sorted_states_with_previous_movements:
        select_tube_state = state[0]
        movement_to_reach_state = state[1]

        movement_list.append(movement_to_reach_state)
        print("Before sending movement_list: {}".format(movement_list))
        movement_list, final_moves_found = recursion(select_tube_state, movement_list)
        if final_moves_found:
            break
        else:
            movement_list = movement_list[:-1]

    return movement_list, final_moves_found