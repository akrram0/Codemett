# codemett_ui.py
import os
import sys
import time
import threading
import shutil

from colorama import Fore, Style, init

init(autoreset=True)

VERSION = "v3.0"
DEFAULT_STATUS = "Groq Connected"

_SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def _term_width():
    return shutil.get_terminal_size((88, 20)).columns


def print_divider(char="─", width=None, color=Fore.LIGHTBLACK_EX):
    if width is None:
        width = _term_width()
    width = max(40, min(width, 120))
    print(color + char * width + Style.RESET_ALL)


def _center(text, width=None):
    if width is None:
        width = _term_width()
    return text.center(width)


def print_box(text, title=None):
    lines = text.splitlines() or [""]
    width = max(len(line) for line in lines)
    if title:
        width = max(width, len(title) + 2)

    pad = 2
    box_width = min(max(width + pad * 2, 40), 100)

    top = "┌" + "─" * (box_width - 2) + "┐"
    bottom = "└" + "─" * (box_width - 2) + "┘"

    print(Fore.LIGHTBLACK_EX + top)
    if title:
        ttl = f" {title} "
        ttl_line = "│" + ttl.ljust(box_width - 2)[: box_width - 2] + "│"
        print(Fore.CYAN + ttl_line)

    for line in lines:
        content = line[: box_width - 4]
        print("│ " + content.ljust(box_width - 4) + " │")

    print(Fore.LIGHTBLACK_EX + bottom)


def typewriter(text, delay=0.012, color=Fore.CYAN, newline=True):
    for ch in text:
        sys.stdout.write(color + ch + Style.RESET_ALL)
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        sys.stdout.write("\n")
        sys.stdout.flush()


def print_success(text):
    print(Fore.GREEN + f"✅ {text}" + Style.RESET_ALL)


def print_error(text):
    print(Fore.RED + f"❌ {text}" + Style.RESET_ALL)


def print_warning(text):
    print(Fore.YELLOW + f"⚠ {text}" + Style.RESET_ALL)


def print_info(text):
    print(Fore.CYAN + f"ℹ {text}" + Style.RESET_ALL)


def print_ai(text):
    print(Fore.MAGENTA + text + Style.RESET_ALL)


def get_current_folder(cwd=None):
    cwd = cwd or os.getcwd()
    return os.path.basename(os.path.normpath(cwd)) or "~"


def get_prompt(cwd=None):
    folder = get_current_folder(cwd)
    return (
        f"{Fore.LIGHTGREEN_EX}CODEMETT{Style.RESET_ALL} "
        f"{Fore.LIGHTBLACK_EX}[{Fore.CYAN}{folder}{Fore.LIGHTBLACK_EX}]"
        f"{Style.RESET_ALL} >>> "
    )


def print_header(cwd=None, version=VERSION, status=DEFAULT_STATUS):
    clear_screen()
    width = _term_width()
    width = max(60, min(width, 120))

    art = r"""
   ___ ___  ___  ___ __  __ ___ _____ _____
  / __/ _ \|   \| __|  \/  | __|_   _|_   _|
 | (_| (_) | |) | _|| |\/| | _|  | |   | |
  \___\___/|___/|___|_|  |_|___| |_|   |_|

""".rstrip("\n")

    print(Fore.CYAN + art + Style.RESET_ALL)
    print()

    meta = (
        f"{Fore.LIGHTGREEN_EX}CODEMETT{Style.RESET_ALL} "
        f"{Fore.LIGHTBLACK_EX}|{Style.RESET_ALL} "
        f"{Fore.YELLOW}{version}{Style.RESET_ALL} "
        f"{Fore.LIGHTBLACK_EX}|{Style.RESET_ALL} "
        f"{Fore.CYAN}{status}{Style.RESET_ALL}"
    )
    print(_center(meta, width))
    print(_center(Fore.LIGHTBLACK_EX + "•" * 26 + Style.RESET_ALL, width))

    if cwd is None:
        cwd = os.getcwd()
    folder = get_current_folder(cwd)

    print(
        _center(
            f"{Fore.LIGHTBLACK_EX}Project:{Style.RESET_ALL} "
            f"{Fore.CYAN}{folder}{Style.RESET_ALL}",
            width,
        )
    )
    print_divider()


def print_help():
    help_text = (
        f"{Fore.CYAN}Commands{Style.RESET_ALL}\n"
        f"{Fore.LIGHTGREEN_EX}/watch{Style.RESET_ALL}   start watch mode\n"
        f"{Fore.LIGHTGREEN_EX}/stop{Style.RESET_ALL}    stop watch mode\n"
        f"{Fore.LIGHTGREEN_EX}/exit{Style.RESET_ALL}    exit CodeMett\n"
        f"{Fore.LIGHTGREEN_EX}/help{Style.RESET_ALL}    show this help\n\n"
        f"{Fore.CYAN}Usage{Style.RESET_ALL}\n"
        f"- type normal text for chat\n"
        f"- provide a file path to analyze that file\n"
        f"- say improve/rewrite to rewrite a file\n"
        f"- ask about the current project to analyze the project context"
    )
    print_box(help_text, title="HELP")


def progress_bar(current, total, message=""):
    total = max(1, int(total))
    current = max(0, min(int(current), total))
    percent = int((current / total) * 100)
    filled = int((current / total) * 24)
    bar = "█" * filled + "░" * (24 - filled)
    msg = f" {message}" if message else ""
    print(
        f"{Fore.CYAN}[{bar}]{Style.RESET_ALL} "
        f"{Fore.YELLOW}{percent:3d}%{Style.RESET_ALL}{msg}"
    )


def loading_spinner(duration=None, message="Thinking", stop_event=None):
    start = time.time()
    i = 0
    last_len = 0

    if duration is None and stop_event is None:
        duration = 1.2

    while True:
        if stop_event is not None and stop_event.is_set():
            break
        if duration is not None and (time.time() - start) >= duration:
            break

        frame = _SPINNER_FRAMES[i % len(_SPINNER_FRAMES)]
        out = (
            f"{Fore.MAGENTA}{frame}{Style.RESET_ALL} "
            f"{Fore.LIGHTGREEN_EX}{message}{Style.RESET_ALL}"
        )

        pad = max(0, last_len - len(message) - 3)
        sys.stdout.write("\r" + out + (" " * pad))
        sys.stdout.flush()

        last_len = len(out)
        i += 1
        time.sleep(0.08)

    sys.stdout.write("\r" + " " * (last_len + 2) + "\r")
    sys.stdout.flush()


def success_animation(message="Done"):
    sys.stdout.write(Fore.GREEN + "✅ ")
    sys.stdout.flush()
    time.sleep(0.05)
    print(message + Style.RESET_ALL)


def confirm_dialog(message):
    print_box(message, title="CONFIRM")
    choice = input(Fore.YELLOW + "Confirm? (y/n): " + Style.RESET_ALL).strip().lower()
    return choice == "y"
def header():
    print_header()
