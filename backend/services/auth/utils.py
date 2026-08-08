"""
Auth Service — Shared security helpers.
"""

import secrets
from random import SystemRandom

# Character classes for generated passwords. Ambiguous characters
# (0/O, 1/l/I) are excluded so the passwords are easy to read aloud.
_UPPER = "ABCDEFGHJKLMNPQRSTUVWXYZ"
_LOWER = "abcdefghijkmnopqrstuvwxyz"
_DIGITS = "23456789"
_SYMBOLS = "!@#$%&*"
_ALPHABET = _UPPER + _LOWER + _DIGITS + _SYMBOLS


def generate_secure_password(length: int = 16) -> str:
    """
    Generate a cryptographically random password with at least one uppercase,
    lowercase, digit, and symbol.

    Used whenever the system must create credentials for a user without an
    explicitly provided password (e.g. school-admin creation, CSV imports).
    The default length of 16 passes Django's ``AUTH_PASSWORD_VALIDATORS``.
    """
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")

    password = [
        secrets.choice(_UPPER),
        secrets.choice(_LOWER),
        secrets.choice(_DIGITS),
        secrets.choice(_SYMBOLS),
    ]
    password.extend(secrets.choice(_ALPHABET) for _ in range(length - 4))
    SystemRandom().shuffle(password)
    return "".join(password)
