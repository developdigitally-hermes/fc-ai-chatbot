"""
Bionic Reading formatter for Hermes/OpenClaw.

Partially bolds the first portion of words so the eye anchors faster.
Applied to the final response string before Rich Panel rendering.

Configuration (config.yaml):
    display:
        bionic_reading: false   # master toggle
        bionic_word_min: 4      # minimum word length to bold
        bionic_ratio: 0.3       # fraction of each word to bold (0.0–1.0)

Reference: https://bionic-reading.com/
Scientific status: experimental — no large-scale peer-reviewed validation.
"""

import re

# Patterns that must never be bolded
_EXCLUDE_PATTERNS = [
    re.compile(r"https?://\S+"),          # URLs
    re.compile(r"`[^`\n]+`"),             # inline code
    re.compile(r"```[\s\S]*?```"),        # fenced code blocks
    re.compile(r"\w[\w.+-]*@\w[\w-]*\.[a-z]{2,}", re.I),  # email addresses
]

# Characters stripped from word edges before measuring/bolding
_PUNCT = ".,!?:;\"'()[]{}–—…\n\r\t"

# Regex to find already-bolded spans and skip them entirely
_ALREADY_BOLD = re.compile(r"\*\*[^*]+\*\*|__[^_]+__")


def _should_exclude(word: str) -> bool:
    """Return True if this token should not be bionic-bolded."""
    # Tokens touching backticks are code fragments
    if word.startswith("`") or word.endswith("`"):
        return True
    for pat in _EXCLUDE_PATTERNS:
        if pat.fullmatch(word) or pat.search(word):
            return True
    return False


def _bold_word(word: str, ratio: float) -> str:
    """Bold the first `ratio` fraction of a single word, preserving surrounding punctuation."""
    # Strip leading/trailing punctuation to measure the root
    stripped = word.strip(_PUNCT)
    if not stripped:
        return word

    # Find where the stripped root sits inside the original token
    start = word.index(stripped[0])
    end = start + len(stripped)
    prefix = word[:start]
    suffix = word[end:]

    bold_len = max(1, round(len(stripped) * ratio))
    bolded = f"**{stripped[:bold_len]}**{stripped[bold_len:]}"
    return f"{prefix}{bolded}{suffix}"


def apply_bionic_reading(
    text: str,
    word_min: int = 4,
    ratio: float = 0.3,
) -> str:
    """
    Transform *text* into Bionic Reading format.

    Already-bold spans, URLs, inline code, and email addresses are left untouched.
    Works by splitting the text around protected spans, processing only the plain
    segments, then reassembling.

    Args:
        text:     The response string (may contain Markdown).
        word_min: Minimum character length of root word to bold (default 4).
        ratio:    Fraction of each root word to bold (default 0.3 = 30 %).

    Returns:
        The transformed string with partial bold markers inserted.
    """
    if not text:
        return text

    result = []
    last = 0

    # Walk through all already-bold/protected spans and leave them verbatim
    for m in _ALREADY_BOLD.finditer(text):
        # Process the plain segment before this protected span
        plain = text[last:m.start()]
        if plain:
            result.append(_process_plain(plain, word_min, ratio))
        # Keep the protected span exactly as-is
        result.append(m.group())
        last = m.end()

    # Process any trailing plain segment
    tail = text[last:]
    if tail:
        result.append(_process_plain(tail, word_min, ratio))

    return "".join(result)


def _process_plain(text: str, word_min: int, ratio: float) -> str:
    """Apply bionic bolding to a plain (non-protected) text segment."""
    tokens = re.split(r"(\s+)", text)
    result = []
    for token in tokens:
        if not token or re.fullmatch(r"\s+", token):
            result.append(token)
            continue
        if _should_exclude(token):
            result.append(token)
            continue
        root = token.strip(_PUNCT)
        if len(root) < word_min:
            result.append(token)
            continue
        result.append(_bold_word(token, ratio))
    return "".join(result)
