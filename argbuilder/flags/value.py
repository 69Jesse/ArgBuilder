from ..arguments import (
    FloatArgument,
    IntegerArgument,
    ParsedArgument,
    StringArgument,
)
from .base import Flag

from abc import (
    abstractmethod,
)

from typing import final, TYPE_CHECKING, Any, Optional
if TYPE_CHECKING:
    from ..builder import Builder


__all__ = (
    'LessThanFlag',
    'LessThanOrEqualFlag',
    'GreaterThanFlag',
    'GreaterThanOrEqualFlag',
)


class ValueFlag(Flag):
    value: int | float
    def __init__(
        self,
        value: int | float,
        /,
    ) -> None:
        self.value = value

    def allowed_parsed_argument_types(self) -> Optional[set[type[ParsedArgument]]]:
        return {StringArgument, IntegerArgument, FloatArgument}

    @abstractmethod
    def apply(
        self,
        value: int | float,
        /,
    ) -> bool:
        raise NotImplementedError

    def check_maybe_raise(
        self,
        argument: ParsedArgument,
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        if isinstance(argument, StringArgument):
            return self.apply(len(argument.raw_get_value(builder=builder)))
        if isinstance(argument, (
            IntegerArgument,
            FloatArgument,
        )):
            return self.apply(argument.raw_get_value(builder=builder))
        raise TypeError(f'Invalid type {argument.__class__.__name__}')

    def maybe_change_display(
        self,
        argument: ParsedArgument,
        display: str,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        return display


@final
class LessThanFlag(ValueFlag):
    def apply(
        self,
        value: int | float,
        /,
    ) -> bool:
        return value < self.value

    def __str__(self) -> str:
        return f'<{self.value}'


@final
class LessThanOrEqualFlag(ValueFlag):
    def apply(
        self,
        value: int | float,
        /,
    ) -> bool:
        return value <= self.value

    def __str__(self) -> str:
        return f'<={self.value}'


@final
class GreaterThanFlag(ValueFlag):
    def apply(
        self,
        value: int | float,
        /,
    ) -> bool:
        return value > self.value

    def __str__(self) -> str:
        return f'>{self.value}'


@final
class GreaterThanOrEqualFlag(ValueFlag):
    def apply(
        self,
        value: int | float,
        /,
    ) -> bool:
        return value >= self.value

    def __str__(self) -> str:
        return f'>={self.value}'
