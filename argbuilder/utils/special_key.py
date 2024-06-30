from enum import Enum


__all__ = (
    'SpecialKey',
    'SPECIAL_KEYS_NOTHING_BEFORE',
)


class SpecialKey(Enum):
    UP = b'H'
    DOWN = b'P'
    LEFT = b'K'
    RIGHT = b'M'
    CTRL_UP = b'\x8d'
    CTRL_DOWN = b'\x91'
    CTRL_LEFT = b's'
    CTRL_RIGHT = b't'
    DELETE = b'S'
    CTRL_DELETE = b'\x93'
    ENTER = b'\r'
    BACKSPACE = b'\x08'
    CTRL_BACKSPACE = b'\x7f'
    ESCAPE = b'\x1b'
    CTRL_Z = b'\x1a'
    CTRL_Y = b'\x19'


SPECIAL_KEYS_NOTHING_BEFORE: set[bytes] = {
    b'\r',
    b'\x08',
    b'\x7f',
    b'\x1b',
    b'\x1a',
    b'\x19',
}
