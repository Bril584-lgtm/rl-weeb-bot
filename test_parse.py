import re

SYSTEM_PHRASES = ('left the match', 'joined the match', 'left the party',
                  'joined the party', 'joined the team', 'have joined', 'voice chat')
BLOCKED_NAMES = {'https', 'http', 'www', 'you', 'party', 'system', 'server'}

def parse(line):
    line_lower = line.lower()
    if any(p in line_lower for p in SYSTEM_PHRASES):
        return None
    clean = re.sub(r'^\[\d+[:.]\d+\]\s*', '', line).strip()
    clean = re.sub(r'^\[.*?\]\s*', '', clean).strip()
    if ':' not in clean:
        return None
    name, _, message = clean.partition(':')
    name = name.strip()
    message = message.strip()
    if not name or not message or len(name) > 32 or len(message) > 120:
        return None
    if name.lower() in BLOCKED_NAMES:
        return None
    if not message[0].isalnum():
        return None
    alnum = sum(c.isalnum() or c in '_- ' for c in name)
    if alnum / max(len(name), 1) < 0.6:
        return None
    word_chars = sum(c.isalpha() or c in " '?!.," for c in message)
    if word_chars / max(len(message), 1) < 0.5:
        return None
    return name, message

tests = [
    '[2:34] RRDZ402: whats ur name',
    '[1:43] RRDZ402: whats ur name?',
    '[0:49] YOU: reply',
]
for t in tests:
    print(repr(t), '->', parse(t))
