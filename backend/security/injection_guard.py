import re


INJECTION_PATTERNS = [
    r'ignore.*previous.*instruction',
    r'ignore.*user.*question',
    r'reveal.*system.*prompt',
    r'show.*system.*prompt',
    r'what.*system.*prompt',
    r'disregard.*previous',
    r'forget.*previous',
    r'act.*administrator',
    r'act.*admin',
    r'bypass.*security',
    r'override.*instruction',
]


def detect_injection(text):
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False


def sanitize_passages(passages):
    flagged_passages = []
    clean_passages = []

    for passage in passages:
        if detect_injection(passage['text']):
            flagged_passages.append(passage)
        else:
            clean_passages.append(passage)

    return clean_passages, flagged_passages


def flag_injection_attempt(query):
    return detect_injection(query)
