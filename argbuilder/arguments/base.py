from ..utils import (
    AllowedTypes,
    SpecialKey,
    colour,
)
from ..command import SetCommand

from abc import (
    ABC,
    abstractmethod,
)
from functools import cached_property

from typing import (
    TYPE_CHECKING,
    Generic,
    Optional,
    TypeVar,
    Any,
)

if TYPE_CHECKING:
    from ..builder import Builder
    from ..flags import Flag


__all__ = (
    'ParsedArgument',
)


Value = TypeVar('Value', bound=AllowedTypes)


class ParsedArgument(ABC, Generic[Value]):
    name: str
    description: str
    field_name: str
    has_default: bool
    default: Optional[Value]
    allow_none: bool
    is_none: bool
    string_value: str
    value_is_default: bool
    options: Optional[list[Value]]
    flags: list['Flag']
    remember: Optional[bool | int]
    prefix: Optional[str]
    suffix: Optional[str]
    def __init__(
        self,
        *,
        name: str,
        description: str,
        field_name: str,
        has_default: bool,
        default: Optional[Value],
        allow_none: bool,
        options: Optional[list[Value]],
        flags: Optional[list['Flag']],
        remember: Optional[bool | int],
        prefix: Optional[str],
        suffix: Optional[str],
    ) -> None:
        self.name = name
        self.description = description
        self.field_name = field_name
        self.has_default = has_default
        self.default = default
        self.allow_none = allow_none
        self.is_none = self.allow_none and self.default is None
        self.string_value = str(self.default if self.default is not None else '')
        self.value_is_default = self.has_default
        self.options = options
        self.flags = flags or []
        self.remember = remember
        self.prefix = prefix
        self.suffix = suffix
        self.after_init()

    def after_init(self) -> None:
        pass

    @property
    def required(self) -> bool:
        return not self.has_default

    def raw_set_string_value_and_is_none(
        self,
        string_value: str,
        is_none: bool,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        """Raises ValueError if the string value is invalid."""
        before_string_value = self.string_value
        before_is_none = self.is_none
        self.string_value = string_value
        self.is_none = is_none
        if not self.value_is_valid(builder=builder):
            self.string_value = before_string_value
            self.is_none = before_is_none
            raise ValueError('Invalid value')

    def check_everything_is_valid_type(
        self,
        cls: type,
        /,
    ) -> None:
        if self.default is not None and not isinstance(self.default, cls):
            raise ValueError(f'Default is not of type {cls}')
        if self.options is not None:
            if len(self.options) == 0:
                raise ValueError('Options cannot be empty')
            if len(self.options) != len(set(self.options)):
                raise ValueError('Options contain duplicates')
            if not all(isinstance(o, cls) for o in self.options):
                raise ValueError(f'Options are not all of type {cls}')

    def value_is_valid(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        try:
            value = self.get_value(builder=builder)
        except Exception:
            return False
        if value is None and self.allow_none:
            return True
        if self.options is not None and value not in self.options:
            return False
        for flag in self.flags:
            if not flag.check(self, builder=builder):
                return False
        return True

    @abstractmethod
    def raw_get_value(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> Value:
        raise NotImplementedError

    def get_value(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> Optional[Value]:
        if self.is_none:
            return None
        return self.raw_get_value(builder=builder)

    @abstractmethod
    def raw_display(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        raise NotImplementedError

    def display(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        if self.is_none:
            return 'None'
        display = self.raw_display(builder=builder)
        for flag in self.flags:
            display = flag.maybe_change_display(self, display, builder=builder)
        display = display.replace('\t', ' ')  # TODO: proper tab handling? seems to be fine for now
        return display

    def one_letter_highlight(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> tuple[int, int]:
        return (builder.inner_index, builder.inner_index + 1)

    def entire_value_highlight(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> tuple[int, int]:
        return (0, len(self.raw_display(builder=builder)))

    @abstractmethod
    def raw_highlighted_range(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> tuple[int, int]:
        raise NotImplementedError

    def highlighted_range(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> tuple[int, int]:
        if self.is_none:
            return (0, 4)
        return self.raw_highlighted_range(builder=builder)

    def formatted_name(
        self,
        *,
        forced_colour: Optional[str] = None,
    ) -> str:
        name = self.name.replace('_', '-')
        if self.required:
            c = forced_colour or '#feae34'
            return colour(f'<{colour(name, hex=c)}>', hex='#f7f7f9')
        c = forced_colour or '#e86a92'
        return colour(f'[{colour(name, hex=c)}]', hex='#f7f7f9')

    @cached_property
    def type_string(self) -> str:
        return self.__class__.__name__.removesuffix('Argument')

    def get_string_value_with_char_inserted(
        self,
        char: str,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        return self.string_value[:builder.inner_index] + char + self.string_value[builder.inner_index:]

    def regular_char_handling(
        self,
        char: str,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        builder.command_manager.do(SetCommand(
            argument=self,
            after_string_value=self.get_string_value_with_char_inserted(char, builder=builder),
            after_is_none=False,
            after_index=builder.index,
            after_inner_index=builder.inner_index + len(char),
        ), builder=builder)

    @abstractmethod
    def handle_char(
        self,
        char: str,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        """Return True if a new command was added, False otherwise."""
        raise NotImplementedError

    def _regular_backspace(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if len(self.string_value) == 0:
            if self.allow_none:
                builder.command_manager.do(SetCommand(
                    argument=self,
                    after_string_value='',
                    after_is_none=not self.is_none,
                    after_index=builder.index,
                    after_inner_index=builder.inner_index,
                ), builder=builder)
            return
        if builder.inner_index == 0:
            return
        builder.command_manager.do(SetCommand(
            argument=self,
            after_string_value=self.string_value[:builder.inner_index - 1] + self.string_value[builder.inner_index:],
            after_is_none=False,
            after_index=builder.index,
            after_inner_index=builder.inner_index - 1,
        ), builder=builder)
        return

    def _regular_ctrl_backspace(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if builder.inner_index == 0:
            return
        builder.command_manager.do(SetCommand(
            argument=self,
            after_string_value=self.string_value[builder.inner_index:],
            after_is_none=False,
            after_index=builder.index,
            after_inner_index=0,
        ), builder=builder)
        return

    def _regular_delete(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if builder.inner_index == len(self.string_value):
            return
        builder.command_manager.do(SetCommand(
            argument=self,
            after_string_value=self.string_value[:builder.inner_index] + self.string_value[builder.inner_index + 1:],
            after_is_none=False,
            after_index=builder.index,
            after_inner_index=builder.inner_index,
        ), builder=builder)
        return

    def _regular_ctrl_delete(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if builder.inner_index == len(self.string_value):
            return
        builder.command_manager.do(SetCommand(
            argument=self,
            after_string_value=self.string_value[:builder.inner_index],
            after_is_none=False,
            after_index=builder.index,
            after_inner_index=builder.inner_index,
        ), builder=builder)
        return

    def _regular_left(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if len(self.string_value) == 0 and self.allow_none:
            builder.command_manager.do(SetCommand(
                argument=self,
                after_string_value='',
                after_is_none=not self.is_none,
                after_index=builder.index,
                after_inner_index=0,
            ), builder=builder)
        if builder.inner_index == 0:
            return
        builder.inner_index = max(0, builder.inner_index - 1)

    def _regular_ctrl_left(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        builder.inner_index = 0

    def _regular_right(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        if builder.inner_index == len(self.string_value):
            return
        builder.inner_index = min(len(self.string_value), builder.inner_index + 1)

    def _regular_ctrl_right(
        self,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        builder.inner_index = len(self.string_value)

    def _regular_special_key(
        self,
        special_key: SpecialKey,
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        if special_key is SpecialKey.BACKSPACE:
            self._regular_backspace(builder=builder)
            return True
        if special_key is SpecialKey.CTRL_BACKSPACE:
            self._regular_ctrl_backspace(builder=builder)
            return True
        if special_key is SpecialKey.DELETE:
            self._regular_delete(builder=builder)
            return True
        if special_key is SpecialKey.CTRL_DELETE:
            self._regular_ctrl_delete(builder=builder)
            return True
        if special_key is SpecialKey.LEFT:
            self._regular_left(builder=builder)
            return True
        if special_key is SpecialKey.CTRL_LEFT:
            self._regular_ctrl_left(builder=builder)
            return True
        if special_key is SpecialKey.RIGHT:
            self._regular_right(builder=builder)
            return True
        if special_key is SpecialKey.CTRL_RIGHT:
            self._regular_ctrl_right(builder=builder)
            return True
        return False

    def regular_special_key_handling(
        self,
        special_key: SpecialKey,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        something_changed = self._regular_special_key(special_key, builder=builder)
        if something_changed and special_key in (
            SpecialKey.LEFT,
            SpecialKey.CTRL_LEFT,
            SpecialKey.RIGHT,
            SpecialKey.CTRL_RIGHT,
        ):
            builder.higher_inner_index = builder.inner_index

    @abstractmethod
    def handle_special_key(
        self,
        special_key: SpecialKey,
        *,
        builder: 'Builder[Any]',
    ) -> None:
        """Return True if a new command was added, False otherwise."""
        raise NotImplementedError
