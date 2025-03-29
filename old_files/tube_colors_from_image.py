import os
import http.server
import socketserver
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

# Get API key from environment variable
ANTHROPIC_API_KEY = os.getenv("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")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

class TubeAnalyzerHandler(http.server.BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle preflight requests for CORS"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path == "/api/analyze_tubes":
                # Get the content length from headers
                content_length = int(self.headers["Content-Length"])
                
                # Read the POST data
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                # Extract the image data (base64 encoded)
                image_data = data.get("image_data", "")
                
                if not image_data:
                    self._send_error(400, "No image data provided")
                    return
                
                # Remove data URL prefix if present
                if image_data.startswith("data:image"):
                    image_data = image_data.split(",", 1)[1]
                
                # Send to Claude API and get results
                tube_colors = self._analyze_image_with_claude(image_data)
                
                # Return results
                result = {"success": True, "tube_colors": tube_colors}
                self._send_response(200, result)
                
            else:
                self._send_error(404, "Endpoint not found")
                
        except Exception as e:
            self._send_error(500, f"Server error: {str(e)}")
    
    def _analyze_image_with_claude(self, image_data: str) -> Dict[str, Any]:
        """Send the image to Claude API and analyze the tubes"""
        
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        # Prepare the prompt for Claude
        prompt = """
        I want the tube colours from this image in a json, which will be used in python. 
        Format will be tube_number: [bottom_color, second_color, third_color, top_color]. Give None for empty slots.
        
        The list of colors has to be from: TOTAL_COLORS = { "RED", "LIGHT_GREEN", "BLUE", "LIGHT_BLUE", "GREY", 
        "ORANGE", "BROWN", "MEHENDI", "PINK", "PURPLE", "YELLOW", "GREEN", None, }
        
        Give me the json structure directly without explanation.
        """
        
        # Prepare the request to Claude's API
        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY
        }
        
        # Create the payload
        payload = {
            "model": "claude-3-7-sonnet-20250219",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        }
                    ]
                }
            ]
        }
        
        # Convert payload to JSON
        payload_json = json.dumps(payload).encode("utf-8")
        
        # Create the request
        req = urllib.request.Request(
            CLAUDE_API_URL,
            data=payload_json,
            headers=headers,
            method="POST"
        )
        
        # Send the request and get the response
        try:
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                
                # Extract the response text
                response_text = response_data["content"][0]["text"]
                
                # Extract just the JSON part
                return self._extract_json(response_text)
                
        except urllib.error.HTTPError as e:
            error_message = e.read().decode("utf-8")
            raise Exception(f"Claude API error ({e.code}): {error_message}")
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON data from Claude's response text"""
        try:
            # Look for JSON object in the response
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
            
            # If JSON parsing fails, return the raw text
            return {"raw_response": text}
        except Exception:
            return {"raw_response": text}
    
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


def start_server(port: int = 8000) -> None:
    """Start the HTTP server"""
    handler = TubeAnalyzerHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    # Make sure the API key is set
    if not ANTHROPIC_API_KEY:
        exit(1)
    
    # Start the server
    start_server()