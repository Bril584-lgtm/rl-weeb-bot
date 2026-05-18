"""Main bot loop — ties capture, responder, and typer together."""
import time
import random
import re
import threading
from dotenv import load_dotenv
from pynput import keyboard as kb

import config
from capture import ChatCapture
from responder import WEEBResponder
from typer import send_chat

load_dotenv()

MODES = {
    "1": ("goal",    "Goal only     — reply once after a goal is scored (12s window)"),
    "2": ("all",     "All chat      — reply to any text chat from other players"),
    "3": ("mention", "Mention only  — reply only if your name is typed in chat"),
    "4": ("off",     "Silent        — watch only, never type"),
}


def pick_mode() -> str:
    print("==================================")
    print("       RL Weeb Bot  owo")
    print("==================================")
    print("\nSelect a mode:\n")
    for key, (_, desc) in MODES.items():
        print(f"  [{key}] {desc}")
    print()
    while True:
        choice = input("Mode (1-4): ").strip()
        if choice in MODES:
            mode, desc = MODES[choice]
            print(f"\n>> {desc}\n")
            return mode
        print("    Pick 1, 2, 3 or 4.")


class RLWeebBot:
    def __init__(self, mode: str):
        self._mode = mode
        self._capture = ChatCapture(config.CHAT_REGION)
        self._responder = WEEBResponder()
        self._sent: set[str] = set()
        self._pending: threading.Timer | None = None
        self._user_opened_chat = threading.Event()
        self._last_reply_at: float = 0
        self._cooldown: float = 8.0
        self._goal_at: float = 0
        self._goal_window: float = 12.0

    # ── Keyboard listener ────────────────────────────────────────────────────

    def _on_press(self, key):
        try:
            ch = key.char
        except AttributeError:
            return
        if ch in ('t', 'T'):
            self._user_opened_chat.set()
            if self._pending:
                self._pending.cancel()
                self._pending = None
                print("[bot] User opened chat — auto-reply cancelled")

    # ── Parsing & filters ────────────────────────────────────────────────────

    # Names that are never real players
    _BLOCKED_NAMES = {'https', 'http', 'www', 'you', 'party', 'system', 'server'}
    # System message keywords — lines containing these are not player chat
    _SYSTEM_PHRASES = ('left the match', 'joined the match', 'left the party',
                       'joined the party', 'joined the team', 'have joined', 'voice chat')

    def _parse_chat(self, line: str) -> tuple[str, str] | None:
        # Reject system notification lines
        line_lower = line.lower()
        if any(p in line_lower for p in self._SYSTEM_PHRASES):
            return None

        clean = re.sub(r'^\[\d+[:.]\d+\]\s*', '', line).strip()
        # Strip [PARTY] or [TEAM] prefixes
        clean = re.sub(r'^\[.*?\]\s*', '', clean).strip()

        if ':' not in clean:
            return None
        name, _, message = clean.partition(':')
        name = name.strip()
        message = message.strip()

        if not name or not message or len(name) > 32 or len(message) > 120:
            return None

        # Reject known non-player names
        if name.lower() in self._BLOCKED_NAMES:
            return None

        # Message must start with a letter or digit
        if not message[0].isalnum():
            return None

        # Name must be mostly alphanumeric
        alnum = sum(c.isalnum() or c in '_- ' for c in name)
        if alnum / max(len(name), 1) < 0.6:
            return None

        # Message must be at least 50% real word characters
        word_chars = sum(c.isalpha() or c in " '?!.," for c in message)
        if word_chars / max(len(message), 1) < 0.5:
            return None

        return name, message

    def _is_own(self, name: str, message: str) -> bool:
        name_clean = re.sub(r'[^a-z]', '', name.lower())
        if name_clean in ('you', 'yov', 'vou', 'yo', 'ycu'):
            return True
        if config.MY_NAME and config.MY_NAME.lower() in name.lower():
            return True
        return any(sent in message.lower() for sent in self._sent)

    def _is_quick_chat(self, message: str) -> bool:
        return any(qc.lower() in message.lower() for qc in config.QUICK_CHATS)

    def _mentions_me(self, message: str) -> bool:
        if not config.MY_NAME:
            return False
        return config.MY_NAME.lower() in message.lower()

    # ── Mode checks ──────────────────────────────────────────────────────────

    def _check_goal(self, lines: list[str]):
        for line in lines:
            if re.search(r'\bgoal\b', line, re.IGNORECASE):
                self._goal_at = time.time()
                print("[bot] Goal detected — 12s reply window open")
                break

    def _allowed(self, name: str, message: str) -> bool:
        if self._mode == "off":
            return False
        if self._mode == "goal":
            return time.time() - self._goal_at < self._goal_window
        if self._mode == "mention":
            return self._mentions_me(message)
        return True  # "all" mode

    # ── Reply scheduling ─────────────────────────────────────────────────────

    def _schedule_reply(self, reply: str):
        delay = random.uniform(config.RESPONSE_DELAY_MIN, config.RESPONSE_DELAY_MAX)
        self._user_opened_chat.clear()

        def _fire():
            if self._user_opened_chat.is_set():
                print("[bot] Reply suppressed — user typed manually")
                return
            print(f"[bot] Sending -> {reply}")
            send_chat(reply)
            self._sent.add(reply.lower().strip())
            self._last_reply_at = time.time()
            self._pending = None

        self._pending = threading.Timer(delay, _fire)
        self._pending.start()

    def _handle_lines(self, lines: list[str]):
        self._user_opened_chat.clear()

        for line in lines:
            parsed = self._parse_chat(line)
            if not parsed:
                continue
            name, message = parsed

            if self._is_own(name, message):
                continue
            if self._is_quick_chat(message):
                continue
            if len(message) < 2:
                continue
            if not self._allowed(name, message):
                continue
            if time.time() - self._last_reply_at < self._cooldown:
                continue

            reply = self._responder.respond(message)
            if reply and not self._pending:
                print(f"[bot] {name}: '{message}'")
                self._schedule_reply(reply)
                break

    # ── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        print(f"Mode   : {MODES[[k for k,v in MODES.items() if v[0]==self._mode][0]][1]}")
        print(f"Region : {config.CHAT_REGION}")
        print("Press Ctrl+C to stop.\n")

        listener = kb.Listener(on_press=self._on_press)
        listener.start()

        try:
            while True:
                new_lines = self._capture.get_new_lines()
                if new_lines:
                    self._check_goal(new_lines)
                    self._handle_lines(new_lines)
                time.sleep(config.SCAN_INTERVAL)
        except KeyboardInterrupt:
            print("\n[bot] Stopped. uwu")
        finally:
            listener.stop()
            if self._pending:
                self._pending.cancel()


if __name__ == "__main__":
    mode = pick_mode()
    RLWeebBot(mode).run()
