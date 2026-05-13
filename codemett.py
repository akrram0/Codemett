# codemett.py
from codemett_ui import header
from codemett_engine import (
    set_printer,
    start_watch,
    stop_watch,
    analyze_file,
    rewrite_file,
    analyze_project,
)
from codemett_ai import ask_ai

import threading
import os
import re
import sys

print_lock = threading.Lock()

FILE_PATH_RE = re.compile(
    r'(?<!\S)((?:\./|/)?[A-Za-z0-9_\-./]+\.(?:py|js|jsx|ts|tsx|json|md|html|css|txt|yml|yaml|toml|xml|java|rb|go|php|c|cpp|rs|swift|kt|dart))(?!\S)'
)

SHORT_CHAT = {
    "hi", "hello", "hey", "yo", "sup", "salam", "سلام", "مرحبا", "hola"
}

REWRITE_HINTS = (
    "rewrite", "improve", "refactor", "rewrite this code",
    "improve this code", "rewrite mode", "rewrite it", "make it better"
)

PROJECT_HINTS = (
    "project", "architecture", "analyze", "analyse", "debug", "bug",
    "broken", "slow", "scan", "files", "which files", "what files",
    "root cause", "fix", "review", "why", "issue", "problem"
)


def safe_print(text=""):
    with print_lock:
        print(text)


def safe_input(prompt=""):
    with print_lock:
        return input(prompt)


def extract_file_path(text):
    match = FILE_PATH_RE.search(text)
    return match.group(1) if match else None


def is_short_chat(text):
    return text.strip().lower() in SHORT_CHAT


def looks_like_rewrite_request(text):
    t = text.lower()
    return any(h in t for h in REWRITE_HINTS)


def looks_like_project_request(text):
    t = text.lower()
    return any(h in t for h in PROJECT_HINTS)


def resolve_file_path(file_path, project_root):
    if os.path.isfile(file_path):
        return os.path.abspath(file_path)

    candidate = os.path.join(project_root, file_path)
    if os.path.isfile(candidate):
        return os.path.abspath(candidate)

    return None


def main():
    set_printer(safe_print)

    header()

    project_root = os.getcwd()
    if len(sys.argv) > 1:
        candidate = os.path.abspath(sys.argv[1])
        if os.path.isdir(candidate):
            project_root = candidate
        elif os.path.isfile(candidate):
            project_root = os.path.dirname(candidate) or os.getcwd()

    safe_print(f"\n📦 Project loaded: {project_root}\n")

    while True:
        cmd = safe_input("codemett >>> ").strip()
        if not cmd:
            continue

        if cmd == "/exit":
            break

        if cmd == "/watch":
            safe_print(start_watch(project_root))
            continue

        if cmd == "/stop":
            safe_print(stop_watch())
            continue

        file_path = extract_file_path(cmd)
        resolved_path = resolve_file_path(file_path, project_root) if file_path else None

        if resolved_path:
            if looks_like_rewrite_request(cmd):
                safe_print("\n🤖 AI (rewrite mode):\n")
                safe_print(rewrite_file(resolved_path, cmd))
            else:
                safe_print("\n🤖 AI (file mode):\n")
                safe_print(analyze_file(resolved_path, cmd))
            continue

        if is_short_chat(cmd):
            safe_print("\n🤖 AI:\n")
            safe_print(ask_ai(cmd))
            continue

        if looks_like_project_request(cmd):
            safe_print("\n🤖 AI (project mode):\n")
            safe_print(analyze_project(project_root, cmd))
            continue

        safe_print("\n🤖 AI:\n")
        safe_print(ask_ai(cmd))


if __name__ == "__main__":
    main()
