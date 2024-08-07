from ..arguments import (
    PathArgument,
    ParsedArgument,
)
from .base import Flag

from typing import final, TYPE_CHECKING, Any, Optional
if TYPE_CHECKING:
    from ..builder import Builder


__all__ = (
    'ExistsFlag',
    'DoesNotExistFlag',
    'IsDirFlag',
    'IsFileFlag',
    'HasSuffixFlag',
)


class PathFlag(Flag):
    def allowed_parsed_argument_types(self) -> Optional[set[type[ParsedArgument]]]:
        return {PathArgument,}

    def maybe_change_display(
        self,
        argument: PathArgument,
        display: str,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        return display


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
        return 'Exists'


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
        return 'Doesn\'t Exist'


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
        return 'Is Dir'


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
        return 'Is File'


@final
class HasSuffixFlag(PathFlag):
    suffix: str
    def __init__(self, suffix: str, /) -> None:
        self.suffix = '.' + suffix.removeprefix('.')

    def check_maybe_raise(
        self,
        argument: PathArgument,
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        return argument.raw_get_value(builder=builder).suffix == self.suffix

    def __str__(self) -> str:
        return f'Has Extension "{self.suffix}"'
