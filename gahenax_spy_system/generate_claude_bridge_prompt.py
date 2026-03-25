"""
generate_claude_bridge_prompt.py
Reads the latest synced Claude.ai session from spy_data/claude_chats/
and formats it as a Gahenax inference prompt for the Core API.
"""
import json
import os
import sys
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "spy_data", "claude_chats")


def load_latest_session(session_id: str | None = None) -> dict:
    if session_id:
        path = os.path.join(DATA_DIR, f"chat_{session_id}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"No session file for id: {session_id}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    files = sorted(glob.glob(os.path.join(DATA_DIR, "chat_*.json")), key=os.path.getmtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No session files found in {DATA_DIR}")
    with open(files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(session: dict) -> str:
    lines = []
    for msg in session.get("messages", []):
        role = msg.get("role", "unknown").upper()
        text = msg.get("text", "").strip()
        if text:
            lines.append(f"[{role}]: {text}")
    conversation = "\n".join(lines)
    prompt = (
        "You are the Gahenax Reasoning Engine.\n"
        "Analyze the following Claude.ai conversation and extract:\n"
        "  1. Core claims or hypotheses\n"
        "  2. Open assumptions\n"
        "  3. Recommended next validation steps\n\n"
        f"--- CONVERSATION ---\n{conversation}\n--- END ---"
    )
    return prompt


def main():
    session_id = sys.argv[1] if len(sys.argv) > 1 else None
    session = load_latest_session(session_id)
    prompt = build_prompt(session)
    print(prompt)
    # Optionally write to file for piping into the Gahenax API
    out_path = os.path.join(BASE_DIR, "generated_prompt.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"\n[SAVED] {out_path}", flush=True)


if __name__ == "__main__":
    main()
