import os
import http.server
import socketserver
import webbrowser
import json
import copy
from typing import List, Dict, Any, Optional, Tuple
from game_solve import initialize_tubes
from depth_search import get_top_states_with_scores, solve_puzzle
from tube_setup import Movement, tubes_list_to_dict
from game_setup import GameState, find_all_legal_movements, is_game_completed, get_new_state


class TubeVisualizer:
    def __init__(self) -> None:
        self.current_state: GameState = initialize_tubes()
        self.dead_ends: set[Tuple[Tuple[Optional[str], ...], ...]] = set()

    def apply_move(self, game_state: GameState, move: Movement) -> Dict[str, Any]:
        """Applies the selected move to the given game state."""
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
    
    def solve_puzzle_api(self):
        """Handles the /api/solve_puzzle API request."""
        try:
            solution = solve_puzzle(self.current_state, self.dead_ends)
            if solution:
                solution_json = [{"from": move.from_tube.name, "to": move.to_tube.name} for move in solution]
                return {"status": "success", "solution": solution_json}
            else:
                return {"status": "failure", "message": "No solution found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, request, client_address, server, visualizer):
            self.visualizer = visualizer
            super().__init__(request, client_address, server)

        def do_GET(self):
            if self.path == "/api/initial_state":
                initial_game_state: GameState = initialize_tubes()
                tubes_data: List[Dict[str, Any]] = tubes_list_to_dict(initial_game_state.tubes)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"tubes": tubes_data}).encode())

            elif self.path == "/api/top_moves":
                top_moves: List[Dict[str, Any]] = get_top_states_with_scores(self.visualizer.current_state, self.visualizer.dead_ends)

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "top_moves": top_moves,
                        }
                    ).encode()
                )

            else:
                # This will use SimpleHTTPRequestHandler's default behavior
                super().do_GET()

        def do_POST(self):
            try:
                if self.path == "/api/apply_move":
                    content_length: int = int(self.headers["Content-Length"])
                    post_data: bytes = self.rfile.read(content_length)
                    data: Dict[str, Any] = json.loads(post_data)

                    from_tube_name: str = data["from_tube"]
                    to_tube_name: str = data["to_tube"]

                    make_movement: Movement = Movement(
                        from_tube=next(
                            tube
                            for tube in self.visualizer.current_state.tubes
                            if tube.name == from_tube_name
                        ),
                        to_tube=next(
                            tube
                            for tube in self.visualizer.current_state.tubes
                            if tube.name == to_tube_name
                        ),
                    )

                    result: Dict[str, Any] = self.visualizer.apply_move(self.visualizer.current_state, make_movement)

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())

                elif self.path == "/api/undo_move":
                    result = self.visualizer.undo_move()
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())

                elif self.path == "/api/solve_puzzle":
                    result = self.visualizer.solve_puzzle_api()
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())

                else:
                    self.send_response(404)
                    self.end_headers()
            except Exception as e:
                self.send_response(500)  # Internal Server Error
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "Failed to perform action", "details": str(e)}).encode()
                )
def start_local_server(port: int = 8000, filename: str = "index.html") -> None:
    """
    Starts a local web server to serve the HTML file.
    """
    visualizer = TubeVisualizer()
    handler = lambda *args, visualizer=visualizer, **kwargs: TubeVisualizer.MyHandler(*args, visualizer=visualizer, **kwargs)
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(
            f"Serving at http://localhost:{port}/{os.path.basename(filename)}"
        )
        webbrowser.open(
            f"http://localhost:{port}/{os.path.basename(filename)}"
        )
        httpd.serve_forever()


def main() -> None:
    start_local_server()


if __name__ == "__main__":
    main()
