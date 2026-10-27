import json
from collections.abc import Iterator
from urllib.parse import urlsplit

MASKED_VALUE = '***'
# Shorter values are not masked: they would hide ordinary text (ports, flags) in every log line.
MIN_SECRET_LENGTH = 8


def _variants(secret: str) -> Iterator[str]:
    yield secret
    yield secret.rstrip('/')

    url = urlsplit(secret)
    if url.scheme and url.netloc:
        # HTTP libraries often log only the path or the query of a URL, and that is where the provider key usually is.
        yield url.path
        yield url.path.rstrip('/')
        yield url.query
        if url.password:
            yield url.password


def secret_values(secrets: dict) -> list[str]:
    """Strings to hide in logs: every secret value and list item, its URL parts and the JSON-escaped forms."""
    values: set[str] = set()

    for value in secrets.values():
        items = value if isinstance(value, list) else [value]
        for item in items:
            if not isinstance(item, str):
                continue
            for variant in _variants(item):
                if len(variant) < MIN_SECRET_LENGTH:
                    continue
                values.add(variant)
                values.add(json.dumps(variant)[1:-1])

    # Longest first, so that a value which contains another one is replaced as a whole.
    return sorted(values, key=len, reverse=True)


class SecretsMasker:
    """Replaces the secret values with MASKED_VALUE in any text, for example in a formatted log line."""

    def __init__(self, secrets: dict):
        self._values = secret_values(secrets)

    def mask(self, text: str) -> str:
        for value in self._values:
            text = text.replace(value, MASKED_VALUE)
        return text
