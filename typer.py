"""Keyboard simulation — paste messages into Rocket League chat via clipboard."""
import time
import pyperclip
from pynput.keyboard import Controller, Key

_ctrl = Controller()


def send_chat(message: str):
    """Copy message to clipboard, open chat with T, paste, send."""
    pyperclip.copy(message)
    time.sleep(0.1)

    # Open chat
    _ctrl.press('t')
    _ctrl.release('t')
    time.sleep(0.2)

    # Paste from clipboard — instant
    with _ctrl.pressed(Key.ctrl):
        _ctrl.press('v')
        _ctrl.release('v')

    time.sleep(0.1)
    _ctrl.press(Key.enter)
    _ctrl.release(Key.enter)
