"""Keyboard simulation — paste messages into Rocket League chat via clipboard."""
import time
import pyperclip
from pynput.keyboard import Controller, Key

_ctrl = Controller()


_bot_typing_flag = None  # set by bot.py to the RLWeebBot instance


def send_chat(message: str):
    """Copy message to clipboard, open chat with T, paste, send."""
    pyperclip.copy(message)
    time.sleep(0.1)

    # Flag so the keyboard listener ignores this T press
    if _bot_typing_flag:
        _bot_typing_flag._bot_typing = True

    _ctrl.press('t')
    _ctrl.release('t')
    time.sleep(0.2)

    if _bot_typing_flag:
        _bot_typing_flag._bot_typing = False

    # Paste from clipboard — instant
    with _ctrl.pressed(Key.ctrl):
        _ctrl.press('v')
        _ctrl.release('v')

    time.sleep(0.1)
    _ctrl.press(Key.enter)
    _ctrl.release(Key.enter)
