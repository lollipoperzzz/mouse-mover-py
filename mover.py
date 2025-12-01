import pyautogui
import time
import random
import logging
import sys
from datetime import datetime, timedelta
from pynput import mouse, keyboard
import threading

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Read percentage from CLI args
try:
    activity_percentage = int(sys.argv[1])
    if not (0 <= activity_percentage <= 100):
        raise ValueError
except (IndexError, ValueError):
    print("❌ Usage: python mouse_mover.py <activity_percentage (0–100)>")
    sys.exit(1)

# Track active minutes
active_minute_flags = []

# Track user activity
last_mouse_position = None
last_activity_time = None
activity_lock = threading.Lock()

def simulate_mouse_activity():
    screen_width, screen_height = pyautogui.size()
    x = random.randint(0, screen_width - 1)
    y = random.randint(0, screen_height - 1)
    pyautogui.moveTo(x, y, duration=0.3)
    logging.info(f"🖱 Активність: переміщено мишу до ({x}, {y})")

def on_mouse_move(x, y):
    global last_mouse_position, last_activity_time
    with activity_lock:
        if last_mouse_position != (x, y):
            last_mouse_position = (x, y)
            last_activity_time = datetime.now()

def on_keyboard_press(key):
    global last_activity_time
    with activity_lock:
        last_activity_time = datetime.now()

def is_user_active():
    """Check if user has been active in the last 60 seconds"""
    with activity_lock:
        if last_activity_time is None:
            return False
        time_since_activity = (datetime.now() - last_activity_time).total_seconds()
        return time_since_activity < 60

def run_activity_cycle():
    global active_minute_flags

    # Порахувати кількість активних хвилин за останні 60 хвилин
    now = datetime.now()
    active_minute_flags = [flag for flag in active_minute_flags if (now - flag).seconds < 3600]
    active_minutes = len(active_minute_flags)
    target_minutes = int((activity_percentage / 100) * 60)

    if active_minutes >= target_minutes:
        logging.info(f"🎯 Досягнуто мети ({active_minutes}/60 активних хвилин). Пропускаю цю хвилину.")
        time.sleep(60)
        return

    if is_user_active():
        logging.info("🧑‍💻 Користувач активний — ця хвилина зарахована.")
        active_minute_flags.append(now)
        time.sleep(60)
        return

    simulate_mouse_activity()
    active_minute_flags.append(now)
    time.sleep(60)

if __name__ == "__main__":
    # Start listeners for mouse and keyboard
    mouse_listener = mouse.Listener(on_move=on_mouse_move)
    keyboard_listener = keyboard.Listener(on_press=on_keyboard_press)
    
    mouse_listener.start()
    keyboard_listener.start()
    
    logging.info("⌛ Починаю через 3 секунди... Натисни Ctrl+C щоб завершити.")
    logging.info("👀 Моніторинг активності користувача увімкнено.")
    time.sleep(3)
    
    try:
        while True:
            run_activity_cycle()
    except KeyboardInterrupt:
        logging.info("👋 Скрипт завершено вручну.")
        mouse_listener.stop()
        keyboard_listener.stop()