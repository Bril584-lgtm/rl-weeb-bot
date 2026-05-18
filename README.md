# RL Weeb Bot 🌸

An external Rocket League chat bot that reads opponent chat via OCR and auto-replies with weeb/owo energy — no game injection, no anti-cheat issues.

## Idea

When someone types in RL chat, the bot catches it and fires back a weeb-style response automatically. Both players see it as normal text chat. You can still manually type whenever you want — the bot only jumps in if you don't.

## How It Works

```
Opponent types in chat
        ↓
OCR reads the screen (Tesseract / easyocr)
        ↓
Text sent to AI or rule-based weeb responder
        ↓
Bot presses T → types reply → hits Enter
        ↓
Both players see it as normal chat
```

No DLL injection. No BakkesMod. Fully external — Easy Anti-Cheat can't touch it.

## Planned Features

- Screen capture + OCR to detect new chat messages
- AI-powered replies with a weeb/owo personality prompt
- Fallback rule-based responses (owo, uwu, nya, nani, sugoi, etc.)
- Manual override — you type first within X seconds, bot stays silent
- Configurable personality (tsundere, yandere, wholesome uwu, etc.)
- Cooldown so it doesn't spam

## Response Style Examples

| They say | Bot replies |
|----------|-------------|
| "gg" | "gg uwu that was so sugoi 🌸" |
| "what a save" | "gomenasai senpai i tried my bestest uwu" |
| "easy" | "h-hontoni?! that wasn't easy baka 😤" |
| "?" | "nani?? (눈_눈)" |

## Tech Stack (planned)

- Python
- `mss` — fast screen capture
- `easyocr` or `pytesseract` — read chat text
- `pyautogui` or `pynput` — simulate keypresses
- OpenAI / Claude API — generate replies (optional)
- `opencv-python` — isolate the chat region on screen

## Requirements

- Python 3.10+
- Rocket League running in windowed or borderless windowed mode
- (Optional) AI API key for dynamic replies

## Status

Idea / early planning stage.
