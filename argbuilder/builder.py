from .arguments import (
    BooleanArgument,
    EnumArgument,
    FloatArgument,
    IntegerArgument,
    ParsedArgument,
    PathArgument,
    StringArgument,
)
from .unparsed import UnparsedArgument
from .utils import (
    AllowedTypes,
    SPECIAL_KEYS_NOTHING_BEFORE,
    SpecialKey,
    colour,
    random_rgb_neon_colour,
)
from .remember import RememberMode, maybe_remember_before, maybe_remember_after, clear_memory
from .command import CommandManager

from enum import Enum
from functools import cached_property
import msvcrt
import os
from pathlib import Path
import re
import sys

from typing import (
    Any,
    NamedTuple,
    Optional,
    TypeVar,
    Generic,
)


__all__ = (
    'Builder',
    'increment_arg_parsers_defined',
)


# https://stackoverflow.com/a/14693789/22837110
ANSI_ESCAPE = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)


NT = TypeVar('NT', bound=NamedTuple)


def should_clear_memory() -> bool:
    if len(sys.argv) > 1 and sys.argv[1] == '!clear':
        sys.argv.pop(1)
        return True
    return False


ARG_PARSERS_DEFINED: int = 0

def increment_arg_parsers_defined() -> None:
    global ARG_PARSERS_DEFINED
    ARG_PARSERS_DEFINED += 1

def should_use_argv() -> bool:
    return ARG_PARSERS_DEFINED <= 1 and len(sys.argv) > 1


