from ..utils import SpecialKey
from .base import ParsedArgument

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..builder import Builder


__all__ = (
    'BooleanArgument',
)


class BooleanArgument(ParsedArgument[bool]):
    def after_init(self) -> None:
        self.check_everything_is_valid_type(bool)
        self.string_value = '1' if self.string_value == 'True' else '0' if self.string_value == 'False' else ''
        return super().after_init()

    def raw_get_value(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        if not self.string_value:
            raise ValueError('No value given')
        return bool(int(self.string_value))

    def raw_display(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        try:
            value = self.raw_get_value(builder=builder)
        except Exception:
            return ''
        return 'Yes' if value else 'No'

    def raw_highlighted_range(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> tuple[int, int]:
        return self.entire_value_highlight(builder=builder)

    TRUE_CHARS: set[str] = set('1tTyY')
    FALSE_CHARS: set[str] = set('0fFnN')

    def handle_char(
        self,
        char: str,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if char in self.TRUE_CHARS:
            self.string_value = '1'
            return
        if char in self.FALSE_CHARS:
            self.string_value = '0'
            return

    def handle_special_key(
        self,
        special_key: SpecialKey,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if special_key is SpecialKey.BACKSPACE:
            self.string_value = ''
            if len(self.string_value) == 0 and self.allow_none:
                self.is_none = not self.is_none
            return
        if special_key is SpecialKey.LEFT:
            if len(self.string_value) == 0 and self.allow_none:
                self.is_none = not self.is_none
        if special_key is SpecialKey.LEFT or special_key is SpecialKey.RIGHT:
            self.string_value = '1' if self.string_value != '1' else '0'
            return
        raise ValueError(f'Unsupported special key {special_key}')
