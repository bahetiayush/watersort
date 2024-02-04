from old_files.optimizations import best_tube_choice
from game_setup import *
from tube_setup import *


#Initializing the system
def initialize_tubes():
    tube1 = Tube(["PINK", "BLUE", "GREEN", "BLUE"], "Tube1")
    tube2 = Tube(["ORANGE", "GREY", "PINK", "RED"], "Tube2")
    tube3 = Tube(["BLUE", "LIGHT_BLUE", "LIGHT_BLUE", "GREEN"], "Tube3")
    tube4 = Tube(["PINK", "ORANGE", "ORANGE", "GREEN"], "Tube4")
    tube5 = Tube(["GREY", "GREY", "GREEN", "RED"], "Tube5")
    tube6 = Tube(["BLUE", "RED", "LIGHT_BLUE", "LIGHT_BLUE"], "Tube6")
    tube7 = Tube(["RED", "PINK", "ORANGE", "GREY"], "Tube7")
    tube8 = Tube([None, None, None, None], "Tube8")
    tube9 = Tube([None, None, None, None], "Tube9")

    list_of_tubes = [tube1, tube2, tube3, tube4, tube5, tube6, tube7, tube8 , tube9]
    return list_of_tubes

solving = True
movement_list = []
avoid_movement = [1,1]

while solving:

    completed_steps = 0
    attempted_steps = 0

    print("----------------------------------STARTING---------------------------------------------")

    list_of_tubes = initialize_tubes()
    if movement_list:
        for moves in movement_list[:-1]:
            movement(moves[0],moves[1])
        avoid_movement = movement_list[-1]
        movement_list = movement_list[:-1]
        
    while attempted_steps < 500:
        try:
            from_tube, to_tube = best_tube_choice(list_of_tubes, avoid_movement)
            if not from_tube:
                break
            copy_of_from_tube, copy_of_to_tube = copy_tubes(from_tube, to_tube)

            attempted_steps = attempted_steps + 1

            movement(from_tube, to_tube)

            if is_dead_end(list_of_tubes):
                from_tube.colors = copy_of_from_tube.colors
                to_tube.colors = copy_of_to_tube.colors
                print("DISCARDING THIS MOVEMENT!")
                print("-------------------------------")
                avoid_movement = [from_tube, to_tube]
                continue

            movement_list.append([from_tube, to_tube])
            completed_steps = completed_steps+1

            if to_tube.completed_tube():
                list_of_tubes.remove(to_tube)
                print("Available tubes reduced! Now playing with: ", len(list_of_tubes))

            if len(list_of_tubes) <= 2:
                solving = False
                break

        except ValueError as VE:
            continue

print("This took a total of {} steps!".format(completed_steps))



