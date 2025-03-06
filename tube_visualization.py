import os
import http.server
import socketserver
import webbrowser
import json
import copy
from typing import List, Dict, Any, Optional, Tuple
from game_solve import initialize_tubes
from depth_search import get_top_states_with_scores, dead_ends
from tube_setup import tube_to_dict, Movement
from game_setup import GameState, is_game_completed, is_dead_end
import random


current_state: GameState = initialize_tubes()
previous_states: List[GameState] = [current_state]


def apply_move(move_index: str) -> Dict[str, Any]:
    """Applies the selected move to the current state."""
    global current_state
    global previous_states

    top_moves: List[Dict[str, Any]] = get_top_states_with_scores(current_state)

    if not top_moves:
        tubes_data: List[Dict[str, Any]] = []
        for tube in current_state.tubes:
            tubes_data.append(tube_to_dict(tube))
        return {
            "status": "error",
            "message": "No top moves found for the current state",
            "tubes": tubes_data,
        }

    selected_move_data: Dict[str, Any] = top_moves[int(move_index)]

    if selected_move_data["movement"]:
        selected_move = Movement(
            from_tube=next(
                tube
                for tube in current_state.tubes
                if tube.name == selected_move_data["movement"][0]["name"]
            ),
            to_tube=next(
                tube
                for tube in current_state.tubes
                if tube.name == selected_move_data["movement"][1]["name"]
            ),
        )
        previous_states.append(
            copy.deepcopy(current_state)
        )  # Append a DEEP COPY of current state
        selected_move.execute()
        current_state = GameState(
            tubes=current_state.tubes,
            movement=selected_move,
            previous_state=current_state,
        )

        tubes_data: List[Dict[str, Any]] = []
        for tube in current_state.tubes:
            tubes_data.append(tube_to_dict(tube))

        return {"status": "success", "tubes": tubes_data}

    else:
        tubes_data: List[Dict[str, Any]] = []
        for tube in current_state.tubes:
            tubes_data.append(tube_to_dict(tube))
        return {
            "status": "error",
            "message": "Selected move is not valid",
            "tubes": tubes_data,
        }


def undo_move() -> Dict[str, Any]:
    global current_state
    global previous_states

    if len(previous_states) > 1:
        current_state = previous_states.pop()
        current_state.movement = None  # remove movement from state
        current_state.previous_state = None  # remove previous_state from state

    new_top_moves: List[Dict[str, Any]] = get_top_states_with_scores(current_state)

    # Format data to send to frontend
    tubes_data: List[Dict[str, Any]] = []
    for tube in current_state.tubes:
        tubes_data.append(tube_to_dict(tube))

    return {"status": "success", "tubes": tubes_data, "top_moves": new_top_moves}


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/initial_state":
            initial_game_state: GameState = initialize_tubes()
            tubes_data: List[Dict[str, Any]] = [
                tube_to_dict(tube) for tube in initial_game_state.tubes
            ]
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"tubes": tubes_data}).encode())

        elif self.path == "/api/top_moves":
            top_moves: List[Dict[str, Any]] = get_top_states_with_scores(current_state)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "top_moves": top_moves,
                        "state": [
                            tube_to_dict(tube) for tube in current_state.tubes
                        ],
                    }
                ).encode()
            )

        elif self.path == "/api/undo_move":
            result = undo_move()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        else:
            # This will use SimpleHTTPRequestHandler's default behavior
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/apply_move":
            content_length: int = int(self.headers["Content-Length"])
            post_data: bytes = self.rfile.read(content_length)
            data: Dict[str, Any] = json.loads(post_data)

            move_index: str = data["move_index"]
            result: Dict[str, Any] = apply_move(move_index)

            if result["status"] == "success":
                if is_game_completed(current_state):
                    result["game_completed"] = True
                elif is_dead_end(current_state):
                    dead_ends.add(
                        tuple(
                            tuple(tube.colors) for tube in current_state.tubes
                        )
                    )
                    if current_state.previous_state:
                        previous_state_tubes_data: List[Dict[str, Any]] = []
                        for tube in current_state.previous_state.tubes:
                            previous_state_tubes_data.append(
                                tube_to_dict(tube)
                            )
                        result["dead_end"] = True
                        result["previous_tubes"] = previous_state_tubes_data
                    else:
                        result["dead_end"] = True
                        result["previous_tubes"] = None

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        elif self.path == "/api/add_dead_end":
            content_length: int = int(self.headers["Content-Length"])
            post_data: bytes = self.rfile.read(content_length)
            data: Dict[str, Any] = json.loads(post_data)
            dead_ends.add(tuple(tuple(tube_data["colors"]) for tube_data in data["state"]))
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())

        else:
            self.send_response(404)
            self.end_headers()

def start_local_server(port: int = 8000, filename: str = "index.html") -> None:
    """
    Starts a local web server to serve the HTML file.
    """

    handler = MyHandler
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
