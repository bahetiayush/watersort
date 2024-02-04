import copy
from tube_setup import Tube

def copy_tubes(from_tube, to_tube):
    copy_of_from_tube = copy.deepcopy(from_tube)
    copy_of_to_tube = copy.deepcopy(to_tube)
    return copy_of_from_tube, copy_of_to_tube

def all_colors(list_of_tubes: list):
    combined = []
    for tube in list_of_tubes:
        combined = combined + tube.colors
        combined = list(set(combined))
    combined = list(filter(None, combined))
    return combined

def is_game_completed(list_of_tubes: list):
    is_completed = True
    for tube in list_of_tubes:
        if tube.empty_tube() or tube.completed_tube():
            continue
        else:
            is_completed = False
            break
    return is_completed

def net_possible_movements(list_of_tubes: list):
    net_movements = 0
    
    for from_tube in list_of_tubes:
        for to_tube in list_of_tubes:
            if is_movement_possible(from_tube, to_tube):
                net_movements = net_movements + 1
    
    return net_movements

def is_movement_possible(from_tube: Tube, to_tube: Tube):
    from_tube_top_color, from_tube_top_color_slots, from_tube_filled_slots = from_tube.tube_details()
    to_tube_top_color, to_tube_top_color_slots, to_tube_filled_slots = to_tube.tube_details()
    to_tube_empty_slots = to_tube.empty_slots()

    if from_tube == to_tube:
        return False
        # raise ValueError("Can't move between same tubes")
    elif from_tube_top_color == None:
        return False
        # raise ValueError("Can't move from empty tube")
    elif from_tube_filled_slots == from_tube_top_color_slots and to_tube_filled_slots == 0:
        # raise ValueError("No point of movement, skip")
        return False
    elif from_tube_top_color_slots > to_tube_empty_slots:
        # raise ValueError("Not enough space to move items")
        return False
    elif to_tube_top_color not in [from_tube_top_color, None]:
        # raise ValueError("Transfer must be for same color")
        return False
    else:
        return True
    
def movement(from_tube: Tube, to_tube: Tube):
    from_tube_top_color, from_tube_top_color_slots, from_tube_filled_slots = from_tube.tube_details()
    to_tube_top_color, to_tube_top_color_slots, to_tube_filled_slots = to_tube.tube_details()

    if is_movement_possible(from_tube, to_tube):
        for slot in range(to_tube_filled_slots,to_tube_filled_slots+from_tube_top_color_slots):
            to_tube.colors[slot] = from_tube_top_color

        for slot in range(from_tube_filled_slots-from_tube_top_color_slots, from_tube_filled_slots):
            from_tube.colors[slot] = None


def movement_print(movement: list):
    from_tube, to_tube = movement
    print("Moving from {} to {}".format(from_tube, to_tube))


def get_color_scores(list_of_tubes: list):
    all_color_list = all_colors(list_of_tubes)
    all_color_values = [[], []]

    for color in all_color_list:
        value = 0
        for tube in list_of_tubes:
            for index, tube_color in enumerate(reversed(tube.colors)):
                if color == tube_color:
                    index_value = find_index_score(index)
                    value = value + index_value
        all_color_values[0].append(color)
        all_color_values[1].append(value)

    return all_color_values


# These are old functions, not being used anymore

def find_index_score(index_value):
    scoring = [(0,10), (1,7), (2,4), (3,1)]

    for tuple in scoring:
        if tuple[0] == index_value:
            return tuple[1]
    return None

def get_tubes_with_top_color(list_of_tubes: list , top_color: str):
    tube_list = []
    for tube in list_of_tubes:
        (tube_top_color, tube_top_color_count, tube_filled_slots) = tube.tube_details()
        if tube_top_color == top_color:
            tube_list.append([tube, tube_top_color_count])
    return tube_list

def get_tube_with_slots_and_top_color(list_of_tubes: list, slots_needed: int, color: str):
    matching_tubes = []

    for tube in list_of_tubes:
        tube_top_color, tube_top_color_count, tube_filled_slots = tube.tube_details()
        empty_slots = 4 - tube_filled_slots

        if empty_slots >= slots_needed and tube_top_color in (color, None):
            matching_tubes.append(tube)

    return matching_tubes

def is_dead_end(list_of_tubes: list):
    is_dead_end = True

    if is_game_completed(list_of_tubes):
        is_dead_end = False
    else:
        for from_tube in list_of_tubes:
            for to_tube in list_of_tubes:
                if is_movement_possible(from_tube, to_tube):
                    is_dead_end = False
                    return is_dead_end
                else:
                    continue
    return is_dead_end
