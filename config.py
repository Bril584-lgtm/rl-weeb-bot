"""All settings for rl-weeb-bot. Edit these to match your setup."""

# Chat box region on screen — run calibrate.py to get exact coords for your resolution
CHAT_REGION = {'top': 15, 'left': 5, 'width': 420, 'height': 160, 'mon': 2}

# Seconds to wait before auto-replying (feels more human)
RESPONSE_DELAY_MIN = 1.5
RESPONSE_DELAY_MAX = 3.5

# Seconds between OCR scans
SCAN_INTERVAL = 0.5

# Your Rocket League in-game name (helps ignore your own messages in chat)
MY_NAME = "Bril"

# Quick chats to ignore — bot won't respond to these
QUICK_CHATS = [
    "What a save!", "Nice shot!", "Great pass!", "Thanks!", "What a save",
    "OMG", "Noooo!", "Wow", "Close one!", "No problem.", "Whoops...",
    "My bad...", "Calculated.", "Savage!", "Okay.", "Incoming!",
    "Centering!", "All yours.", "Take the shot!", "Need boost!",
    "To the air!", "Defending...", "On your left", "On your right",
    "I got it!", "Bumping!",
]

# Set to True and add ANTHROPIC_API_KEY to .env for AI-powered replies
USE_AI = True
