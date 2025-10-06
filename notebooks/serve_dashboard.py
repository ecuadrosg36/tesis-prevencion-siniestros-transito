
#!/usr/bin/env python3
"""
Simple web server for the dashboard
Run this script and open http://localhost:8000 in your browser
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8000
DIRECTORY = Path.cwd()

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        super().end_headers()

def run_server():
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        print(f"Open http://localhost:{PORT}/dashboard.html in your browser")
        print("Press Ctrl+C to stop the server")

        # Auto-open browser
        webbrowser.open(f'http://localhost:{PORT}/dashboard.html')

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")

if __name__ == "__main__":
    run_server()
