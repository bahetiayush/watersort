import base64
import os
import http.server
import re
import socketserver
import webbrowser
import json
import copy
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

import requests
from game_solve import initialize_tubes
from depth_search import get_top_states_with_scores, solve_puzzle
from tube_setup import Movement, Tube, tubes_list_to_dict, COLORS_WITH_HEX
from game_setup import GameState, find_all_legal_movements, is_game_completed, get_new_state

# --- Claude API Configuration ---
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

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

    def _analyze_image_with_claude(self, image_data: str, image_type: str) -> Dict[str, Any]:
        """Sends image to Claude API, handles response, and returns tube colors."""
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        total_colors_str = str(COLORS_WITH_HEX)
        example_json = {
        "tubes": [
            {"name": "Tube1", "colors": ["BROWN", "LIGHT_GREEN", "BLUE", "GREY"]},
            {"name": "Tube2", "colors": ["GREEN", "RED", "RED", "GREEN"]},
        ]
    }
        example_json_str = json.dumps(example_json, indent=2)

        # Construct Claude API request
        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
        }
        payload = {
            "model": "claude-3-7-sonnet-20250219",
            "max_tokens": 1000,
            "system": "You are a JSON-only response bot. Never include explanations or text outside of valid JSON structures.",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""I want the tube colours from this image in a json, which will be used in python. 
                                    I need a JSON array representing the colors in each tube.  Do not include any explanation,
                                      your response needs to be directly parsable.
                                    
                                    Each object in the array should have a "name" (e.g., "Tube1", "Tube2", etc.) 
                                    and a "colors" array with 4 elements (colors in each tube, from bottom to top. Use "None" for empty slots).
                                    
                                    Each colour can be used exactly 4 times. The last 2 tubes must be empty. All other tubes are full (4 slots).
                                    Pay special attention to tubes with repeated colours - they are blended together.
                                    
                                    Validation: In case the colours don't add up to 4, please check the response again.

                                    Ideally, go tube by tube and check the 4 colours. Don't explain your thinking but always go tube by tube.

                                    Colours must be from this list. Check the hex code for the approx match:
                                    {total_colors_str}

                                    The JSON should look like this:
                                    {example_json_str}
                                    """,
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image_type,
                                "data": image_data,
                            },
                        },
                    ],
                }
            ],
        }
        try:
            response = requests.post(CLAUDE_API_URL, headers=headers, json=payload)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            response_data = response.json()
            result_text = response_data["content"][0]["text"]
            return self._extract_json(result_text)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with Claude API: {e}")
        except Exception as e:
            raise Exception(f"Error processing Claude response: {str(e)}")

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            start_idx = text.find("{")
            end_idx = text.rfind("}") + 1
            if start_idx != -1 and end_idx != 0:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
            return {"raw_response": text}
        except Exception:
            return {"raw_response": text}
    
    def set_initial_state(self, tube_colors: Dict[str, List[Optional[str]]]) -> Dict[str, Any]:
        """Sets a new initial game state from the provided data."""
        try:
            tubes = []
            for tube in tube_colors:
                tube_name = tube["name"]
                colors = tube["colors"]
                fixed_colors = list(map(lambda x: None if x.lower() == "none" else x, colors))
                make_tube = Tube(fixed_colors, tube_name)
                tubes.append(make_tube)
            self.current_state = GameState(tubes)
            self.dead_ends = set()
        except Exception as e:
            return {"status": "error", "message": str(e)}


class MyHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, request, client_address, server, visualizer):
        self.visualizer: TubeVisualizer = visualizer
        super().__init__(request, client_address, server)

    def do_GET(self):
        try:
            if self.path == "/api/initial_state":
                current_game_state: GameState = self.visualizer.current_state
                tubes_data: List[Dict[str, Any]] = tubes_list_to_dict(current_game_state.tubes)
                self._send_response(200, {"tubes": tubes_data})

            elif self.path == "/api/top_moves":
                top_moves: List[Dict[str, Any]] = get_top_states_with_scores(self.visualizer.current_state, self.visualizer.dead_ends)
                self._send_response(200, {"top_moves": top_moves})

            else:
                # This will use SimpleHTTPRequestHandler's default behavior
                super().do_GET()
        except Exception as e:
            self._send_error(500, f"Server error: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle preflight requests for CORS"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

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
                self._send_response(200, result)

            elif self.path == "/api/undo_move":
                result = self.visualizer.undo_move()
                self._send_response(200, result)

            elif self.path == "/api/solve_puzzle":
                result = self.visualizer.solve_puzzle_api()
                if result.get("status") == "success":
                  self._send_response(200, result)
                else:
                  self._send_error(400, result.get("message"))

            elif self.path == "/api/analyze_tubes":

                content_length = int(self.headers["Content-Length"])
                content_type = self.headers.get("Content-Type")

                if content_type and "multipart/form-data" in content_type:
                    # Read the POST data
                    post_data = self.rfile.read(content_length)
                    
                    # Parse multipart form data
                    parser = MultipartFormParser(content_type, post_data)
                    form_data = parser.parse()
                    
                    # Extract image and image_type
                    image_data = None
                    image_type = None
                    
                    if 'image' in form_data:
                        image_file = form_data['image']
                        image_data = base64.b64encode(image_file['content']).decode('utf-8')
                    
                    if 'image_type' in form_data:
                        # If provided separately
                        image_type = form_data['image_type']
                    
                    if not image_data:
                        self._send_error(400, "No image data provided")
                        return
                    tube_colors_from_claude = self.visualizer._analyze_image_with_claude(image_data, image_type)
                    result = {"status": "success", "tubes": tube_colors_from_claude["tubes"]}
                    self.visualizer.set_initial_state(tube_colors_from_claude["tubes"])
                    self._send_response(200, result)

        except Exception as e:
                    self._send_error(500, f"Some error occurred: {str(e)}") 


    def _send_response(self, status_code: int, data: Dict[str, Any]) -> None:
        """Send a JSON response"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, status_code: int, message: str) -> None:
        """Send an error response"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        error_data = {"success": False, "error": message}
        self.wfile.write(json.dumps(error_data).encode())

class MultipartFormParser:
    """Parser for multipart/form-data requests"""
    
    def __init__(self, content_type: str, data: bytes):
        self.content_type = content_type
        self.data = data
        self.boundary = self._get_boundary()
        
    def _get_boundary(self) -> bytes:
        """Extract boundary from content type header"""
        match = re.search(r'boundary=(.+)', self.content_type)
        if match:
            return match.group(1).encode()
        raise ValueError("Boundary not found in content type")
    
    def parse(self) -> Dict[str, Any]:
        """Parse the multipart form data and return a dictionary of fields"""
        result = {}
        
        # Split data by boundary
        parts = self.data.split(b'--' + self.boundary)
        
        # Skip the first and last parts (they're empty or just '--')
        for part in parts[1:-1]:
            # Skip the initial newline
            if part.startswith(b'\r\n'):
                part = part[2:]
                
            # Split headers and content
            headers_end = part.find(b'\r\n\r\n')
            if headers_end == -1:
                continue
                
            headers_raw = part[:headers_end]
            content = part[headers_end + 4:]  # +4 to skip '\r\n\r\n'
            
            # Parse headers
            headers = {}
            for header_line in headers_raw.split(b'\r\n'):
                if b':' in header_line:
                    header_name, header_value = header_line.split(b':', 1)
                    headers[header_name.strip().lower().decode()] = header_value.strip().decode()
            
            # Extract field name
            field_name = None
            if 'content-disposition' in headers:
                cd_parts = headers['content-disposition'].split(';')
                for cd_part in cd_parts:
                    if 'name=' in cd_part:
                        field_name = cd_part.split('=', 1)[1].strip('"\'')
                        break
            
            if not field_name:
                continue
            
            # Handle file fields
            if 'filename=' in headers.get('content-disposition', ''):
                filename = re.search(r'filename="([^"]*)"', headers['content-disposition'])
                if filename:
                    filename = filename.group(1)
                    # Remove the trailing \r\n from content if it exists
                    if content.endswith(b'\r\n'):
                        content = content[:-2]
                    # Store file data
                    result[field_name] = {
                        'filename': filename,
                        'content': content,
                        'content_type': headers.get('content-type', 'application/octet-stream')
                    }
            else:
                # Regular field
                # Remove the trailing \r\n from content if it exists
                if content.endswith(b'\r\n'):
                    content = content[:-2]
                result[field_name] = content.decode()
                
        return result


def start_local_server(port: int = 8000, filename: str = "index.html") -> None:
    """
    Starts a local web server to serve the HTML file.
    """
    visualizer = TubeVisualizer()
    handler = lambda *args, visualizer=visualizer, **kwargs: MyHandler(*args, visualizer=visualizer, **kwargs)
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(
            f"Serving at http://localhost:{port}/{os.path.basename(filename)}"
        )
        webbrowser.open(
            f"http://localhost:{port}/{os.path.basename(filename)}"
        )
        httpd.serve_forever()

def main() -> None:
    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        exit(1)
    start_local_server()

if __name__ == "__main__":
    main()
