import copy
from typing import Any, List, Dict, Optional
from tube_setup import Tube, Movement 

class GameState:
    def __init__(
        self,
        tubes: List[Tube],
        previous_state=None):
        
        self.moves: List[Movement] = []
        self.tubes: List[Tube] = tubes
        self.previous_state: Optional[GameState] = previous_state
        self.score: Optional[int] = None

    def __repr__(self) -> str:
        return f"GameState(tubes={self.tubes}, movement={self.movement})"
    
    def add_move(self, move: Movement):
        """Adds a move to the game state's move history."""
        self.moves.append(move)


def all_colors(list_of_tubes: List[Tube]) -> List[str]:
    """
    Gets a list of all unique colors in a list of tubes, excluding None.

    Args:
        list_of_tubes: A list of Tube objects.

    Returns:
        A list of unique color strings.
    """
    return list(
        set(
            color
            for tube in list_of_tubes
            for color in tube.colors
            if color is not None
        )
    )


def is_game_completed(game_state: GameState) -> bool:
    """
    Checks if the water sort game is completed.

    Args:
        game_state: GameState object

    Returns:
        True if the game is completed, False otherwise.
    """
    return all(
        tube.empty_tube() or tube.completed_tube() for tube in game_state.tubes
    )  

def find_all_legal_movements(game_state: GameState, dead_ends: set) -> List[
    Movement
]:
    """
    Finds all legal movements between tubes, excluding dead-end states.

    Args:
        game_state: A list of Tube objects (the current state).
        dead_ends: A set of tuples representing known dead-end states.

    Returns:
        A list of legal Movement objects.
    """
    legal_movements: List[Movement] = []
    candidate_to_tubes: List[Tube] = []
    first_empty_tube_added = False  # Flag to track if the first empty tube has been added

    for tube in game_state.tubes:
        if not tube.is_empty():
            candidate_to_tubes.append(tube)
        elif not first_empty_tube_added:
            candidate_to_tubes.append(tube)
            first_empty_tube_added = True
    
    for from_tube in game_state.tubes:
        for to_tube in candidate_to_tubes:
           _check_movement_and_add(from_tube, to_tube, game_state, dead_ends, legal_movements)
    return legal_movements

def _check_movement_and_add(
    from_tube: Tube,
    to_tube: Tube,
    game_state: GameState,
    dead_ends: set,
    legal_movements: List[Movement],
) -> None:
    """
    Checks if a movement is possible and adds it to legal_movements if it is not a dead end.
    Also adds the state to dead_ends if the hypothetical move state is a dead end.

    Args:
        from_tube: The tube to move from.
        to_tube: The tube to move to.
        list_of_tubes: The current list of tubes.
        dead_ends: The set of known dead-end states.
        legal_movements: The list of legal movements to add to.
    """
    movement: Movement = Movement(from_tube, to_tube)
    if movement.is_possible():
        # Create a hypothetical new state using get_new_state
        hypothetical_game_state: GameState = get_new_state(game_state, movement)
        hypothetical_state_tuple = tuple(tuple(tube.colors) for tube in hypothetical_game_state.tubes)
        
        # Check if hypothetical state is a dead end
        if hypothetical_state_tuple not in dead_ends and _are_there_any_moves(hypothetical_game_state):
             legal_movements.append(movement)
        elif not _are_there_any_moves(hypothetical_game_state):
             dead_ends.add(hypothetical_state_tuple)

def _are_there_any_moves(game_state: GameState) -> bool:
    """Check if there are any possible moves in current tubes"""
    for from_tube in game_state.tubes:
        for to_tube in game_state.tubes:
            movement = Movement(from_tube, to_tube)
            if movement.is_possible() or is_game_completed(game_state):
                return True
    return False

def get_new_state(game_state: GameState, move: Movement) -> GameState:
    """Applies a single move to a game state and returns the new state."""
    new_game_state: GameState = copy.deepcopy(game_state)

    from_tube: Tube = next(
        tube for tube in new_game_state.tubes if move.from_tube.name == tube.name
    )
    to_tube: Tube = next(
        tube for tube in new_game_state.tubes if move.to_tube.name == tube.name
    )

    new_move = Movement(from_tube, to_tube)
    new_move.execute()
    new_game_state.add_move(new_move)
    new_game_state.previous_state = game_state

    return new_game_state