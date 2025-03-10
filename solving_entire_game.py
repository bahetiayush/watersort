from game_solve import initialize_tubes
from depth_search import solve_game

initial_state = initialize_tubes()
solution = solve_game(initial_state, set())

if solution:
    print(f"Solution found with {len(solution)} moves:")
    for move in solution:
        print(move)
    
else:
    print("No solution found.")
