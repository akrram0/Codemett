#!/usr/bin/env python

import os
import time
import threading
import requests
from colorama import Fore, Style, init

init(autoreset=True)

# =========================
# CONFIG
# =========================

API_KEY = "PUT_YOUR_GROQ_API_KEY"
MODEL = "qwen/qwen3-32b"

IGNORE_DIRS = {
    "node_modules", ".git", ".expo",
    "dist", "build", "__pycache__"
}

SYSTEM_PROMPT = """
You are CodeMett, a senior debugging AI.

Focus:
- React Native / Expo
- JavaScript / Python
- runtime errors
- dependency issues

Return:
- root cause
- fix
- minimal explanation
"""

# =========================
# MEMORY
# =========================

history = []

def save_memory(x):
    history.append(str(x))
    if len(history) > 20:
        history.pop(0)

# =========================
# AI
# =========================

def ask_ai(prompt):
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.4
            },
            timeout=60
        )

        data = r.json()

        if "choices" not in data:
            return f"❌ API ERROR: {data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ AI ERROR: {e}"

# =========================
# PROJECT SCAN
# =========================

def scan_project():
    base = os.getcwd()
    files = set()

    for root, dirs, fs in os.walk(base):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for f in fs:
            files.add(os.path.join(root, f))

    return files

# =========================
# WATCH ENGINE (BACKGROUND)
# =========================

watch_running = False

def watch_loop():
    global watch_running

    print(Fore.CYAN + "\n👀 WATCH MODE ACTIVE")
    print(Fore.YELLOW + f"📁 {os.getcwd()}\n")

    old = scan_project()
    last_ai = 0

    while watch_running:
        time.sleep(2)

        new = scan_project()

        added = new - old
        removed = old - new

        changes = []

        for f in list(added)[:5]:
            changes.append(f"🆕 {f}")

        for f in list(removed)[:5]:
            changes.append(f"❌ {f}")

        if changes:
            print(Fore.YELLOW + "\n".join(changes))

            if time.time() - last_ai > 6:

                prompt = f"""
Project changes:
{changes}

Recent context:
{history[-5:]}

Detect:
- bugs
- risky changes
- missing deps
"""

                print(Fore.GREEN + "\n🧠 WATCH AI:\n")
                print(ask_ai(prompt))

                save_memory(changes)
                last_ai = time.time()

        old = new


def watch_mode():
    global watch_running

    if watch_running:
        print(Fore.RED + "⚠️ already running")
        return

    watch_running = True
    threading.Thread(target=watch_loop, daemon=True).start()

    print(Fore.GREEN + "✔ watch started (background)")

def stop_watch():
    global watch_running
    watch_running = False
    print(Fore.RED + "🛑 watch stopped")

# =========================
# DEBUG MODE
# =========================

def debug_mode():
    print(Fore.CYAN + "\n🐛 DEBUG MODE")

    print(Fore.YELLOW + "Paste error (EOF to finish):")

    lines = []

    while True:
        x = input()
        if x == "EOF":
            break
        lines.append(x)

    error = "\n".join(lines)
    save_memory(error)

    print(Fore.GREEN + "\n🧠 FIXING...\n")

    print(ask_ai(f"""
Fix this error:

{error}

Context:
{history[-10:]}

Return:
- root cause
- fix
- code
"""))

# =========================
# SYSTEM COMMANDS
# =========================

def is_system_command(cmd):
    return cmd.split()[0] in [
        "nano", "ls", "cd", "pwd", "cat",
        "rm", "mkdir", "touch"
    ]

def run_system(cmd):
    try:
        os.system(cmd)
    except Exception as e:
        print("❌ system error:", e)

# =========================
# CHAT MODE
# =========================

def chat(cmd):
    return ask_ai(cmd)

# =========================
# ROUTER (CORE ENGINE)
# =========================

def handle(cmd):

    # EXIT
    if cmd in ["/exit", "exit"]:
        return "EXIT"

    # TOOLS
    if cmd == "/watch":
        watch_mode()
        return

    if cmd == "/stop":
        stop_watch()
        return

    if cmd == "/debug":
        debug_mode()
        return

    # SYSTEM COMMANDS 🔥
    if is_system_command(cmd):
        run_system(cmd)
        return

    # CHAT AI 🤖
    print(Fore.MAGENTA + "\n🤖 AI:\n")
    print(chat(cmd))

# =========================
# HEADER
# =========================

def header():
    print(Fore.CYAN + r"""
  ██████╗ ██████╗ ██████╗ ███████╗███████╗
 ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝
 ██║     ██║   ██║██║  ██║█████╗  █████╗
 ██║     ██║   ██║██║  ██║██╔══╝  ██╔══╝
 ╚██████╗╚██████╔╝██████╔╝███████╗███████╗
  ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝
""")

    print(Fore.GREEN + "⚡ CODEMETT v10 DEV OS ENGINE")
    print(Fore.YELLOW + "Commands: /watch /stop /debug /exit + terminal + AI\n")

# =========================
# MAIN LOOP
# =========================

header()

while True:

    cmd = input(Fore.GREEN + "codemett >>> " + Style.RESET_ALL).strip()

    result = handle(cmd)

    if result == "EXIT":
        break
