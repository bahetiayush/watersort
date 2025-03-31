import http.server
import json
import base64
from typing import Dict, Any, List, Optional, Callable, Type

from form_parser import MultipartFormParser
from game_controller import GameController
from image_analyzer import ImageAnalyzer
from tube_setup import tubes_list_to_dict
from depth_search import get_top_states_with_scores


class HttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    HTTP request handler for the Water Sort Puzzle application.
    Handles API endpoints and serves static files.
    """

    def __init__(self, request, client_address, server, game_controller: GameController):
        self.game_controller: GameController = game_controller
        super().__init__(request, client_address, server)

    def do_GET(self):
        """Handle GET requests."""
        try:
            if self.path == "/api/initial_state":
                tubes_data: List[Dict[str, Any]] = tubes_list_to_dict(self.game_controller.current_state.tubes)
                self._send_response(200, {"tubes": tubes_data})

            elif self.path == "/api/top_moves":
                top_moves: List[Dict[str, Any]] = get_top_states_with_scores(
                    self.game_controller.current_state, 
                    self.game_controller.dead_ends
                )
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
        """Handle POST requests."""
        try:
            if self.path == "/api/apply_move":
                content_length: int = int(self.headers["Content-Length"])
                post_data: bytes = self.rfile.read(content_length)
                data: Dict[str, Any] = json.loads(post_data)

                from_tube_name: str = data["from_tube"]
                to_tube_name: str = data["to_tube"]

                from_tube = next(
                    tube
                    for tube in self.game_controller.current_state.tubes
                    if tube.name == from_tube_name
                )
                to_tube = next(
                    tube
                    for tube in self.game_controller.current_state.tubes
                    if tube.name == to_tube_name
                )

                from tube_setup import Movement
                move = Movement(from_tube=from_tube, to_tube=to_tube)

                result: Dict[str, Any] = self.game_controller.apply_move(
                    self.game_controller.current_state, 
                    move
                )
                self._send_response(200, result)

            elif self.path == "/api/undo_move":
                result = self.game_controller.undo_move()
                self._send_response(200, result)

            elif self.path == "/api/solve_puzzle":
                result = self.game_controller.solve_puzzle_api()
                if result.get("status") == "success":
                  self._send_response(200, result)
                else:
                  self._send_error(400, result.get("message"))
                  
            elif self.path == "/api/update_tubes":
                content_length: int = int(self.headers["Content-Length"])
                post_data: bytes = self.rfile.read(content_length)
                data: Dict[str, Any] = json.loads(post_data)
                
                if "tubes" not in data:
                    self._send_error(400, "Missing 'tubes' data in request")
                    return
                    
                set_state_result = self.game_controller.set_initial_state(data["tubes"])
                if set_state_result["status"] == "error":
                    self._send_error(500, f"Failed to update tubes: {set_state_result['message']}")
                    return
                    
                self._send_response(200, {
                    "status": "success", 
                    "tubes": tubes_list_to_dict(self.game_controller.current_state.tubes)
                })

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
                        image_type = image_file['content_type']

                    if not image_data:
                        self._send_error(400, "No image data provided")
                        return

                    # Use the analyze function to get the initial colors
                    provider_to_use = "anthropic"
                    tube_colors_from_llm = ImageAnalyzer.analyze_image_with_llm(
                        image_data, image_type, provider=provider_to_use
                    )

                    # Check if the LLM response indicates an error or failed JSON extraction
                    if "error" in tube_colors_from_llm:
                        self._send_error(500, f"LLM analysis failed: {tube_colors_from_llm['error']}. Raw response: {tube_colors_from_llm.get('raw_response', '')}")
                        return
                    if "tubes" not in tube_colors_from_llm:
                        self._send_error(500, f"LLM analysis failed: 'tubes' key missing in response. Raw response: {tube_colors_from_llm.get('raw_response', '')}")
                        return
                    
                    # Validate the colors
                    validation_result = ImageAnalyzer.validate_tube_colors(tube_colors_from_llm["tubes"])
                    
                    # If validation passes, return the result
                    if validation_result["valid"]:
                        print("Color validation passed")
                        result = {"status": "success", "tubes": tube_colors_from_llm["tubes"]}
                        self._send_response(200, result)
                        return
                    
                    # If validation fails, balance the colors
                    print("Color validation failed, balancing colors...")
                    balanced_tubes = ImageAnalyzer.balance_tube_colors(tube_colors_from_llm["tubes"])
                    
                    # Verify the balance
                    final_validation = ImageAnalyzer.validate_tube_colors(balanced_tubes)
                    if final_validation["valid"]:
                        print("Color balancing successful")
                        result = {"status": "success", "tubes": balanced_tubes}
                        self._send_response(200, result)
                    else:
                        print("Color balancing failed, returning original result with warning")
                        result = {
                            "status": "success",  # Still return success for frontend
                            "tubes": balanced_tubes,
                            "warning": "Colors may not be perfectly balanced"
                        }
                        self._send_response(200, result)

                else:
                     self._send_error(400, "Invalid content type, expected multipart/form-data")

            else:
                self._send_error(404, f"Endpoint not found: {self.path}")

        except Exception as e:
            self._send_error(500, f"Server error in POST handler: {str(e)}")

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


def create_handler_class(game_controller: GameController) -> Type[http.server.SimpleHTTPRequestHandler]:
    """
    Creates a handler class with the game controller injected.
    
    Args:
        game_controller: The game controller to inject
        
    Returns:
        A handler class with the game controller injected
    """
    class CustomHttpRequestHandler(HttpRequestHandler):
        def __init__(self, request, client_address, server):
            super().__init__(request, client_address, server, game_controller)
    
    return CustomHttpRequestHandler
