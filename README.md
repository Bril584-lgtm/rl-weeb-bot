# RL Weeb Bot

External Rocket League chat bot that reads opponent chat via OCR and auto-replies with weeb/owo energy.

Both players see replies as normal text chat. You can still type manually — if you press T yourself, the pending auto-reply is cancelled.

---

## Disclaimer — Read Before Using

**This bot does NOT inject into the Rocket League process, does NOT read game memory, and does NOT modify any game files.** Easy Anti-Cheat (EAC) operates by detecting code injection, memory manipulation, and process hooking — none of which this bot does. EAC is therefore technically unlikely to flag it.

**However — Rocket League's Terms of Use and Code of Conduct explicitly prohibit bots and automation tools in online play.** Psyonix has a zero-tolerance policy on this. They have conducted ban waves specifically targeting bot accounts and have stated that any player found using bots or third-party automation in online matches may receive a permanent ban — regardless of whether EAC detects it or not. Psyonix can detect unusual behavior through gameplay pattern analysis and player reports, independent of EAC.

**Use this bot in private matches with friends only.** Using it in online ranked or casual matchmaking puts your account at risk of a permanent ban under Rocket League's Terms of Use. The author takes no responsibility for any bans or account actions that result from misuse.

**TL;DR:**
- EAC (the technical anti-cheat): unlikely to detect it
- Rocket League ToS: this violates it if used in online play
- Safe use: private matches only

---

## How It Works

```
Opponent types in chat
        |
OCR reads the screen (easyocr)
        |
Weeb reply generated (AI or rule-based)
        |
Bot waits 0.3-0.6s
        |
Presses T, types reply, hits Enter
        |
Both players see normal chat
```

No BakkesMod. No DLL injection. Fully external process.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

### 1. Calibrate the chat region

Run this with Rocket League visible:

```bash
python calibrate.py
```

Drag a box over the chat area in the top-left of the game, press Enter. Paste the output into `config.py`.

### 2. Set your in-game name

Edit `config.py`:
```python
MY_NAME = "YourRLName"
```

### 3. Run

```bash
python bot.py
```

Pick a mode at the prompt and keep the terminal open in the background.

## Modes

| # | Mode | Behaviour |
|---|------|-----------|
| 1 | Goal only | Reply once after a goal is scored (12s window) |
| 2 | All chat | Reply to any text chat from other players |
| 3 | Mention only | Reply only if your name is typed in chat |
| 4 | Silent | Watch only, never type |

## Optional: AI replies (Claude)

For intelligent contextual weeb replies instead of rule-based:

1. Set `USE_AI=true` and add your `ANTHROPIC_API_KEY` in `.env`
2. Run as normal — Claude Haiku generates the responses

## Response Examples

| They type | Bot replies |
|-----------|-------------|
| `gg` | `gg uwu that was so sugoi!!` |
| `what a save` | `gomenasai senpai i tried my bestest uwu` |
| `easy` | `h-hontoni?! that wasn't easy baka!!` |
| `whats ur name` | `s-senpai my name is none of ur business desu uwu` |
| anything else | owoified version or random weeb reaction |

## Files

| File | Purpose |
|------|---------|
| `bot.py` | Main loop + mode selector |
| `capture.py` | Screen capture + OCR (background threaded) |
| `responder.py` | Weeb response engine |
| `typer.py` | Keyboard simulation |
| `config.py` | All settings |
| `calibrate.py` | GUI region picker |

## Notes

- Rocket League must be in **windowed** or **borderless windowed** mode for OCR to work
- Run as **Administrator** on Windows if key simulation does not work
- First run of easyocr downloads a ~100MB model — one time only
- Replies are capped at 120 characters and stripped of non-ASCII for RL chat compatibility
