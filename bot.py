"""Main bot loop — ties capture, responder, and typer together."""
import time
import random
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

    def _is_player_chat(self, line: str) -> tuple[bool, str]:
        """
        RL text chat format is 'PlayerName: message'.
        Returns (is_player_chat, message_only).
        Rejects anything that doesn't have a colon separator — kills OCR noise,
        system messages, scoreboard text, etc.
        """
        if ':' not in line:
            return False, ''
        name, _, message = line.partition(':')
        name = name.strip()
        message = message.strip()
        # Name should be 1–32 chars, no newlines, reasonably word-like
        if not name or not message or len(name) > 32:
            return False, ''
        return True, message

    def _is_own_message(self, line: str) -> bool:
        lower = line.lower()
        if config.MY_NAME and config.MY_NAME.lower() in lower.split(':')[0]:
            return True
        _, _, msg = line.partition(':')
        return any(sent in msg.lower().strip() for sent in self._sent)

    def _is_quick_chat(self, message: str) -> bool:
        lower = message.lower()
        return any(qc.lower() in lower for qc in config.QUICK_CHATS)

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
            self._pending = None

        self._pending = threading.Timer(delay, _fire)
        self._pending.start()

    def _handle_lines(self, lines: list[str]):
        self._user_opened_chat.clear()

        for line in lines:
            # Must look like "PlayerName: message" — filters all OCR noise
            is_chat, message = self._is_player_chat(line)
            if not is_chat:
                continue
            if self._is_own_message(line):
                continue
            if self._is_quick_chat(message):
                continue
            if len(message) < 2:
                continue

            reply = self._responder.respond(message)
            if reply and not self._pending:
                print(f"[bot] Detected: '{line}' -> '{reply}'")
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
