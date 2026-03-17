"""Custom tokenization helpers."""

import re
from typing import List


def simple_tokenize(text: str) -> List[str]:
    """Simple whitespace + punctuation tokenizer for fallback use."""
    tokens = re.findall(r"\b\w+\b|[^\w\s]", text)
    return tokens


def count_tokens(text: str) -> int:
    """Estimate token count using simple whitespace splitting."""
    return len(text.split())


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to approximately max_tokens."""
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text
    return " ".join(tokens[:max_tokens])
