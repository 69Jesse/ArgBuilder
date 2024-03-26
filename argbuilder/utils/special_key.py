from enum import Enum


__all__ = (
    'SpecialKey',
    'SPECIAL_KEYS_NOTHING_BEFORE',
)


class SpecialKey(Enum):
    up = b'H'
    down = b'P'
    left = b'K'
    right = b'M'
    ctrl_up = b'\x8d'
    ctrl_down = b'\x91'
    ctrl_left = b's'
    ctrl_right = b't'
    delete = b'S'
    ctrl_delete = b'\x93'
    enter = b'\r'
    backspace = b'\x08'
    ctrl_backspace = b'\x7f'
    escape = b'\x1b'
    ctrl_z = b'\x1a'
    ctrl_y = b'\x19'


SPECIAL_KEYS_NOTHING_BEFORE: set[bytes] = {
    b'\r',
    b'\x08',
    b'\x7f',
    b'\x1b',
    b'\x1a',
    b'\x19',
}
