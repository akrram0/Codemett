# codemett_engine.py
import os
import time
import threading
import shutil

from codemett_ai import ask_ai

watch_running = False
_printer = print

IGNORE_DIRS = {
    "node_modules", "__pycache__", ".git", "dist", "build", ".expo",
    "android", ".gradle", ".idea", "ios", "coverage", ".next", ".turbo"
}

ALLOWED_SPECIAL = {
    "package.json", "tsconfig.json", "jsconfig.json", "README.md",
    "README", "requirements.txt", "pyproject.toml", "Pipfile",
    "Cargo.toml", "go.mod", "go.sum", ".gitignore"
}

ALLOWED_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".html",
    ".css", ".txt", ".yml", ".yaml", ".toml", ".xml", ".java",
    ".rb", ".go", ".php", ".c", ".cpp", ".rs", ".swift", ".kt", ".dart"
}


def set_printer(func):
    global _printer
    _printer = func


def _p(text=""):
    _printer(text)


def scan_project(root):
    files = set()

    for r, d, fs in os.walk(root):
        d[:] = [x for x in d if x not in IGNORE_DIRS]
        for f in fs:
            files.add(os.path.join(r, f))

    return files


def read_text_file(file_path, max_chars=50000):
    with open(file_path, "r", errors="ignore") as f:
        content = f.read()
    if len(content) > max_chars:
        content = content[:max_chars] + "\n... (truncated)"
    return content


def clean_ai_output(text):
    if not text:
        return ""
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            if lines[0].startswith("```") and lines[-1].startswith("```"):
                return "\n".join(lines[1:-1]).strip()

    return text


def backup_file(file_path):
    bak_path = file_path + ".bak"
    shutil.copy2(file_path, bak_path)
    return bak_path


def load_project_context(root, max_files=50, max_chars_per_file=12000):
    context = []
    count = 0

    for r, d, files in os.walk(root):
        d[:] = [x for x in d if x not in IGNORE_DIRS]

        for file in sorted(files):
            if count >= max_files:
                return "\n".join(context)

            ext = os.path.splitext(file)[1].lower()
            if file not in ALLOWED_SPECIAL and ext not in ALLOWED_EXTS:
                continue

            path = os.path.join(r, file)

            try:
                content = read_text_file(path, max_chars=max_chars_per_file)
                rel = os.path.relpath(path, root)
                context.append(f"\n\n### FILE: {rel}\n{content}")
                count += 1
            except Exception:
                continue

    return "\n".join(context)


def build_chat_request(cmd):
    return f"""
MODE: chat
USER_MESSAGE:
{cmd}
""".strip()


def build_file_analysis_request(cmd, file_path, code):
    return f"""
MODE: file_analysis
USER_REQUEST:
{cmd}

FILE_PATH:
{file_path}

FILE_CONTENT:
{code}
""".strip()


def build_file_rewrite_request(cmd, file_path, code):
    return f"""
MODE: rewrite
USER_REQUEST:
{cmd}

FILE_PATH:
{file_path}

FILE_CONTENT:
{code}
""".strip()


def build_project_request(cmd, project_context):
    return f"""
MODE: project_analysis
USER_REQUEST:
{cmd}

PROJECT_CONTEXT:
{project_context}
""".strip()


def analyze_file(file_path, user_request):
    try:
        code = read_text_file(file_path)
    except Exception as e:
        return f"❌ Error reading file: {e}"

    prompt = build_file_analysis_request(user_request, file_path, code)
    return ask_ai(prompt)


def rewrite_file(file_path, user_request):
    try:
        code = read_text_file(file_path)
    except Exception as e:
        return f"❌ Error reading file: {e}"

    prompt = build_file_rewrite_request(user_request, file_path, code)
    result = clean_ai_output(ask_ai(prompt)).strip()

    if not result:
        return "❌ Empty AI result."

    try:
        bak_path = backup_file(file_path)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result)
        return f"✅ Rewritten and saved: {file_path}\n🗂️ Backup saved: {bak_path}"
    except Exception as e:
        return f"❌ Error writing file: {e}"


def analyze_project(project_root, user_request):
    _p("\n📦 Analyzing project...\n")
    project = load_project_context(project_root)
    prompt = build_project_request(user_request, project)
    return ask_ai(prompt)


def watch_loop(project_root, interval=2):
    global watch_running

    _p("\n👀 CODEMETT WATCH ACTIVE\n")

    old = scan_project(project_root)
    last = 0

    while watch_running:
        time.sleep(interval)

        new = scan_project(project_root)
        added = new - old
        removed = old - new

        changes = []

        for f in list(added)[:10]:
            changes.append(f"🆕 {os.path.relpath(f, project_root)}")

        for f in list(removed)[:10]:
            changes.append(f"❌ {os.path.relpath(f, project_root)}")

        if changes:
            _p("\n📡 CHANGES DETECTED:\n")
            _p("\n".join(changes))

            if time.time() - last > 5:
                prompt = f"""
MODE: watch_changes
PROJECT_ROOT: {project_root}

CHANGES:
{changes}

Return:
- root cause
- fix
- files affected
- keep it short
""".strip()
                _p("\n🧠 AI:\n")
                _p(ask_ai(prompt))
                last = time.time()

        old = new


def start_watch(project_root):
    global watch_running

    if watch_running:
        return "⚠️ Watch already running"

    watch_running = True
    thread = threading.Thread(target=watch_loop, args=(project_root,), daemon=True)
    thread.start()
    return "✔ Watch started (background mode)"


def stop_watch():
    global watch_running
    watch_running = False
    return "🛑 Watch stopped"
