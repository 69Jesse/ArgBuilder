from ..utils import SpecialKey
from .base import ParsedArgument

from pathlib import Path

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..builder import Builder


__all__ = (
    'PathArgument',
)


class PathArgument(ParsedArgument[Path]):
    def after_init(self) -> None:
        self.check_everything_is_valid_type(Path)
        return super().after_init()

    def raw_get_value(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> Path:
        if not self.string_value:
            raise ValueError('Empty path is not allowed')
        return Path(self.string_value)

    def raw_display(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        try:
            return str(self.raw_get_value(builder=builder))
        except Exception:
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
        return self.regular_char_handling(char, builder=builder)

    def handle_special_key(
        self,
        special_key: SpecialKey,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        return self.regular_special_key_handling(special_key, builder=builder)
