from ..utils import SpecialKey
from .base import ParsedArgument
from ..command import SetCommand

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

    def raw_set_string_value_and_is_none(
        self,
        string_value: str,
        is_none: bool,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if is_none:
            self.string_value = ''
            self.is_none = True
            return
        try:
            char = string_value[0]
        except IndexError:
            raise ValueError('No value given')
        if char in self.TRUE_CHARS:
            self.string_value = '1'
            self.is_none = False
        elif char in self.FALSE_CHARS:
            self.string_value = '0'
            self.is_none = False
        else:
            raise ValueError('Invalid value')

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
            builder.command_manager.do(SetCommand(
                argument=self,
                after_string_value='1',
                after_is_none=False,
                after_index=builder.index,
                after_inner_index=0,
            ), builder=builder)
        elif char in self.FALSE_CHARS:
            builder.command_manager.do(SetCommand(
                argument=self,
                after_string_value='0',
                after_is_none=False,
                after_index=builder.index,
                after_inner_index=0,
            ), builder=builder)

    def handle_special_key(
        self,
        special_key: SpecialKey,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if special_key is SpecialKey.BACKSPACE:
            if self.is_none or self.string_value != '':
                builder.command_manager.do(SetCommand(
                    argument=self,
                    after_string_value='',
                    after_is_none=False,
                    after_index=builder.index,
                    after_inner_index=0,
                ), builder=builder)
            elif self.string_value == '' and self.allow_none:
                builder.command_manager.do(SetCommand(
                    argument=self,
                    after_string_value='',
                    after_is_none=True,
                    after_index=builder.index,
                    after_inner_index=0,
                ), builder=builder)
            return
        if special_key is SpecialKey.LEFT or special_key is SpecialKey.RIGHT:
            if special_key is SpecialKey.LEFT:
                if self.allow_none:
                    if not self.is_none and self.string_value == '' or self.string_value == '1':
                        after = ('', True)
                    elif self.is_none:
                        after = ('0', False)
                    else:
                        after = ('1', False)
                else:
                    if self.string_value == '0':
                        after = ('1', False)
                    else:
                        after = ('0', False)
            else:
                if self.allow_none:
                    if not self.is_none and self.string_value == '0':
                        after = ('', True)
                    elif not self.is_none and self.string_value == '1':
                        after = ('0', False)
                    else:
                        after = ('1', False)
                else:
                    if self.string_value == '0':
                        after = ('1', False)
                    else:
                        after = ('0', False)
            builder.command_manager.do(SetCommand(
                argument=self,
                after_string_value=after[0],
                after_is_none=after[1],
                after_index=builder.index,
                after_inner_index=0,
            ), builder=builder)
