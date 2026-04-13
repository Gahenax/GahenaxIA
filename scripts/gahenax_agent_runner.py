import os
import subprocess
import json
import requests
import sys

# GAHENAX: Agentic Bridge for Ollama (Mistral v0.3)
# Allows local model to execute safe/critical commands with human-in-the-loop logic.

OLLAMA_API = "http://localhost:11434/api/chat"
MODEL_NAME = "gahenax-antigravity"

# Tool Definitions (Mistral v0.3 JSON Format)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List contents of a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the directory."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite content to a file. (CRITICAL)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file."},
                    "content": {"type": "string", "description": "The content to write."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command. (CRITICAL)",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command string to execute."}
                },
                "required": ["command"]
            }
        }
    }
]

def execute_tool(name, args):
    """Executes a tool locally with safe/critical permission logic."""
    if name == "read_file":
        try:
            with open(args["path"], "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
            
    elif name == "list_dir":
        try:
            return str(os.listdir(args["path"]))
        except Exception as e:
            return f"Error listing directory: {str(e)}"
            
    elif name == "write_file":
        print(f"\n[CRITICAL ACTION] Write to {args['path']}?")
        confirm = input("Confirm write? (y/N): ").lower()
        if confirm == 'y':
            try:
                os.makedirs(os.path.dirname(args["path"]), exist_ok=True)
                with open(args["path"], "w", encoding="utf-8") as f:
                    f.write(args["content"])
                return "File written successfully."
            except Exception as e:
                return f"Error writing file: {str(e)}"
        else:
            return "User rejected write_file."
            
    elif name == "run_command":
        print(f"\n[CRITICAL ACTION] Run command: {args['command']}")
        confirm = input("Confirm execution? (y/N): ").lower()
        if confirm == 'y':
            try:
                result = subprocess.run(args["command"], shell=True, capture_output=True, text=True)
                return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
            except Exception as e:
                return f"Error executing command: {str(e)}"
        else:
            return "User rejected run_command."
            
    return f"Unknown tool: {name}"

def agent_loop(user_input):
    messages = [{"role": "user", "content": user_input}]
    
    while True:
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "tools": TOOLS,
            "stream": False
        }
        
        response = requests.post(OLLAMA_API, json=payload).json()
        msg = response["message"]
        messages.append(msg)
        
        if "tool_calls" in msg:
            for tool_call in msg["tool_calls"]:
                name = tool_call["function"]["name"]
                args = tool_call["function"]["arguments"]
                print(f"[*] Tool Call: {name}({args})")
                
                result = execute_tool(name, args)
                messages.append({
                    "role": "tool",
                    "name": name,
                    "content": result
                })
        else:
            print(f"\n[Antigravity]: {msg['content']}")
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        agent_loop(" ".join(sys.argv[1:]))
    else:
        print("Usage: python gahenax_agent_runner.py \"prompt here\"")
