"""SeedHelper-compatible codes, separate from internal signed 64-bit seeds."""
import re

MASK64 = (1 << 64) - 1
ALPHABET = "0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ"


def signed64(value: int) -> int:
    value &= MASK64
    return value if value < (1 << 63) else value - (1 << 64)


def encode_seed(seed: int) -> str:
    """Match SeedHelper.getString, including the empty representation of zero."""
    value = seed & MASK64
    result = ""
    while value:
        value, digit = divmod(value, 35)
        result = ALPHABET[digit] + result
    return result


def sterilize_seed(code: str) -> str:
    """Match Java trim/uppercase/filter; invalid text becomes empty."""
    code = code.strip("".join(chr(i) for i in range(33))).upper()
    return code.replace("O", "0") if re.fullmatch(r"[A-Z0-9]*", code) else ""


def decode_seed(code: str) -> int:
    """Raw SeedHelper.getLong semantics, including invalid-character -1 digits.

    Configuration must use parse_seed_code instead of this low-level API.
    """
    value = 0
    for character in code.upper().replace("O", "0"):
        value = signed64(value * 35 + ALPHABET.find(character))
    return value


def valid_seed_character(character: str) -> str | None:
    character = character.upper().replace("O", "0")
    return character if character in ALPHABET else None


def parse_seed_code(code: str) -> int | None:
    """Validate user input; an empty input means automatic, not internal zero."""
    if not isinstance(code, str):
        raise ValueError("seed_code must be a quoted string")
    normalized = sterilize_seed(code)
    if not normalized and code.strip("".join(chr(i) for i in range(33))):
        raise ValueError("Invalid seed code: use letters A-Z and digits 0-9")
    return decode_seed(normalized) if normalized else None
