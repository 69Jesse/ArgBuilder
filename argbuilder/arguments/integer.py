from ..utils import SpecialKey
from .base import ParsedArgument

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..builder import Builder


__all__ = (
    'IntegerArgument',
)


class IntegerArgument(ParsedArgument[int]):
    def after_init(self) -> None:
        self.check_everything_is_valid_type(int)
        return super().after_init()

    def raw_get_value(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> int:
        value = float(self.string_value)
        if value.is_integer():
            return int(value)
        raise ValueError(f'Value {value} is not an integer')

    def raw_display(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        return self.string_value

    def raw_highlighted_range(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> tuple[int, int]:
        return self.one_letter_highlight(builder=builder)

    ALLOWED_CHARS: set[str] = set('0123456789-_eE')

    def handle_char(
        self,
        char: str,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if char not in self.ALLOWED_CHARS:
            return
        self.add_to_string_value(char, builder=builder)

    def handle_special_key(
        self,
        special_key: SpecialKey,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if self.regular_special_key_handling(special_key, builder=builder):
            return
        raise ValueError(f'Unsupported special key {special_key}')
