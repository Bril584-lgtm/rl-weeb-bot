"""Keyboard simulation — types messages into Rocket League chat."""
import time
import random
from pynput.keyboard import Controller, Key

_ctrl = Controller()


def send_chat(message: str, wpm: int = 75):
    """Press T to open chat, type message, press Enter."""
    # Open chat
    _ctrl.press('t')
    _ctrl.release('t')
    time.sleep(0.2)

    # Type each character at human-like speed
    char_delay = 60 / (wpm * 5)
    for char in message:
        _ctrl.type(char)
        jitter = random.uniform(0, char_delay * 0.6)
        time.sleep(char_delay + jitter)

    time.sleep(0.12)
    _ctrl.press(Key.enter)
    _ctrl.release(Key.enter)
