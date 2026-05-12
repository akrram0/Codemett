import os
import time
import threading
from codemett_ai import ask_ai

# =========================
# STATE
# =========================

watch_running = False


# =========================
# PROJECT SCAN
# =========================

def scan_project():
    base = os.getcwd()
    files = set()

    for root, dirs, fs in os.walk(base):
        for f in fs:
            files.add(os.path.join(root, f))

    return files


# =========================
# WATCH LOOP (CORE ENGINE)
# =========================

def watch_loop():

    global watch_running

    print("\n👀 CODEMETT WATCH ACTIVE\n")

    old = scan_project()
    last = 0

    while watch_running:

        time.sleep(2)

        new = scan_project()

        added = new - old
        removed = old - new

        changes = []

        for f in list(added)[:10]:
            changes.append(f"🆕 {f}")

        for f in list(removed)[:10]:
            changes.append(f"❌ {f}")

        if changes:

            print("\n📡 CHANGES DETECTED:\n")
            print("\n".join(changes))

            # anti spam AI calls
            if time.time() - last > 5:

                prompt = f"""
Analyze these file changes:

{changes}

Find:
- bugs
- risky changes
- missing dependencies
"""

                print("\n🧠 AI:\n")
                print(ask_ai(prompt))

                last = time.time()

        old = new


# =========================
# START WATCH
# =========================

def start_watch():
    global watch_running

    if watch_running:
        print("⚠️ Watch already running")
        return

    watch_running = True

    thread = threading.Thread(target=watch_loop, daemon=True)
    thread.start()

    print("✔ Watch started (background mode)")


# =========================
# STOP WATCH
# =========================

def stop_watch():
    global watch_running

    watch_running = False

    print("🛑 Watch stopped")
