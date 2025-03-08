import copy
from typing import List, Dict, Any
from game_setup import (
    GameState,
    find_all_legal_movements,
    get_new_state,
    is_game_completed
)
from tube_setup import Tube, tube_to_dict


def calculate_color_scores(tubes:List[Tube]) -> Dict[str, float]:
    """Calculates the color score for all tubes."""
    color_scores: Dict[str, float] = {}
    for tube in tubes:
      for i, color in enumerate(reversed(tube.colors)):
          if color is not None:
              if color not in color_scores:
                  color_scores[color] = 0
              if i == 0: #top
                  color_scores[color] += 4
              elif i == 1: #second
                  color_scores[color] += 2
              elif i == 2: #third
                  color_scores[color] += 1
              else: #bottom
                  color_scores[color] -= 1
          if i < 3:
            if len(tube.colors) > (i+1):
              if tube.colors[-(i+1)] is not None and tube.colors[-(i+2)] is not None and tube.colors[-(i+1)] != tube.colors[-(i+2)]:
                  color_scores[tube.colors[-(i+1)]] = color_scores.get(tube.colors[-(i+1)],0) -0.5
                  color_scores[tube.colors[-(i+2)]] = color_scores.get(tube.colors[-(i+2)],0) -0.5
    return color_scores

def calculate_tube_score(tube: Tube, color_scores: Dict[str,float]) -> float:
    """Calculates the overall score for a given tube."""
    tube_score = 0
    for color in tube.colors:
      if color in color_scores:
        tube_score += color_scores[color]
    return tube_score

def get_top_states_with_scores(game_state: GameState, dead_ends: List) -> List[Dict[str, Any]]:
    """Retrieves top 5 states, including scores (unless game is over)."""
    top_states = []
    possible_moves = find_all_legal_movements(game_state, dead_ends)
    valid_states_with_scores = []

    color_scores = calculate_color_scores(game_state.tubes)
    initial_tube_scores = {tube.name: calculate_tube_score(tube, color_scores) for tube in game_state.tubes}

    game_over = False

    for move in possible_moves:
        new_state = get_new_state(game_state, move)
        state_tuple = tuple(tuple(tube.colors) for tube in new_state.tubes)
        if state_tuple in dead_ends:
            continue

        game_over = is_game_completed(new_state)
        
        tube_score = 0
        original_to_tube = move.to_tube
        if original_to_tube.is_empty():
            tube_score -= 10
        
        move_score = len(find_all_legal_movements(new_state, dead_ends))
        from_tube = move.from_tube
        tube_score += initial_tube_scores[from_tube.name]
        final_score = move_score + tube_score
        valid_states_with_scores.append((new_state, move, game_over, final_score))

    if not game_over: 
      valid_states_with_scores.sort(key=lambda x: (not x[2], -x[3]), reverse=False)
      

    for state, move, game_complete, score in valid_states_with_scores[:5]:
        move_data = {
            "state": [tube_to_dict(tube) for tube in state.tubes],
            "movement": [
                {"name": move.from_tube.name, "colors": move.from_tube.colors},
                {"name": move.to_tube.name, "colors": move.to_tube.colors},
            ],
            "game_completed": game_complete,
            "score": score
        }
        top_states.append(move_data)
    return top_states
