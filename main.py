import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# Record the start time to calculate uptime
START_TIME = time.time()

class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Helper function to send JSON responses
        def send_json(status_code, data):
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        # Endpoint 1: Status Check
        if self.path == '/status':
            uptime = round(time.time() - START_TIME, 2)
            send_json(200, {"status": "OK", "uptime": uptime})
            
        # Endpoint 2: Data Resource
        elif self.path == '/api/data':
            send_json(200, {"message": "Hello from the backend!", "items": [1, 2, 3]})
            
        # Catch-all for 404 Not Found
        else:
            send_json(404, {"error": "Not Found"})

# Start the server on port 3000
if __name__ == "__main__":
    # Use 'localhost' and port 3000
    server_address = ('localhost', 3000)
    server = HTTPServer(server_address, SimpleServer)
    print("Server is running at http://localhost:3000")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    
    server.server_close()