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

def compute_next_chime(active_hours, last_chimed_hour):
  now = datetime.now()
  current_hour = now.hour
  next_hour = current_hour
  for i in range(1, 25):
    h = (current_hour + i) % 24
    if active_hours[h] and h != last_chimed_hour:
      next_hour = h
      break
  next_chime = now.replace(minute=0, second=0, microsecond=0)
  if next_hour <= current_hour:
    next_chime += timedelta(days=1)
  next_chime = next_chime.replace(hour=next_hour)
  return next_chime

def seconds_until(dt):
  now = datetime.now()
  delta = dt - now
  return max(delta.total_seconds(), 0)

def check_command():
  if not os.path.exists(COMMAND_FILE):
    return None
  try:
    with open(COMMAND_FILE, "r") as f:
      cmd = f.read().strip().lower()
    open(COMMAND_FILE, "w").close()
    return cmd
  except Exception:
    return None

def play_bell(bell_file, volume, count=1, interval=1.5):
  import simpleaudio as sa
  try:
    wave_obj = sa.WaveObject.from_wave_file(bell_file)
    for _ in range(count):
      play_obj = wave_obj.play()
      play_obj.wait_done()
      if _ < count - 1:
        time.sleep(interval)
  except Exception as e:
    print(f"Failed to play bell: {e}")

# ----------- Main Daemon Loop -----------
def main():
  config = load_config()
  state = load_state()
  print("Hourly bell daemon started.")
  
  while True:
    if not config["enabled"]:
      time.sleep(60)
      config = load_config()
      continue

    next_chime = compute_next_chime(config["active_hours"], state.get("last_chimed_hour"))
    sleep_secs = seconds_until(next_chime)
    time.sleep(sleep_secs)

    cmd = check_command()
    if cmd == "shutdown":
      print("Shutdown command received. Exiting.")
      break
    elif cmd == "reload":
      config = load_config()
      continue
    elif cmd == "test":
      play_bell(config.get("bell_sound", BELL_DEFAULT), config["volume"])
      continue

    bell_count = next_chime.hour % 12
    if bell_count == 0:
      bell_count = 12
    play_bell(config.get("bell_sound", BELL_DEFAULT), config["volume"], count=bell_count)
    state["last_chimed_hour"] = next_chime.hour
    state["last_run_timestamp"] = datetime.now().isoformat()
    save_state(state)

if __name__ == "__main__":
  main()
