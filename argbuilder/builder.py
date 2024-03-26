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
from .remember import RememberMode, maybe_remember_before, maybe_remember_after

import time
from enum import Enum
from functools import cached_property
import msvcrt
import os
from pathlib import Path
import re

from typing import (
    Any,
    NamedTuple,
    Optional,
    TypeVar,
    Generic,
)


__all__ = (
    'Builder',
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


def scuffed_log(*message: str | Any) -> None:
    with open('log.txt', 'a') as file:
        file.write(f'{' '.join(map(str, message))}\n')


NT = TypeVar('NT', bound=NamedTuple)


class Builder(Generic[NT]):
    named_tuple_cls: type[NT]
    name: str
    description: str
    author: str
    arguments: list[ParsedArgument[Any]]
    remember_mode: RememberMode
    started: bool
    finished: bool
    index: int
    inner_index: int
    higher_inner_index: int
    last_text_line_count: int
    previous_string_values: list[tuple[str, bool, int, float]]  # [(string_value, selected.is_none, index, epoch), ...]
    reversed_string_values: list[tuple[str, bool, int]]  # [(string_value, selected.is_none, index), ...]
    previous_input: Optional[str | SpecialKey]
    def __init__(
        self,
        *,
        named_tuple_cls: type[NT],
        name: str,
        description: str,
        author: str,
        arguments: list[ParsedArgument],
        remember_mode: RememberMode,
    ) -> None:
        self.named_tuple_cls = named_tuple_cls
        self.name = name
        self.description = description
        self.author = author
        self.arguments = arguments
        self.remember_mode = remember_mode
        self.started = False
        self.finished = False
        self.index = 0
        self.inner_index = 0
        self.higher_inner_index = 0
        self.last_text_line_count = -1
        self.previous_string_values = []
        self.reversed_string_values = []
        self.previous_input = None
        maybe_remember_before(self)

    @staticmethod
    def from_named_tuple_cls(
        named_tuple_cls: type[NT],
        *,
        name: str,
        description: str,
        author: str,
        remember_mode: RememberMode,
    ) -> 'Builder[NT]':
        for key, value in vars(named_tuple_cls).items():
            if isinstance(value, UnparsedArgument):
                raise ValueError(f'{key!r} must have a type annotation. Example:\n\t{key}: int = arg(...)')

        arguments: list[ParsedArgument] = []

        for index, field_name in enumerate(named_tuple_cls._fields):
            try:
                unparsed: Any = named_tuple_cls._field_defaults.get(field_name, None)
                if unparsed is None:
                    unparsed = UnparsedArgument()
                if isinstance(unparsed, str):
                    unparsed = UnparsedArgument(description=unparsed)
                if not isinstance(unparsed, UnparsedArgument):
                    raise ValueError(f'Expected {UnparsedArgument.__name__!r} for the default value but got {unparsed.__class__.__name__!r}')
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
                )
                arguments.append(argument)
            except ValueError as exc:
                raise ValueError(f'Error while parsing {field_name!r}') from exc

        return Builder(
            named_tuple_cls=named_tuple_cls,
            name=name,
            description=description,
            author=author,
            arguments=arguments,
            remember_mode=remember_mode,
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
        try:
            self.selected_argument().handle_char(self.previous_input, builder=self)
        except ValueError:
            pass
        return

    def on_value_change(
        self,
        *,
        before: tuple[str, bool],
        after: tuple[str, bool],
    ) -> None:
        if len(after) > 0:
            self.selected_argument().is_none = False
        if self.previous_input not in (
            SpecialKey.ctrl_z,
            SpecialKey.ctrl_y,
        ):
            self.reversed_string_values = []
            previous_entry: Optional[tuple[str, bool, int, float]] = self.previous_string_values[-1] if self.previous_string_values else None
            if previous_entry is not None:
                _, _, index, previous_epoch = previous_entry
                if index == self.index:
                    epoch_difference: float = time.time() - previous_epoch
                    if epoch_difference < 0.3:
                        return
            self.previous_string_values.append((*before, self.index, time.time()))

    def go_back(self) -> None:
        if len(self.previous_string_values) == 0:
            return
        string_value, is_none, index, _ = self.previous_string_values.pop()
        argument = self.arguments[index]
        entry = (argument.string_value, argument.is_none, index)
        scuffed_log(string_value, is_none, index, entry)
        argument.string_value = string_value
        argument.is_none = is_none
        self.reversed_string_values.append(entry)

    def reverse_go_back(self) -> None:
        if len(self.reversed_string_values) == 0:
            return
        string_value, is_none, index = self.reversed_string_values.pop()
        argument = self.arguments[index]
        entry = (argument.string_value, argument.is_none, index, 0)
        argument.string_value = string_value
        argument.is_none = is_none
        self.previous_string_values.append(entry)

    def handle_special_key(self, special_key: SpecialKey) -> None:
        self.previous_input = special_key
        if special_key is SpecialKey.up:
            self.index = (self.index - 1) % len(self.arguments)
        elif special_key is SpecialKey.down:
            self.index = (self.index + 1) % len(self.arguments)
        elif special_key is SpecialKey.ctrl_up:
            self.index = 0
        elif special_key is SpecialKey.ctrl_down:
            self.index = len(self.arguments) - 1
        elif special_key is SpecialKey.enter:
            self.maybe_finish()
        elif special_key is SpecialKey.ctrl_z:
            self.go_back()
        elif special_key is SpecialKey.ctrl_y:
            self.reverse_go_back()
        else:
            try:
                self.selected_argument().handle_special_key(special_key, builder=self)
            except ValueError:
                pass
            return
        self.inner_index = min(self.higher_inner_index, len(self.arguments[self.index].display(builder=self)))

    def iterate(self) -> None:
        self.display()
        byte = msvcrt.getch()
        if byte == b'\x03':
            raise KeyboardInterrupt

        selected: ParsedArgument = self.selected_argument()
        before_string_value: str = selected.string_value
        before_is_none: bool = selected.is_none
        if byte == b'\xe0':
            byte = msvcrt.getch()
            self.handle_special_key(SpecialKey(byte))
        elif byte in SPECIAL_KEYS_NOTHING_BEFORE:
            self.handle_special_key(SpecialKey(byte))
        else:
            self.handle_byte(byte)
        if selected is self.selected_argument() and (before_string_value != selected.string_value or before_is_none != selected.is_none):
            self.on_value_change(
                before=(before_string_value, before_is_none),
                after=(selected.string_value, selected.is_none),
            )

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
