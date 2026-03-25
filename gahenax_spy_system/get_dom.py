import urllib.request
import json
import websocket
import sys

def get_dom():
    try:
        req = urllib.request.Request('http://127.0.0.1:9222/json')
        with urllib.request.urlopen(req) as response:
            tabs = json.loads(response.read().decode('utf-8'))
        
        mines_tab = None
        for tab in tabs:
            if 'mines' in tab.get('url', '').lower() and tab.get('type') == 'page':
                mines_tab = tab
                break
                
        if not mines_tab:
            print("No Mines tab found.")
            return

        ws_url = mines_tab['webSocketDebuggerUrl']
        
        # Connect without sending an Origin header, or faking it
        ws = websocket.create_connection(ws_url, suppress_origin=True)
        
        # Request DOM
        command = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": "document.documentElement.outerHTML",
                "returnByValue": True
            }
        }
        ws.send(json.dumps(command))
        result = json.loads(ws.recv())
        
        if 'result' in result and 'result' in result['result']:
            html = result['result']['result']['value']
            with open('mines_dom.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("DOM successfully saved to mines_dom.html")
        else:
            print("Failed to evaluate: ", result)
            
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_dom()
