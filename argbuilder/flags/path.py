from ..arguments import (
    PathArgument,
    ParsedArgument,
)
from .base import Flag

from typing import final, TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..builder import Builder


__all__ = (
    'ExistsFlag',
    'DoesNotExistFlag',
    'IsDirFlag',
    'IsFileFlag',
)


class PathFlag(Flag):
    value: int | float
    def __init__(
        self,
        value: int | float,
        /,
    ) -> None:
        self.value = value

    def allowed_parsed_argument_types(self) -> set[type[ParsedArgument]]:
        return {PathArgument,}


@final
class ExistsFlag(PathFlag):
    def check_maybe_raise(
        self,
        argument: PathArgument,
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        return argument.raw_get_value(builder=builder).exists()

    def __str__(self) -> str:
        return f'<{self.value}'


@final
class DoesNotExistFlag(PathFlag):
    def check_maybe_raise(
        self,
        argument: PathArgument,
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        return not ExistsFlag.check_maybe_raise(self, argument, builder=builder)  # type: ignore

    def __str__(self) -> str:
        return f'!{self.value}'


@final
class IsDirFlag(PathFlag):
    def check_maybe_raise(
        self,
        argument: PathArgument,
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        return argument.raw_get_value(builder=builder).is_dir()

    def __str__(self) -> str:
        return f'[{self.value}'


@final
class IsFileFlag(PathFlag):
    def check_maybe_raise(
        self,
        argument: PathArgument,
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        return argument.raw_get_value(builder=builder).is_file()

    def __str__(self) -> str:
        return f']{self.value}'
