import string

from base64 import b64decode, b64encode

from .util import str_to_bytes

# Decode base64 input and convert the output to a string (unprintable characters are represented as
# `\x00` etc).
def b64decode_to_str(encoded: str) -> str:
    return str(b64decode(encoded))[2:-1]

# Encode a string using base64.
def b64encode_str(string: str) -> str:
    return b64encode(str_to_bytes(string)).decode("utf8")

# Performs a caesar shift on input text. Leaves non-alphabetic characters alone.
def caesar_shift(text: str, shift: int) -> str:
    output = ""
    for c in text:
        if not c.isalpha():
            output += c
        else:
            alphabet = string.ascii_lowercase if c.islower() else string.ascii_uppercase
            index = (alphabet.index(c) + shift) % 26
            output += alphabet[index]
    return output
