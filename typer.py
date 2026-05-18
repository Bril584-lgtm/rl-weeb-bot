"""Keyboard simulation — type messages directly into Rocket League chat."""
import time
from pynput.keyboard import Controller, Key

_ctrl = Controller()

_bot_typing_flag = None  # set by bot.py to the RLWeebBot instance


def send_chat(message: str):
    """Open chat with T, type message char by char, send with Enter."""
    if _bot_typing_flag:
        _bot_typing_flag._bot_typing = True

    _ctrl.press('t')
    _ctrl.release('t')
    time.sleep(0.15)

    if _bot_typing_flag:
        _bot_typing_flag._bot_typing = False

    for char in message:
        _ctrl.type(char)

    time.sleep(0.05)
    _ctrl.press(Key.enter)
    _ctrl.release(Key.enter)
