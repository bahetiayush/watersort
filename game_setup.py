import copy
from typing import Any, List, Tuple, Set, Dict, Optional
from tube_setup import Tube, Movement  # import Movement


class GameState:
    def __init__(
        self,
        tubes: List[Tube],
        previous_state=None,
        movement: Optional[Movement] = None,):
        
        self.moves: List[str] = []
        self.tubes: List[Tube] = tubes
        self.movement: Optional[Movement] = movement
        self.previous_state: Optional[GameState] = previous_state
        self.score: Optional[int] = None

    def __repr__(self) -> str:
        return f"GameState(tubes={self.tubes}, movement={self.movement})"
    
    def add_move(self, move: Movement):
        """Adds a move to the game state's move history."""
        self.moves.append(str(move))


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
        list_of_tubes: A list of Tube objects.

    Returns:
        True if the game is completed, False otherwise.
    """
    return all(
        tube.empty_tube() or tube.completed_tube() for tube in game_state.tubes
    )  # use gamestate.tubes


def net_possible_movements(game_state: GameState) -> int:
    """
    Calculates the total number of possible movements between tubes.

    Args:
        list_of_tubes: A list of Tube objects.

    Returns:
        The total number of possible movements.
    """
    possible_movements: List[Movement] = find_all_legal_movements(
        game_state.tubes
    )  # Use Movement object.
    return int(len(possible_movements))


def get_color_scores(game_state: GameState) -> List[
    List[object]
]:
    """
    Calculates a score for each color based on its position in the tubes.

    Args:
        list_of_tubes: A list of Tube objects.

    Returns:
        A list containing two lists:
        - The first inner list contains the colors.
        - The second inner list contains the corresponding scores.
    """
    all_color_list: List[str] = all_colors(
        game_state.tubes
    )  # use game state
    all_color_values: List[List[object]] = [[], []]

    color_scores: Dict[int, int] = {0: 10, 1: 7, 2: 4, 3: 1}

    for color in all_color_list:
        total_score: int = 0
        for tube in game_state.tubes:  # use gamestate
            for index, tube_color in enumerate(reversed(tube.colors)):
                if color == tube_color:
                    total_score += color_scores.get(index, 0)
        all_color_values[0].append(color)
        all_color_values[1].append(total_score)

    return all_color_values


def is_dead_end(game_state: GameState) -> bool:
    """
    Checks if the current game state is a dead end.

    Args:
        list_of_tubes: A list of Tube objects.

    Returns:
        True if the game is in a dead end, False otherwise.
    """
    if is_game_completed(game_state):
        return False
    return not find_all_legal_movements(game_state.tubes)


def find_all_legal_movements(list_of_tubes: List[Tube]) -> List[
    Movement
]:
    """
    Finds all legal movements between tubes.

    Args:
        list_of_tubes: A list of Tube objects (the current state).

    Returns:
        A list of tuples, where each tuple is a (from_tube, to_tube) move.
    """
    legal_movements: List[Movement] = []
    empty_tubes: List[Tube] = [tube for tube in list_of_tubes if tube.is_empty()]
    non_empty_tubes: List[Tube] = [
        tube for tube in list_of_tubes if not tube.is_empty()
    ]

    representative_empty_tube: Optional[Tube] = (
        empty_tubes[0] if empty_tubes else None
    )

    for from_tube in list_of_tubes:
        # Moves to non-empty tubes
        for to_tube in non_empty_tubes:
            movement: Movement = Movement(from_tube, to_tube)
            if movement.is_possible():
                legal_movements.append(movement)

        # Move to the representative empty tube (if any)
        if representative_empty_tube:
            movement: Movement = Movement(from_tube, representative_empty_tube)
            if movement.is_possible():
                legal_movements.append(movement)
    return legal_movements
