#!/usr/bin/env python3
"""
This module is kept for backward compatibility.
The functionality has been refactored into separate modules:
- form_parser.py: Contains the MultipartFormParser class
- image_analyzer.py: Contains the image analysis functionality
- game_controller.py: Contains the game logic
- http_server.py: Contains the HTTP server implementation
- main.py: Contains the entry point for the application
"""

# Import the main function from the main module
from main import main

# For backward compatibility, keep the TubeVisualizer name
from game_controller import GameController as TubeVisualizer

# If this file is run directly, call the main function
if __name__ == "__main__":
    main()
