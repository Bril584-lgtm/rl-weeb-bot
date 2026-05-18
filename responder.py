"""Weeb/owo response engine — trigger-based + owoify + optional AI."""
import os
import random
import re

# Trigger keyword → possible replies
TRIGGERS: dict[str, list[str]] = {
    "gg": [
        "gg uwu that was so sugoi!!",
        "gg!! you're so kakkoii senpai (≧◡≦)",
        "ggwp!! this was so much fun nyaa~",
        "gg!! i had so much fun playing with you uwu",
    ],
    "what a save": [
        "gomenasai senpai i tried my bestest uwu",
        "i-it wasn't that great baka!! (>_<)",
        "a-arigato... i got lucky uwu",
        "s-stop it senpai you're making me blush uwu",
    ],
    "nice shot": [
        "a-arigato senpai!! (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
        "nyaa~ thank you!! uwu",
        "h-hontoni?? you're too kind senpai uwu",
        "e-ehh?? i-it was nothing uwu",
    ],
    "easy": [
        "h-hontoni?! that wasn't easy baka!! (눈_눈)",
        "nani?? easy?? you're so mean senpai!! >_<",
        "i-it was NOT easy!! hmph!! (╬ Ò﹏Ó)",
        "iie!! nothing about this is easy!! uwu",
    ],
    "?": [
        "nani?? (눈_눈)",
        "nani ga okita no?? uwu",
        "e-eh?? what happened senpai uwu",
        "???  watashi wa confused desu uwu",
    ],
    "wow": [
        "sugoi desu ne~!! uwu",
        "SUGOI!! (ﾉ◕ヮ◕)ﾉ",
        "waaaa sugoi!! nyaa~",
        "a-are you impressed?? (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
    ],
    "close": [
        "s-so close!! my kokoro couldn't take it uwu",
        "chotto matte that was too close!! (>ω<)",
        "my heart uwu that was so close nyaa",
    ],
    "nice": [
        "arigato gozaimasu senpai!! uwu",
        "nyaa~ thank you so much!! (≧▽≦)",
        "a-arigato!! you're so kind uwu",
    ],
    "lol": [
        "hehehe~ nyaa!! (ﾉ≧∀≦)ﾉ",
        "ahahaha~ uwu same!!",
        "w-wha— that was so funny uwu",
    ],
    "no": [
        "n-nani?! IIE!! (╬ Ò﹏Ó)",
        "nooo~ that can't be!! uwu",
        "iie iie iie!! >_<",
    ],
    "yes": [
        "hai hai!! uwu (≧◡≦)",
        "YES!! sugoi!! nyaa~",
        "hai desu!! uwu",
    ],
    "thanks": [
        "d-dou itashimashite senpai uwu",
        "nyaa~ of course!! (≧▽≦)",
        "a-anytime senpai!! uwu",
    ],
    "sorry": [
        "daijoubu daijoubu!! uwu it's okay nyaa~",
        "ii yo ii yo~ don't worry about it!! (≧◡≦)",
        "mou~ it's okay senpai uwu",
    ],
    "stop": [
        "y-you can't just tell me to stop!! baka!! (>_<)",
        "iie!! i won't stop!! nyaa~",
        "hmph!! (╬ Ò﹏Ó)",
    ],
    "why": [
        "naze...?? uwu that's a very good question senpai",
        "nani?? w-why what?? uwu",
        "b-because!! that's why!! uwu",
    ],
    "noob": [
        "n-nani?! i'm not a noob!! baka!! (눈_눈)",
        "hmph!! i'm actually very kawaii AND skilled!! uwu",
        "t-that's so rude senpai!! (╬ Ò﹏Ó)",
    ],
    "haha": [
        "a-are you laughing at me?? (>_<)",
        "nyahaha~ uwu i'm glad you find it funny!!",
        "hehe~ uwu",
    ],
    "skill": [
        "h-hontoni?! s-sugoi desu!! uwu",
        "i've been training for this moment senpai nyaa~",
        "a-arigato!! i practice every day uwu",
    ],
}

GENERIC_REACTIONS = [
    "uwu",
    "nyaa~",
    "sugoi!!",
    "nani?? (눈_눈)",
    "h-hontoni?? uwu",
    "a-are you perhaps flirting with me senpai?? (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
    "ehhh?? uwu",
    "mou~ (>_<)",
    "w-watashi wa confused desu uwu",
    "owo what's this??",
    "nani the heck senpai uwu",
    "h-hai... uwu",
    "s-senpai noticed me!! nyaa~",
    "uwu uwu uwu",
    "t-this is fine uwu",
]

_OWO_SUBS = [
    (r'\b([rRlL])\b', lambda m: 'w' if m.group().islower() else 'W'),
    (r'(?<=[a-zA-Z])([rRlL])(?=[a-zA-Z])', lambda m: 'w' if m.group().islower() else 'W'),
    (r'\bna\b', 'nya'), (r'\bNa\b', 'Nya'), (r'\bNA\b', 'NYA'),
]

_STUTTER = {'i', 'a', 'e', 'o', 'u', 'its', 'im', "i'm", 'oh'}

_SUFFIXES = [' uwu', ' owo', ' nyaa~', '!! uwu', ' (≧◡≦)', '']


def _owoify(text: str) -> str:
    for pat, rep in _OWO_SUBS:
        text = re.sub(pat, rep, text)

    words = text.split()
    out = []
    for w in words:
        if w.lower() in _STUTTER and random.random() < 0.4:
            out.append(f"{w[0]}-{w}")
        else:
            out.append(w)

    return ' '.join(out) + random.choice(_SUFFIXES)


class WEEBResponder:
    def __init__(self):
        self._use_ai = os.getenv("USE_AI", "false").lower() == "true"
        self._ai = None
        if self._use_ai:
            self._init_ai()

    def _init_ai(self):
        try:
            import anthropic
            self._ai = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            print("[responder] AI mode enabled (Claude Haiku)")
        except Exception as e:
            print(f"[responder] AI init failed: {e} — using rule-based responses")
            self._use_ai = False

    def _ai_respond(self, message: str) -> str | None:
        if not self._ai:
            return None
        try:
            resp = self._ai.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=60,
                system=(
                    "You are an anime weeb bot playing Rocket League. "
                    "Reply to the player's chat message in a cute uwu/owo weeb style. "
                    "Mix Japanese words (uwu, owo, nyaa, senpai, sugoi, nani, hai, "
                    "iie, kawaii, baka, arigato, gomenasai, hontoni) with English. "
                    "Keep replies under 80 characters. Be funny. Never break character. "
                    "Use only ASCII or basic Unicode — no full Japanese script."
                ),
                messages=[{"role": "user", "content": message}],
            )
            return resp.content[0].text.strip()
        except Exception:
            return None

    def respond(self, message: str) -> str | None:
        msg_lower = message.lower().strip()

        # Trigger-based response
        for trigger, replies in TRIGGERS.items():
            if trigger in msg_lower:
                return random.choice(replies)

        # AI response
        if self._use_ai:
            reply = self._ai_respond(message)
            if reply:
                return reply

        # Owoify their message back (50% chance, only if message is long enough)
        if len(message) > 4 and random.random() < 0.5:
            return _owoify(message)

        # Generic reaction
        return random.choice(GENERIC_REACTIONS)
