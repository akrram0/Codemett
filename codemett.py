from codemett_ui import header
from codemett_engine import start_watch, stop_watch
from codemett_ai import ask_ai
import threading

# 🔒 Lock باش مايتخربقش terminal
print_lock = threading.Lock()


def safe_print(text=""):
    with print_lock:
        print(text)


def safe_input(prompt=""):
    with print_lock:
        return input(prompt)


# UI
header()

# LOOP
while True:

    cmd = safe_input("codemett >>> ").strip()

    if cmd == "/exit":
        break

    elif cmd == "/watch":
        start_watch()

    elif cmd == "/stop":
        stop_watch()

    else:
        safe_print("\n🤖 AI:\n")
        result = ask_ai(cmd)
        safe_print(result)
