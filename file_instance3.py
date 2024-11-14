from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import io
import urllib.parse

class FileHandler(BaseHTTPRequestHandler):
    def _send_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(message).encode())

    def do_GET(self):
        if self.path == '/health':
            self._send_response(200, {"status": "Healthy"})
        else:
            self._send_response(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == '/upload':
            try:
                # Get content length
                content_length = int(self.headers['Content-Length'])
                
                # Get content type and boundary
                content_type = self.headers['Content-Type']
                boundary = content_type.split('=')[1].encode()
                
                # Read the entire POST data
                post_data = self.rfile.read(content_length)
                
                # Parse multipart form data
                parts = post_data.split(boundary)
                
                # Find the file part
                file_data = None
                filename = None
                
                for part in parts:
                    if b'filename=' in part:
                        # Extract filename
                        filename_start = part.find(b'filename="') + 10
                        filename_end = part.find(b'"', filename_start)
                        filename = part[filename_start:filename_end].decode()
                        
                        # Extract file data
                        file_start = part.find(b'\r\n\r\n') + 4
                        file_data = part[file_start:-2]  # Remove trailing \r\n
                        break
                
                if filename and file_data:
                    # Create uploads directory if it doesn't exist
                    if not os.path.exists("uploads"):
                        os.makedirs("uploads")
                    
                    # Write the file
                    filepath = os.path.join("uploads", filename)
                    with open(filepath, 'wb') as f:
                        f.write(file_data)
                    
                    self._send_response(200, {"message": "File uploaded successfully"})
                else:
                    self._send_response(400, {"error": "No file was uploaded"})
                    
            except Exception as e:
                self._send_response(500, {"error": str(e)})
        else:
            self._send_response(404, {"error": "Not found"})

def run_server(port):
    server = HTTPServer(('localhost', port), FileHandler)
    print(f"Server started on port {port}")
    server.serve_forever()

if __name__ == '__main__':
    run_server(8703)
