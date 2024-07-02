from ..arguments import (
    PathArgument,
    ParsedArgument,
)
from .base import Flag

from typing import final, TYPE_CHECKING, Any, Optional
if TYPE_CHECKING:
    from ..builder import Builder


__all__ = (
    'SecretFlag',
    'VerySecretFlag',
)


@final
class SecretFlag(Flag):
    def allowed_parsed_argument_types(self) -> Optional[set[type[ParsedArgument]]]:
        return None

    def maybe_change_display(
        self,
        argument: PathArgument,
        display: str,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        new_display = '*' * len(display)
        if builder.selected_argument() is not argument or builder.inner_index == 0:
            return new_display
        try:
            index = builder.inner_index - 1
            new_display = new_display[:index] + display[index] + new_display[index + 1:]
        except IndexError:
            pass
        return new_display

    def check_maybe_raise(
        self,
        argument: ParsedArgument,
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        return True

    def __str__(self) -> str:
        return 'Password'


@final
class VerySecretFlag(Flag):
    def allowed_parsed_argument_types(self) -> Optional[set[type[ParsedArgument]]]:
        return None

    def maybe_change_display(
        self,
        argument: PathArgument,
        display: str,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        return '*' * len(display)

    def check_maybe_raise(
        self,
        argument: ParsedArgument,
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        return True

    def __str__(self) -> str:
        return 'Password'
