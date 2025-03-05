from depth_search import get_top_moves_with_scores, dead_ends
from game_setup import GameState
from tube_setup import Tube
from typing import Tuple, Optional
from depth_search import get_new_state, Movement

def test_get_top_moves_with_scores_zero_moves():
    """Test get_top_moves_with_scores with a state where no moves are possible."""

    # Example 1 (Zero Moves):
    # Tube 1: [RED, BLUE, GREEN, YELLOW]
    # Tube 2: [PURPLE, ORANGE, GREY, LIGHT_BLUE]
    # Tube 3: [PINK, BROWN, MEHENDI, LIGHT_GREEN]
    tube1: Tube = Tube(["RED", "BLUE", "GREEN", "YELLOW"], "tube1")
    tube2: Tube = Tube(["PURPLE", "ORANGE", "GREY", "LIGHT_BLUE"], "tube2")
    tube3: Tube = Tube(["PINK", "BROWN", "MEHENDI", "LIGHT_GREEN"], "tube3")

    game_state: GameState = GameState([tube1, tube2, tube3])

    # Manually define the dead end state
    dead_ends_tuple: set[Tuple[Tuple[Optional[str], ...], ...]] = {
        (("RED", "BLUE", "GREEN", "YELLOW"), ("PURPLE", "ORANGE", "GREY", "LIGHT_BLUE"), ("PINK", "BROWN", "MEHENDI", "LIGHT_GREEN"))
    }
    
    # Add the dead_ends_tuple to the dead ends set
    dead_ends.update(dead_ends_tuple)

    # Call get_top_moves_with_scores
    top_moves = get_top_moves_with_scores(game_state)

    # Assert that the result is an empty list
    assert len(top_moves) == 0

def test_get_top_moves_with_scores_one_move_to_dead_end():
    """Test get_top_moves_with_scores with a state that can go to a dead end."""

    # Example 2 (One Move to Dead End):
    # Tube 1: [RED, RED, BLUE, BLUE]
    # Tube 2: [GREEN, GREEN, ORANGE, ORANGE]
    # Tube 3: [None, None, None, None]
    tube1: Tube = Tube(["RED", "RED", "BLUE", "BLUE"], "tube1")
    tube2: Tube = Tube(["GREEN", "GREEN", "ORANGE", "ORANGE"], "tube2")
    tube3: Tube = Tube([None, None, None, None], "tube3")
    
    game_state: GameState = GameState([tube1, tube2, tube3])
    
    # move from 1 to 3
    move = Movement(tube1, tube3)

    game_state_after_move: GameState = get_new_state(game_state,move)
    
    # Manually define the dead end state
    dead_ends_tuple: set[Tuple[Tuple[Optional[str], ...], ...]] = {
        (("RED", "RED", None, None), ("GREEN", "GREEN", "ORANGE", "ORANGE"), ("BLUE", "BLUE", None, None))
    }

    # Add the dead_ends_tuple to the dead ends set
    dead_ends.update(dead_ends_tuple)

    # Call get_top_moves_with_scores
    top_moves = get_top_moves_with_scores(game_state_after_move)

    # Assert that the result is an empty list
    assert len(top_moves) == 0

