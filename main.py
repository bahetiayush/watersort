#!/usr/bin/env python3
import os
import socket
import socketserver
import webbrowser
import http.server
from typing import Type

from game_controller import GameController
from http_server import create_handler_class


def start_local_server(port: int = 8000, filename: str = "index.html") -> None:
    """
    Starts a local web server to serve the HTML file.
    
    Args:
        port: The port to run the server on
        filename: The HTML file to serve
    """
    # Create the game controller
    game_controller = GameController()
    
    # Create the handler class with the game controller injected
    handler_class = create_handler_class(game_controller)

    # Enable socket reuse
    socketserver.TCPServer.allow_reuse_address = True

    # Check if port is already in use
    addr = ("", port)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(addr)
    except OSError as e:
        if e.errno == socket.errno.EADDRINUSE:
            print(f"Port {port} is already in use. Please close the other process or choose a different port.")
            exit(1)
        else:
            raise

    print(f"Attempting to start server on port {port}...")
    with socketserver.TCPServer(addr, handler_class) as httpd:
        print(
            f"Serving at http://localhost:{port}/{os.path.basename(filename)}"
        )
        # Open browser only if server starts successfully
        webbrowser.open(
            f"http://localhost:{port}/{os.path.basename(filename)}"
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            # No need to call httpd.server_close() here, 'with' statement handles it
        finally:
            print("Server shut down.")


def main() -> None:
    """Main entry point for the application."""
    # Check for API keys
    from image_analyzer import ANTHROPIC_API_KEY, OPENROUTER_API_KEY
    
    if not ANTHROPIC_API_KEY and not OPENROUTER_API_KEY:
        print("Error: Neither ANTHROPIC_API_KEY nor OPEN_ROUTER_KEY environment variables are set.")
        print("Please set at least one API key in your .env file.")
        exit(1)
        
    # Start the server
    start_local_server()


if __name__ == "__main__":
    main()
