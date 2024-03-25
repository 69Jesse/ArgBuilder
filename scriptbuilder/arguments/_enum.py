from ..utils import SpecialKey
from .base import ParsedArgument

from enum import Enum
from functools import cached_property

from typing import TYPE_CHECKING, Optional, Any
if TYPE_CHECKING:
    from ..builder import Builder


__all__ = (
    'EnumArgument',
)


class EnumArgument(ParsedArgument[Enum]):
    options: list[Enum]
    enum_cls: type[Enum]
    def after_init(self) -> None:
        self.check_everything_is_valid_type(Enum)
        if self.options is None or len(self.options) == 0:
            raise ValueError('No options provided for EnumArgument')
        if len(self.string_value) > 0:
            self.string_value = self.string_value.split('.', 1)[-1]
        self.enum_cls = type(self.options[0])
        return super().after_init()

    def raw_get_value(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> Enum:
        possible_values: list[Optional[Enum]] = [
            None, None, None, None,
        ]
        starting_with_count: int = 0
        for option in self.options:
            if option.name.startswith(self.string_value) or str(option.value).startswith(self.string_value):
                starting_with_count += 1
                if starting_with_count > 1:
                    break
        check_things_other_than_name: bool = starting_with_count <= 1
        lowered: str = self.string_value.lower()
        for option in self.options:
            if option.name == self.string_value and possible_values[0] is None:
                possible_values[0] = option
            if not check_things_other_than_name:
                continue
            if option.name.lower() == lowered and possible_values[2] is None:
                possible_values[2] = option
            option_value: str = str(option.value)
            if option_value == self.string_value and possible_values[1] is None:
                possible_values[1] = option
            if option_value.lower() == lowered and possible_values[3] is None:
                possible_values[3] = option

        try:
            value: Enum = next((value for value in possible_values if value is not None))
            self.string_value = value.name
            builder.inner_index = len(value.name)
            return value
        except StopIteration:
            raise ValueError(f'Invalid value {self.string_value} for {self.name}')

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

    @cached_property
    def type_string(self) -> str:
        return f'{self.enum_cls.__name__.title()}'

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
