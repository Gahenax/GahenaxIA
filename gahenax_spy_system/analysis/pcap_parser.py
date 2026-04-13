# Gahenax Spy v9.0 - Wireshark PCAP Parser
# Author: Antigravity AI
# Usage: python pcap_parser.py --file traffic_export.json

import json
import argparse
import os
import time

LOG_FILE = "../utils/aviator_telemetry.jsonl"

def parse_pcap_json(filepath):
    print(f"‍ Procesando captura de red: {filepath}...")
    
    if not os.path.exists(filepath):
        print(f" Error: El archivo {filepath} no existe.")
        return

    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            packets = json.load(f)
        except Exception as e:
            print(f" Error cargando JSON de Wireshark: {e}")
            return

        for packet in packets:
            source = packet.get("_source", {})
            layers = source.get("layers", {})
            
            # Buscamos frames de WebSocket
            ws = layers.get("websocket", {})
            if ws:
                payload = ws.get("websocket.payload.text")
                if payload and ("multiplier" in payload or "round" in payload):
                    # Ingerir en el flujo de Gahenax
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    telemetry_data = {
                        "ts": timestamp,
                        "data": payload,
                        "source": "WIRESHARK_DISSECTION",
                        "frame_number": layers.get("frame", {}).get("frame.number")
                    }
                    
                    with open(LOG_FILE, "a", encoding="utf-8") as out:
                        out.write(json.dumps(telemetry_data) + "\n")
                    count += 1

    print(f" Ingesta Packet-Layer completada: {count} frames extraídos.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gahenax Wireshark Ingester")
    parser.add_argument("--file", type=str, required=True, help="Ruta al archivo JSON exportado de Wireshark")
    args = parser.parse_args()
    
    parse_pcap_json(args.file)
