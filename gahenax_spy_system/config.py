# Gahenax Spy System v10.0 - Central Configuration
# Author: Antigravity AI

import os

# Base Directory (Absolute)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Network Ports
TELEMETRY_PORT = 8080
DASHBOARD_PORT = 5000

# File Paths (Absolute)
UTILS_DIR = os.path.join(BASE_DIR, "utils")
ANALYSIS_DIR = os.path.join(BASE_DIR, "analysis")
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
AGENTS_DIR = os.path.join(BASE_DIR, "agents")

TELEMETRY_LOG = os.path.join(UTILS_DIR, "aviator_telemetry.jsonl")
TRAINING_DATA = os.path.join(UTILS_DIR, "aviator_training_data.jsonl")
BURNED_IPS_LOG = os.path.join(UTILS_DIR, "burned_ips.jsonl")

# Persistence Dirs
PLAYWRIGHT_SESSION = os.path.join(BASE_DIR, "gahenax_user_session")
SELENIUM_SESSION = os.path.join(BASE_DIR, "gahenax_user_session_selenium")

# Aviator Target Config
CASINO_BASE_URL = "https://gamelauncher-uu-pop-co.wplay.co/launcher?real=1&popSkipPasParam=true&ptuserId=X0WvqAN/Fm9GrxWeJ5ul11FAE4BA%3D%3D&username=1DR336572302&casino=wplayco&clienttype=casino&backurl=https://www.wplay.co/casino&country=CO&clientplatform=web&language=ES&token=s-FVVD7E64mDgO_WDDr3Lu7v0rui5F_uPY6MNKh3v3tXJ_DQXqhR21Er8EGQOzV07LvwpGF_AUwY-i4LO40LgUcA&currency=COP&popcp_fullscreen=false&cashierurl=https://www.wplay.co/game/payment/deposit&game=pop_5767cf5c_spr"
AVIATOR_GAME_ID = "5767cf5c_spr" # WPlay Game ID for Aviator

# Mersenne Twister (MT19937) Cryptanalysis Parameters
MT_TEMPERING_B = 0x9d2c5680
MT_TEMPERING_C = 0xefc60000
MT_STATE_SIZE = 624 # Words required for full state recovery

# Hooks
GHOST_HOOK = os.path.join(UTILS_DIR, "ghost_hook.js")

print(f"Gahenax Config v10.0 Loaded from: {BASE_DIR}")
