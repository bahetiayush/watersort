from typing import List, Optional, Any, Dict
from game_setup import GameState
from tube_setup import Tube

# Constants for controlling initial state
USE_DEFAULT_INITIAL_STATE = False  # Set to False to use TEST_INITIAL_STATE
# Constants for the default game state
DEFAULT_TUBE_COLORS: Dict[str, List[Any]] = {
    "Tube1": ["BROWN", "LIGHT_GREEN", "BLUE", "GREY"],
    "Tube2": ["GREEN", "RED", "RED", "GREEN"],
    "Tube3": ["PINK", "BLUE", "MEHENDI", "LIGHT_BLUE"],
    "Tube4": ["MEHENDI", "GREY", "BROWN", "ORANGE"],
    "Tube5": ["BLUE", "ORANGE", "LIGHT_BLUE", "PURPLE"],
    "Tube6": ["YELLOW", "YELLOW", "LIGHT_GREEN", "LIGHT_BLUE"],
    "Tube7": ["MEHENDI", "BLUE", "PURPLE", "GREY"],
    "Tube8": ["PINK", "RED", "GREEN", "ORANGE"],
    "Tube9": ["LIGHT_BLUE", "YELLOW", "GREY", "BROWN"],
    "Tube10": ["PURPLE", "PINK", "BROWN", "MEHENDI"],
    "Tube11": ["RED", "LIGHT_GREEN", "GREEN", "PURPLE"],
    "Tube12": ["YELLOW", "ORANGE", "LIGHT_GREEN", "PINK"],
    "Tube13": [None, None, None, None],
    "Tube14": [None, None, None, None],
}

# Constants for the test state
TEST_TUBE_COLORS: Dict[str, List[Any]] = {
    "tube1": ["RED", "RED", "BLUE", "BLUE"],
    "tube2": ["GREEN", "GREEN", "ORANGE", "ORANGE"],
    "tube3": ["ORANGE", "ORANGE", "BLUE", "BLUE"],
    "tube4": ["RED", "RED", "GREEN", "GREEN"],
    "tube5": [None, None, None, None],
}

def initialize_tubes() -> GameState:
    """
    Initializes the tubes for the water sort game, using either the default or test state.

    Returns:
        A GameState object representing the initial game state.
    """
    if USE_DEFAULT_INITIAL_STATE:
        tube_colors = DEFAULT_TUBE_COLORS
    else:
        tube_colors = TEST_TUBE_COLORS

    list_of_tubes: List[Tube] = [
        Tube(colors, name) for name, colors in tube_colors.items()
    ]
    initial_state = GameState(tubes=list_of_tubes)
    return initial_state

