# ---------------- Imports ---------------
import os
import json
import time
from datetime import datetime, timedelta

# -------------- File Paths --------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "../config/config.json")
STATE_FILE = os.path.join(BASE_DIR, "../config/state.json")
COMMAND_FILE = os.path.join(BASE_DIR, "../config/command.txt")
BELL_DEFAULT = os.path.join(BASE_DIR, "../assets/bell.wav")

# ----------- Helper Functions -----------
def load_config():
  default_config = {
    "enabled": True,
    "volume": 30,
    "active_hours": [
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 12AM to 11AM
      1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0   # 12PM to 11PM
    ],                                     # Default 12PM to 10PM
    "bell_sound": BELL_DEFAULT
  }
  try:
    with open(CONFIG_FILE, "r") as f:
      cfg = json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
    cfg = default_config
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
      json.dump(cfg, f, indent=2)
  cfg["volume"] = max(0, min(100, int(cfg.get("volume", 30))))
  if not isinstance(cfg.get("active_hours"), list) or len(cfg["active_hours"]) != 24:
    cfg["active_hours"] = default_config["active_hours"]
  return cfg

def load_state():
  default_state = {
    "last_chimed_hour": None,
    "last_run_timestamp": None
  }
  try:
    with open(STATE_FILE, "r") as f:
      state = json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
    state = default_state
  return state

def save_state(state):
  os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
  with open(STATE_FILE, "w") as f:
    json.dump(state, f, indent=2)
