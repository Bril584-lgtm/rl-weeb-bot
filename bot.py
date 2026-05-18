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


class RLWeebBot:
    def __init__(self):
        self._capture = ChatCapture(config.CHAT_REGION)
        self._responder = WEEBResponder()
        self._sent: set[str] = set()          # messages we've sent — skip these
        self._pending: threading.Timer | None = None
        self._user_opened_chat = threading.Event()
        self._last_reply_at: float = 0        # timestamp of last sent reply
        self._cooldown: float = 8.0           # seconds of silence after each reply
        self._goal_at: float = 0              # timestamp of last detected goal
        self._goal_window: float = 12.0       # seconds after a goal to allow replies

    # ── Keyboard listener ────────────────────────────────────────────────────

    def _on_press(self, key):
        try:
            ch = key.char
        except AttributeError:
            return
        if ch in ('t', 'T'):
            # User opened chat manually — cancel any pending auto-reply
            self._user_opened_chat.set()
            if self._pending:
                self._pending.cancel()
                self._pending = None
                print("[bot] User opened chat — auto-reply cancelled")

    # ── Core logic ───────────────────────────────────────────────────────────

    def _parse_chat(self, line: str) -> tuple[str, str] | None:
        """
        Parse RL chat lines. Handles both:
          'PlayerName: message'
          '[3:36] PlayerName: message'  (with timestamp)
        Returns (name, message) or None if not a chat line.
        """
        import re
        # Strip leading timestamp like [3:36] or [3.36]
        clean = re.sub(r'^\[\d+[:.]\d+\]\s*', '', line).strip()
        if ':' not in clean:
            return None
        name, _, message = clean.partition(':')
        name = name.strip()
        message = message.strip()
        if not name or not message or len(name) > 32 or len(message) > 120:
            return None
        # Name must be mostly alphanumeric (real player names) — reject OCR garbage
        alnum = sum(c.isalnum() or c in '_- ' for c in name)
        if alnum / max(len(name), 1) < 0.6:
            return None
        # Message must have at least 40% real word characters — reject garbled OCR
        word_chars = sum(c.isalpha() or c in " '?!.,'" for c in message)
        if word_chars / max(len(message), 1) < 0.4:
            return None
        return name, message

    def _is_own_message(self, name: str, message: str) -> bool:
        # RL shows your own messages as "YOU" — OCR may garble it slightly
        name_clean = re.sub(r'[^a-z]', '', name.lower())
        if name_clean in ('you', 'yov', 'vou', 'yo', 'ycu'):
            return True
        if config.MY_NAME and config.MY_NAME.lower() in name.lower():
            return True
        return any(sent in message.lower() for sent in self._sent)

    def _is_quick_chat(self, message: str) -> bool:
        return any(qc.lower() in message.lower() for qc in config.QUICK_CHATS)

    def _schedule_reply(self, reply: str):
        delay = random.uniform(config.RESPONSE_DELAY_MIN, config.RESPONSE_DELAY_MAX)
        self._user_opened_chat.clear()

        def _fire():
            if self._user_opened_chat.is_set():
                print("[bot] Reply suppressed — user typed manually")
                return
            print(f"[bot] Sending → {reply}")
            send_chat(reply)
            self._sent.add(reply.lower().strip())
            self._last_reply_at = time.time()
            self._pending = None

        self._pending = threading.Timer(delay, _fire)
        self._pending.start()

    def _check_goal(self, lines: list[str]):
        for line in lines:
            if re.search(r'\bgoal\b', line, re.IGNORECASE):
                self._goal_at = time.time()
                print("[bot] Goal detected — reply window open")
                break

    def _in_goal_window(self) -> bool:
        return time.time() - self._goal_at < self._goal_window

    def _handle_lines(self, lines: list[str]):
        self._user_opened_chat.clear()

        for line in lines:
            parsed = self._parse_chat(line)
            if not parsed:
                continue
            name, message = parsed

            if self._is_own_message(name, message):
                continue
            if self._is_quick_chat(message):
                continue
            if len(message) < 2:
                continue

            # Only reply during goal celebration window
            if not self._in_goal_window():
                continue

            # Cooldown — stay silent after each reply
            if time.time() - self._last_reply_at < self._cooldown:
                continue

            reply = self._responder.respond(message)
            if reply and not self._pending:
                print(f"[bot] {name}: '{message}' -> '{reply}'")
                self._schedule_reply(reply)
                break  # one reply at a time

    # ── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        print("==================================")
        print("       RL Weeb Bot  owo")
        print("==================================")
        print(f"Region : {config.CHAT_REGION}")
        print(f"Delay  : {config.RESPONSE_DELAY_MIN}–{config.RESPONSE_DELAY_MAX}s")
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
    RLWeebBot().run()
