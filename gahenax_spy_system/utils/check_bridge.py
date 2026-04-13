import os
import time

def check_pipe(pipe_name):
    try:
        # On Windows, we can use os.path.exists for named pipes
        if os.path.exists(pipe_name):
            return True
        return False
    except:
        return False

if __name__ == "__main__":
    pipe = r"\\.\pipe\CE_MCP_Bridge_v99"
    if check_pipe(pipe):
        print(f"✅ Bridge Pipe Found: {pipe}")
    else:
        print(f"❌ Bridge Pipe Not Found: {pipe}")
        print("Tip: Run the 'ce_mcp_bridge.lua' script in Cheat Engine first.")
