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

    def _is_own_message(self, line: str) -> bool:
        lower = line.lower()
        if config.MY_NAME and config.MY_NAME.lower() in lower:
            return True
        return any(sent in lower for sent in self._sent)

    def _is_quick_chat(self, line: str) -> bool:
        lower = line.lower()
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
            if self._is_own_message(line):
                continue
            if self._is_quick_chat(line):
                continue
            if len(line.strip()) < 2:
                continue

            reply = self._responder.respond(line)
            if reply and not self._pending:
                print(f"[bot] Detected: '{line}'")
                self._schedule_reply(reply)
                break  # one reply at a time

    # ── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        print("╔══════════════════════════════════╗")
        print("║       RL Weeb Bot  owo           ║")
        print("╚══════════════════════════════════╝")
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