class Builder(Generic[NT]):
    named_tuple_cls: type[NT]
    name: str
    description: str
    author: str
    arguments: list[ParsedArgument[Any]]
    remember_data: tuple[RememberMode, int]  # (mode, duration)  # duration in seconds, -1 for infinite
    started: bool
    finished: bool
    index: int
    inner_index: int
    higher_inner_index: int
    last_text_line_count: int
    command_manager: CommandManager
    previous_input: Optional[str | SpecialKey]
    def __init__(
        self,
        *,
        named_tuple_cls: type[NT],
        name: str,
        description: str,
        author: str,
        arguments: list[ParsedArgument],
        remember_data: tuple[RememberMode, int],
    ) -> None:
        self.named_tuple_cls = named_tuple_cls
        self.name = name
        self.description = description
        self.author = author
        self.arguments = arguments
        self.remember_data = remember_data
        self.started = False
        self.finished = False
        self.index = 0
        self.higher_inner_index = 0
        self.last_text_line_count = -1
        self.command_manager = CommandManager()
        self.previous_input = None
        if should_clear_memory():
            clear_memory(self)
        else:
            maybe_remember_before(self)
        if should_use_argv():
            self.use_argv()
        self.inner_index = self.highest_inner_index_from_current_selected()
        self.higher_inner_index = self.inner_index

    @staticmethod
    def from_named_tuple_cls(
        named_tuple_cls: type[NT],
        *,
        name: str,
        description: str,
        author: str,
        remember_mode: tuple[RememberMode, int],
    ) -> 'Builder[NT]':
        for key, value in vars(named_tuple_cls).items():
            if isinstance(value, UnparsedArgument):
                raise ValueError(f'"{key}" must have a type annotation. Example:\n\t{key}: int = arg(...)')

        arguments: list[ParsedArgument] = []

        for index, field_name in enumerate(named_tuple_cls._fields):
            try:
                unparsed: Any = named_tuple_cls._field_defaults.get(field_name, None)
                if unparsed is None:
                    unparsed = UnparsedArgument()
                elif not isinstance(unparsed, UnparsedArgument):
                    unparsed = UnparsedArgument(default=unparsed)
                unparsed.check_everything(
                    named_tuple_cls=named_tuple_cls,
                    index=index,
                    parsed_arguments=arguments,
                )

                parsed_argument_cls: type[ParsedArgument]
                if unparsed._type is bool:
                    parsed_argument_cls = BooleanArgument
                elif unparsed._type is str:
                    parsed_argument_cls = StringArgument
                elif unparsed._type is int:
                    parsed_argument_cls = IntegerArgument
                elif unparsed._type is float:
                    parsed_argument_cls = FloatArgument
                elif issubclass(unparsed._type, Enum):  # type: ignore
                    parsed_argument_cls = EnumArgument
                elif unparsed._type is Path:
                    parsed_argument_cls = PathArgument
                else:
                    raise ValueError(f'Unsupported type {unparsed._type}')

                unparsed.check_everything_with_parsed_cls(
                    named_tuple_cls=named_tuple_cls,
                    index=index,
                    parsed_arguments=arguments,
                    parsed_cls=parsed_argument_cls,  # type: ignore
                )
                if (
                    unparsed.name is None
                    or unparsed.description is None
                    or unparsed.allow_none is None
                ):
                    raise ValueError('Something went wrong on our end.. Please report this.')

                argument: ParsedArgument[AllowedTypes] = parsed_argument_cls(  # type: ignore
                    name=unparsed.name,
                    description=unparsed.description,
                    field_name=field_name,
                    has_default=unparsed.has_default,
                    default=unparsed.default,  # type: ignore
                    allow_none=unparsed.allow_none,
                    options=unparsed.options,  # type: ignore
                    flags=unparsed.flags,
                    remember=unparsed.remember,
                )
                arguments.append(argument)
            except ValueError as exc:
                raise ValueError(f'Error while parsing "{field_name}"') from exc

        return Builder(
            named_tuple_cls=named_tuple_cls,
            name=name,
            description=description,
            author=author,
            arguments=arguments,
            remember_data=remember_mode,
        )

    def get_terminal_width(self) -> int:
        return os.get_terminal_size()[0]

    @cached_property
    def biggest_argument_length(self) -> int:
        return max(len(a.name) for a in self.arguments)

    @cached_property
    def biggest_argument_type_length(self) -> int:
        return max(len(a.type_string) for a in self.arguments)

    def title(self) -> str:
        author: str = colour(self.author, rgb=random_rgb_neon_colour())
        name: str = colour(f'{colour(f' {self.name} ', hex='#f7f7f9', background_hex='#0095e9', bold=True)}', hex='#0095e9', bold=True)
        description: str = colour(self.description, hex='#f7f7f9')
        return '  '.join(
            (author, name, description),
        )

    def create_line(
        self,
        argument: ParsedArgument,
        *,
        index: int,
        width: int,
    ) -> str:
        selected: bool = index == self.index
        is_valid: bool = argument.value_is_valid(builder=self)
        displayed: str = argument.display(builder=self)
        if selected:
            left, right = argument.highlighted_range(builder=self)
            right = max(right, left + 1)
            displayed += ' ' * (right - len(displayed))
            displayed = displayed[:left] + colour(displayed[left:right], hex='#000000', background_hex='#ffffff') + displayed[right:]

        prefix: str = colour(('\u276f' if selected else ' '), hex='#0095e9')
        type_string: str = colour(argument.type_string, hex='#545454') + ' ' * (self.biggest_argument_type_length - len(argument.type_string))
        name: str = argument.formatted_name(forced_colour='#0095e9' if selected else None) + ' ' * (self.biggest_argument_length - len(argument.name))
        ok: str = colour(f'[{colour('OK', hex=('#00ff00' if is_valid else '#f7f7f9'), background_hex=(None if is_valid else '#ff0000'))}]', hex='#f7f7f9')
        displayed = colour(displayed, hex='#f7f7f9')

        line: str = f' {prefix} {type_string} {name} {ok} {displayed}'
        escaped: str = self.ansi_escape(line)
        description_diff: int = width - ((len(escaped) - 1) % width) - 1
        if description_diff > 0:
            description_suffix: str = colour(
                ' ' * max(0, description_diff - len(argument.description)) + argument.description[-max(0, description_diff):],
                hex='#545454',
            )
            line += description_suffix
        return line

    def selected_argument(self) -> ParsedArgument:
        return self.arguments[self.index]

    def ansi_escape(
        self,
        text: str,
    ) -> str:
        return ANSI_ESCAPE.sub('', text)

    def display(self) -> None:
        width: int = self.get_terminal_width()
        text: str = '\n' + '\n'.join((
            self.title(),
            *(
                self.create_line(argument, index=i, width=width)
                for i, argument in enumerate(self.arguments)
            )
        )) + '\n\n'

        text_line_count: int = 0
        new_text: str = ''
        for i, line in enumerate(text.split('\n')):
            escaped: str = self.ansi_escape(line)
            text_line_count += (max(0, (len(escaped) - 1) // width)) + 1
            if line:
                line += ' ' * (width - ((len(escaped) - 1) % width) - 1)
            else:
                line = ' ' * width
            new_text += ('\n' * (i != 0)) + line
        text_line_count -= 1

        line_count_diff: int = self.last_text_line_count - text_line_count
        printing: str = ('\033[F' * self.last_text_line_count) + new_text
        self.last_text_line_count = text_line_count
        if line_count_diff > 0:
            printing += ' ' * (width * line_count_diff) + ('\033[F' * line_count_diff)
        print(
            printing,
            end='',
            flush=True,
        )

    def handle_byte(
        self,
        byte: bytes,
    ) -> None:
        try:
            self.previous_input = byte.decode('cp437')
        except UnicodeDecodeError:
            return
        self.selected_argument().handle_char(self.previous_input, builder=self)

    def highest_inner_index_from_current_selected(self) -> int:
        return len(self.arguments[self.index].display(builder=self))

    def handle_special_key(self, special_key: SpecialKey) -> None:
        self.previous_input = special_key
        if special_key is SpecialKey.UP:
            self.index = (self.index - 1) % len(self.arguments)
            self.inner_index = self.higher_inner_index
        elif special_key is SpecialKey.DOWN:
            self.index = (self.index + 1) % len(self.arguments)
            self.inner_index = self.higher_inner_index
        elif special_key is SpecialKey.CTRL_UP:
            self.index = 0
            self.inner_index = self.higher_inner_index
        elif special_key is SpecialKey.CTRL_DOWN:
            self.index = len(self.arguments) - 1
            self.inner_index = self.higher_inner_index
        elif special_key is SpecialKey.ENTER:
            self.maybe_finish()
        elif special_key is SpecialKey.CTRL_Z:
            self.command_manager.undo(builder=self)
        elif special_key is SpecialKey.CTRL_Y:
            self.command_manager.redo(builder=self)
        else:
            self.selected_argument().handle_special_key(special_key, builder=self)
        self.inner_index = min(self.inner_index, self.highest_inner_index_from_current_selected())

    def fetch_input_bytes(self) -> bytes:
        return msvcrt.getch()

    def iterate(self) -> None:
        self.display()
        byte = self.fetch_input_bytes()
        if byte == b'\x03':
            raise KeyboardInterrupt

        if byte == b'\xe0':
            byte = msvcrt.getch()
            self.handle_special_key(SpecialKey(byte))
        elif byte in SPECIAL_KEYS_NOTHING_BEFORE:
            self.handle_special_key(SpecialKey(byte))
        else:
            self.handle_byte(byte)

    def set_or_throw_if_exists(self, mapping: dict[Any, Any], key: Any, value: Any) -> None:
        if key in mapping:
            raise ValueError(f'Key "{key}" used more than once')
        mapping[key] = value

    def fetch_argv_values(self) -> dict[ParsedArgument[Any], str]:
        keyword_values: dict[str, Optional[str]] = {}
        positional_values: list[str] = []
        latest_keyword: Optional[str] = None
        for arg in sys.argv[1:]:
            if arg.startswith('--'):
                if latest_keyword is not None:
                    self.set_or_throw_if_exists(keyword_values, latest_keyword, None)
                latest_keyword = arg[2:].replace('-', '_')
                continue
            if latest_keyword is not None:
                self.set_or_throw_if_exists(keyword_values, latest_keyword, arg)
                latest_keyword = None
                continue
            latest_keyword = None
            positional_values.append(arg)
        if latest_keyword is not None:
            self.set_or_throw_if_exists(keyword_values, latest_keyword, None)

        mapping: dict[ParsedArgument[Any], str] = {}
        for key, value in keyword_values.items():
            value = value if value is not None else '1'
            argument = next((a for a in self.arguments if a.name == key), None)
            if argument is None:
                raise ValueError(f'Invalid argument "{key}"')
            mapping[argument] = value

        for value in positional_values:
            argument = next((a for a in self.arguments if a not in mapping), None)
            if argument is None:
                raise ValueError('Too many positional arguments')
            mapping[argument] = value

        return mapping

    def use_argv(self) -> bool:
        failed: bool = False
        argv_values: dict[ParsedArgument[Any], str] = self.fetch_argv_values()
        for argument, value in argv_values.items():
            try:
                if argument.allow_none and value.lower() == 'none':
                    argument.raw_set_string_value_and_is_none(
                        '', True, builder=self,
                    )
                else:
                    argument.raw_set_string_value_and_is_none(
                        value, False, builder=self,
                    )
            except ValueError as exc:
                print(colour(f'Error while using argv for "{argument.name}": {exc}', hex='#ff0000'))
                failed = True
                continue
        return not failed and bool(argv_values)

    def create_named_tuple(self) -> NT:
        if not all(a.value_is_valid(builder=self) for a in self.arguments):
            raise ValueError('Not all values are valid')
        return self.named_tuple_cls(
            **{a.field_name: a.get_value(builder=self) for a in self.arguments},  # type: ignore
        )

    def maybe_finish(self) -> None:
        if all(a.value_is_valid(builder=self) for a in self.arguments):
            self.on_finish()

    def on_finish(self) -> None:
        self.finished = True
        self.index = -1
        maybe_remember_after(self)
        self.display()
