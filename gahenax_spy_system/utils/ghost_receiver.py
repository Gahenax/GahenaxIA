# Gahenax Spy System v3.2 - Ghost Protocol (Telemetry Receiver)
# Author: Antigravity AI
# Use with ghost_hook.js

import os
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import sys
import os

# Añadir el path base para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

PORT = config.TELEMETRY_PORT
LOG_FILE = config.TELEMETRY_LOG

def anonymize_ip(ip: str, mask_v4: int = 12, mask_v6: int = 84) -> str:
    """Anonip-style IP masking logic."""
    if ":" in ip: # IPv6
        parts: list[str] = ip.split(":")
        return ":".join(parts[:4]) + "::" # type: ignore
    else: # IPv4
        parts: list[str] = ip.split(".")
        return ".".join(parts[:3]) + ".0" # type: ignore

class TelemetryHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        # Fallback for when POST/Fetch is blocked (Tracking Pixel style)
        query = parse_qs(urlparse(self.path).query)
        msg_list = query.get("msg", [""])
        msg = msg_list[0]
        
        if msg:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            data = {"ts": timestamp, "data": msg, "source": "GET_PING"}
            
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
            
            print(f"📡 {timestamp} | PING RECIBIDO: {msg[:80]}...") # type: ignore

        self.send_response(200)
        self.send_header('Content-type', 'image/gif')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        client_ip = self.client_address[0]
        anon_ip = anonymize_ip(client_ip)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            data["source_ip_anon"] = anon_ip
            
            # Etiquetado para telemetría agéntica
            msg = data.get("msg", "")
            if "[MCP_AGENT]" in msg:
                 data["source_type"] = "MCP_AGENTIC"
            
            with open(config.TELEMETRY_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": timestamp, "data": data}) + "\n")
            
            msg = data.get("msg", "")
            if "[CAPTURE]" in msg:
                 print(f"📡 {timestamp} | RECIBIDO: {msg[:100]}...")

            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        except Exception as e:
            print(f"❌ Error decoding: {e}")
            self.send_response(500)
            self.end_headers()

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, TelemetryHandler)
    print(f"🦾 Gahenax Ghost Receiver v3.2 | PUERTO: {PORT}")
    print(f"Esperando inyecciones (POST/GET) en: http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Receptor detenido.")

if __name__ == "__main__":
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as _: pass
    run_server()
