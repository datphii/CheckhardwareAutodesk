import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000
# Serve the "out" directory where the reports are generated
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# Make sure directory exists
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # Clean logging
        print(f"[Server] {self.address_string()} - - {format % args}")

def main():
    # Allow overriding port via command line argument
    port = PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    # Find the HTML reports to show them to the user
    reports = [f for f in os.listdir(DIRECTORY) if f.endswith(".html")]

    socketserver.TCPServer.allow_reuse_address = True
    httpd = None
    
    # Attempt to bind to the requested port, or find the next available one
    max_attempts = 10
    current_port = port
    for attempt in range(max_attempts):
        try:
            httpd = socketserver.TCPServer(("", current_port), Handler)
            port = current_port
            break
        except OSError as e:
            if attempt == max_attempts - 1:
                print(f"Error: Could not bind to any port. {e}")
                sys.exit(1)
            print(f"[Warning] Port {current_port} is busy. Trying next port...")
            current_port += 1

    print("=" * 60)
    print("           AUTODESK HARDWARE SCANNER REPORT SERVER")
    print("=" * 60)
    print(f"Serving files from: {DIRECTORY}")
    print(f"Server is running at: http://localhost:{port}")
    
    if reports:
        print("\nAvailable Reports:")
        for r in reports:
            print(f" - http://localhost:{port}/{r}")
    else:
        print("\nNo HTML reports found in the 'out' directory yet.")
        print("Run the scanner first to generate reports!")

    print("\nPress Ctrl+C to stop the server.")
    print("=" * 60)

    # Automatically open the root directory in the default web browser
    webbrowser.open(f"http://localhost:{port}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if httpd:
            httpd.server_close()

if __name__ == "__main__":
    main()
