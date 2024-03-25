from ..flags import (
    GreaterThanFlag,
    GreaterThanOrEqualFlag,
    LessThanFlag,
    LessThanOrEqualFlag,
)

from typing import final


__all__ = (
    'Flag',
)


@final
class Flag:
    __slots__ = ()

    def __new__(cls) -> None:
        raise TypeError('Do not instantiate this class, use "Flag.xyz()" instead.')

    LessThan = LessThanFlag
    LessThanOrEqual = LessThanOrEqualFlag
    GreaterThan = GreaterThanFlag
    GreaterThanOrEqual = GreaterThanOrEqualFlag
