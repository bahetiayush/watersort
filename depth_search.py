import copy
from typing import List, Tuple, Dict, Any, Optional
from game_setup import (
    GameState,
    is_game_completed,
    find_all_legal_movements,
    is_dead_end,
)
from tube_setup import Tube, tube_to_dict, Movement


# Set of dead ends
dead_ends: set[Tuple[Tuple[Optional[str], ...], ...]] = set()


def get_new_state(game_state: GameState, move: Movement) -> GameState:
    """
    Applies a single move to a game state and returns the new state.
    """
    new_list_of_tubes: List[Tube] = copy.deepcopy(game_state.tubes)

    # Find the matching tubes by name (a bit more robust)
    from_tube: Tube = next(
        tube for tube in new_list_of_tubes if move.from_tube.name == tube.name
    )
    to_tube: Tube = next(
        tube for tube in new_list_of_tubes if move.to_tube.name == tube.name
    )
    new_move = copy.deepcopy(move)
    new_move.from_tube = from_tube
    new_move.to_tube = to_tube

    new_move.execute()

    new_game_state: GameState = GameState(
        tubes=new_list_of_tubes, movement=new_move, previous_state=game_state
    )
    return new_game_state


def get_score_by_state(game_state: GameState) -> int:
    """Calculates a score for a given state of tubes."""
    score: int = 0

    completed_tubes: int = 0
    for tube in game_state.tubes:
        if tube.completed_tube():
            completed_tubes += 1
    score += completed_tubes * 10

    possible_movements = len(find_all_legal_movements(game_state.tubes)) / 2
    score += possible_movements * 2
    game_state.score = score
    return score


def get_top_states_with_scores(
    game_state: GameState,
) -> List[Dict[str, Any]]:
    """
    Retrieves the top 5 possible states with their corresponding scores.

    Args:
        game_state: The current GameState.

    Returns:
        A list of dictionaries, where each dictionary represents a move and its score.
    """
    top_states_with_scores: List[Dict[str, Any]] = []

    possible_moves = find_all_legal_movements(game_state.tubes)

    valid_states_with_scores: List[Tuple[GameState, Movement, int]] = []

    for move in possible_moves:
        new_state: GameState = get_new_state(game_state, move)

        # Check if the new state is in dead_ends
        state_tuple = tuple(tuple(tube.colors) for tube in new_state.tubes)
        if state_tuple in dead_ends:
            continue  # Skip this state if it's in dead_ends

        score: int = get_score_by_state(new_state)
        # Only add the state, if it has a score higher than 0
        if score > 0:
            valid_states_with_scores.append((new_state, move, score))

    # Sort by score in descending order
    valid_states_with_scores.sort(key=lambda x: x[2], reverse=True)

    for state, move, score in valid_states_with_scores[:5]:
        top_states_with_scores.append(
            {
                "state": [tube_to_dict(tube) for tube in state.tubes],
                "movement": [
                    {"name": move.from_tube.name, "colors": move.from_tube.colors},
                    {"name": move.to_tube.name, "colors": move.to_tube.colors},
                ],
                "score": score,
            }
        )

    return top_states_with_scores

