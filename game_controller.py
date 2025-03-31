import copy
from typing import List, Dict, Any, Optional, Tuple, Set

from game_setup import GameState, find_all_legal_movements, is_game_completed, get_new_state
from tube_setup import Movement, Tube, tubes_list_to_dict
from depth_search import get_top_states_with_scores, solve_puzzle
from game_solve import initialize_tubes


class GameController:
    """
    Handles game state management and game logic for the Water Sort Puzzle.
    This class is responsible for applying moves, undoing moves, and solving the puzzle.
    """

    def __init__(self) -> None:
        """Initialize the game controller with a default game state."""
        self.current_state: GameState = initialize_tubes()
        self.dead_ends: Set[Tuple[Tuple[Optional[str], ...], ...]] = set()

    def apply_move(self, game_state: GameState, move: Movement) -> Dict[str, Any]:
        """
        Applies the selected move to the given game state.
        
        Args:
            game_state: The current game state
            move: The movement to apply
            
        Returns:
            A dictionary with the result of the move, including the new tubes state
        """
        new_game_state: GameState = get_new_state(game_state, move)
        tubes_data = tubes_list_to_dict(new_game_state.tubes)

        self.current_state = copy.deepcopy(new_game_state)

        result = {"status": "success", "tubes": tubes_data}

        if is_game_completed(self.current_state):
            final_move_list: List[Dict[str, str]] = [
                {"from": move.from_tube.name, "to": move.to_tube.name}
                for move in new_game_state.moves
            ]
            result["game_completed"] = True
            result["final_move_list"] = final_move_list
            return result

        if not find_all_legal_movements(self.current_state, self.dead_ends):
            self.dead_ends.add(tuple(tuple(tube.colors) for tube in self.current_state.tubes))
            result["dead_end"] = True
        return result

    def undo_move(self) -> Dict[str, Any]:
        """
        Undoes the last move.
        
        Returns:
            A dictionary with the result of the undo operation, including the new tubes state
        """
        if not self.current_state.previous_state:
             return {"status": "success", "tubes": tubes_list_to_dict(self.current_state.tubes)}
        self.current_state = self.current_state.previous_state
        tubes_data = tubes_list_to_dict(self.current_state.tubes)
        top_moves: List[Dict[str, Any]] = get_top_states_with_scores(self.current_state, self.dead_ends)

        result = {"status": "success", "tubes": tubes_data}

        if len(top_moves) == 0:
            self.dead_ends.add(tuple(tuple(tube.colors) for tube in self.current_state.tubes))
            result["dead_end"] = True
            print("Dead end after doing undo. Moving back the movement")

        return result

    def solve_puzzle_api(self) -> Dict[str, Any]:
        """
        Solves the puzzle from the current state.
        
        Returns:
            A dictionary with the solution or an error message
        """
        try:
            solution = solve_puzzle(self.current_state, self.dead_ends)
            if solution:
                solution_json = [{"from": move.from_tube.name, "to": move.to_tube.name} for move in solution]
                return {"status": "success", "solution": solution_json}
            else:
                return {"status": "failure", "message": "No solution found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def set_initial_state(self, tube_colors_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sets a new initial game state from the provided data.
        
        Args:
            tube_colors_data: A list of dictionaries containing tube data
            
        Returns:
            A dictionary with the result of the operation, including the new tubes state
        """
        try:
            tubes = []
            # Ensure tube_colors_data is the list of dicts, not the whole JSON object
            if not isinstance(tube_colors_data, list):
                 raise TypeError(f"Expected a list of tube data, but got {type(tube_colors_data)}")

            for tube_dict in tube_colors_data: # Iterate over the list
                tube_name = tube_dict["name"]
                colors = tube_dict["colors"]
                # Ensure colors is a list
                if not isinstance(colors, list):
                    raise TypeError(f"Expected a list of colors for tube {tube_name}, but got {type(colors)}")
                fixed_colors = list(map(lambda x: None if isinstance(x, str) and x.lower() == "none" else x, colors))
                make_tube = Tube(fixed_colors, tube_name)
                tubes.append(make_tube)
            self.current_state = GameState(tubes)
            self.dead_ends = set()
            # Return success status, maybe the tubes data for confirmation?
            return {"status": "success", "tubes": tubes_list_to_dict(self.current_state.tubes)}
        except Exception as e:
            # Provide more context in the error message
            return {"status": "error", "message": f"Error setting initial state: {str(e)}"}
