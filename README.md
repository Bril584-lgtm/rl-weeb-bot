# RL Weeb Bot 🌸

External Rocket League chat bot that reads opponent chat via OCR and auto-replies with weeb/owo energy. No DLL injection, no anti-cheat issues.

Both players see replies as normal text chat. You can still type manually — if you press T yourself, the pending auto-reply is cancelled.

## How It Works

```
Opponent types in chat
        ↓
OCR reads the screen (easyocr)
        ↓
Trigger matching → weeb reply generated
        ↓
Bot waits 1.5–3.5s (feels human)
        ↓
Presses T → types reply → hits Enter
        ↓
Both players see normal chat
```

No BakkesMod. No DLL injection. Easy Anti-Cheat can't touch it.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

### 1. Calibrate the chat region

Run this with Rocket League visible (or a screenshot of it):

```bash
python calibrate.py
```

Drag a box over the chat area in the bottom-left, press Enter. Paste the output into `config.py`.

### 2. Set your in-game name (optional but recommended)

Edit `config.py`:
```python
MY_NAME = "YourRLName"
```

This prevents the bot from responding to its own messages.

### 3. Run

```bash
python bot.py
```

Keep the terminal open. The bot runs while RL is in the foreground.

## Optional: AI replies (Claude)

For dynamic AI-powered responses instead of rule-based:

1. Set `USE_AI=true` and add your `ANTHROPIC_API_KEY` in `.env`
2. Run as normal — Claude Haiku generates contextual weeb replies

## Response Examples

| They type | Bot replies |
|-----------|-------------|
| `gg` | `gg uwu that was so sugoi!!` |
| `what a save` | `gomenasai senpai i tried my bestest uwu` |
| `easy` | `h-hontoni?! that wasn't easy baka!! (눈_눈)` |
| `?` | `nani?? (눈_눈)` |
| `nice shot` | `a-arigato senpai!! (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)` |
| anything else | owoified version of their message + random reaction |

## Manual override

Press **T** yourself before the bot fires → auto-reply is cancelled, you type normally.

## Files

| File | Purpose |
|------|---------|
| `bot.py` | Main loop |
| `capture.py` | Screen capture + OCR |
| `responder.py` | Weeb response engine |
| `typer.py` | Keyboard simulation |
| `config.py` | All settings |
| `calibrate.py` | GUI region picker |

## Notes

- Rocket League must be in **windowed** or **borderless windowed** mode for OCR to work
- Run as **Administrator** on Windows if key simulation doesn't work
- First run of easyocr downloads a ~100MB model — one time only
