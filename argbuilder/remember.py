from enum import Enum

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from .builder import Builder


class RememberMode(Enum):
    ALL = 0
    CWD = 1
    NONE = 2


def maybe_remember_before(builder: 'Builder[Any]') -> None:
    if builder.remember_mode is RememberMode.NONE:
        return


def maybe_remember_after(builder: 'Builder[Any]') -> None:
    if builder.remember_mode is RememberMode.NONE:
        return
