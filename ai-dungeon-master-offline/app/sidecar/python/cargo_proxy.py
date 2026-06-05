import http.server
import socketserver
import urllib.request
import json
import urllib.parse
from http import HTTPStatus

PORT = 8080

class CargoProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Intercept registry queries
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        # Route logic
        if path == "/index/config.json":
            self.forward_config()
        elif path.startswith("/index/"):
            # Fetch crate metadata from index.crates.io
            remote_path = path.replace("/index/", "/")
            self.forward_request(f"https://index.crates.io{remote_path}")
        elif path.startswith("/dl/"):
            # Fetch crate downloads from static.crates.io and stream them back over HTTP
            remote_path = path.replace("/dl/", "/")
            self.forward_request(f"https://static.crates.io/crates{remote_path}")
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def forward_config(self):
        try:
            req = urllib.request.Request("https://index.crates.io/config.json", headers={"User-Agent": "cargo-proxy"})
            with urllib.request.urlopen(req) as response:
                config_data = json.loads(response.read().decode("utf-8"))
                
                # Rewrite download API to route through our proxy
                config_data["dl"] = f"http://127.0.0.1:{PORT}/dl/{{crate}}/{{version}}/download"
                
                response_bytes = json.dumps(config_data).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_bytes)))
                self.end_headers()
                self.wfile.write(response_bytes)
        except Exception as e:
            self.send_error(HTTPStatus.BAD_GATEWAY, f"Proxy error: {e}")

    def forward_request(self, target_url):
        try:
            req = urllib.request.Request(target_url, headers={"User-Agent": "cargo-proxy"})
            with urllib.request.urlopen(req) as response:
                content = response.read()
                self.send_response(HTTPStatus.OK)
                # Propagate headers
                for header, val in response.headers.items():
                    if header.lower() not in ("content-encoding", "transfer-encoding"):
                        self.send_header(header, val)
                self.end_headers()
                self.wfile.write(content)
        except Exception as e:
            self.send_error(HTTPStatus.BAD_GATEWAY, f"Proxy error: {e}")

def run():
    # Allow address reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), CargoProxyHandler) as httpd:
        print(f"[CargoProxy] Running local HTTP proxy on http://127.0.0.1:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
