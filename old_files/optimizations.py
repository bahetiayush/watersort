
import random
from game_setup import get_color_scores, get_tube_with_slots_and_top_color, get_tubes_with_top_color, is_movement_possible, net_possible_movements


# Function to select the best tubes based on colour scoring
def best_tube_choice(list_of_tubes: list, avoid_movement: list):
    # Retrieve color scores for tubes
    color_scores = get_color_scores(list_of_tubes)
    potential_to_tubes = []
    ineligible_from_tube = []
    max_steps = 1000
    total_from_steps = 0
    total_to_steps = 0
    ensure_movement = False

    #Loop to make sure movement is possible
    while total_to_steps < max_steps and not ensure_movement:
        potential_to_tubes = []
        # Loop to find the best tubes within a maximum number of steps
        while total_from_steps < max_steps and not potential_to_tubes:
            eligible_from_tubes = []

            # Select tubes with a specific color until eligible tubes are found
            while not eligible_from_tubes:
                selected_color = random.choices(color_scores[0], weights=color_scores[1], k=1)[0]

                #Removing ineligible from tubes
                list_of_tubes_removing_ineligible_from = [tube for tube in list_of_tubes if tube not in ineligible_from_tube]

                from_tubes_with_color = get_tubes_with_top_color(list_of_tubes_removing_ineligible_from, selected_color)
                eligible_from_tubes.extend(from_tubes_with_color)
            
            # Randomly select a tube and retrieve necessary information
            selected_tube_with_slots = random.choice(eligible_from_tubes)
            from_tube, slots_needed = selected_tube_with_slots[0], selected_tube_with_slots[1]

            # Exclude the selected tube from the tube list for further consideration
            list_of_tubes_removing_from_tube = [tube for tube in list_of_tubes if tube != from_tube]

            # Find potential tubes satisfying criteria for transfer
            potential_to_tubes = get_tube_with_slots_and_top_color(list_of_tubes_removing_from_tube, slots_needed, selected_color)
            if not potential_to_tubes:
                total_from_steps += 1
                ineligible_from_tube.append(from_tube)
                continue

        # If potential tubes are found, choose one randomly and return the transfer
        if potential_to_tubes:
            to_tube = random.choice(potential_to_tubes)
            if is_movement_possible(from_tube, to_tube):
                if from_tube != avoid_movement[0] and to_tube != avoid_movement[1]:
                    ensure_movement = True
                else:
                    total_to_steps += 1
                    continue
            else:
                total_to_steps += 1
                continue
            return from_tube, to_tube

    # If no suitable tubes are found within the steps limit, return None
    return None, None
