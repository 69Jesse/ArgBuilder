from ..utils import SpecialKey
from .base import ParsedArgument

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..builder import Builder


__all__ = (
    'StringArgument',
)


class StringArgument(ParsedArgument[str]):
    def after_init(self) -> None:
        self.check_everything_is_valid_type(str)
        return super().after_init()

    def raw_get_value(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        return self.string_value

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

    def handle_char(
        self,
        char: str,
        *,
        builder: 'Builder[Any]',
    ) -> None:
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
