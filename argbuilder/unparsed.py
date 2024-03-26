from .arguments import ParsedArgument
from .flags import Flag
from .utils import (
    AllowedTypes,
    MISSING,
)

from enum import Enum

from typing import (
    Iterable,
    Literal,
    NamedTuple,
    Optional,
    get_origin,
    Union,
    Any,
)
from types import UnionType


__all__ = (
    'UnparsedArgument',
)


class UnparsedArgument:
    description: Optional[str]
    _type: Optional[type[AllowedTypes]]
    name: Optional[str]
    default: Optional[AllowedTypes]
    has_default: bool
    allow_none: Optional[bool]
    options: Optional[list[AllowedTypes]]
    flags: list[Flag]
    remember: Optional[bool]
    field_name: str
    def __init__(
        self,
        description: str = MISSING,
        *,
        type: type[AllowedTypes] = MISSING,
        name: str = MISSING,
        default: Optional[AllowedTypes] = MISSING,
        allow_none: bool = MISSING,
        options: Iterable[AllowedTypes] = MISSING,
        flag: Flag = MISSING,
        flags: Flag | Iterable[Flag] = MISSING,
        remember: bool = MISSING,
    ) -> None:
        self.description = description if description is not MISSING else None
        self._type = type if type is not MISSING else None
        self.name = name if name is not MISSING else None
        self.default = default if default is not MISSING else None
        self.has_default = default is not MISSING
        self.allow_none = allow_none if allow_none is not MISSING else None
        self.options = list(options) if options is not MISSING else None
        if flag is not MISSING:
            if flags is not MISSING:
                raise ValueError('Cannot use both flag and flags')
            self.flags = [flag]
        if isinstance(flags, Flag):
            flags = [flags]
        self.flags = list(flags) if flags is not MISSING else []
        self.remember = remember if remember is not MISSING else None

    def _check_description(
        self,
        *,
        named_tuple_cls: type[NamedTuple],
        index: int,
        parsed_arguments: list[ParsedArgument[AllowedTypes]],
    ) -> None:
        self.description = self.description if self.description is not None else 'No description provided'

    def _take_out_of_union(self, value: Any) -> Any:
        if value is None:
            return value
        value_is_union = get_origin(value) is Union or isinstance(value, UnionType)
        if not value_is_union:
            return value
        items: tuple[Any, ...] = value.__args__
        if len(items) == 1:
            return items[0]
        if len(items) != 2:
            raise ValueError(f'Invalid type {value!r}')
        try:
            none_index: int = items.index(type(None))
        except ValueError:
            raise ValueError(f'Invalid type {value!r}')
        self.allow_none = True
        return items[1 - none_index]

    def _check_type(
        self,
        *,
        named_tuple_cls: type[NamedTuple],
        index: int,
        parsed_arguments: list[ParsedArgument[AllowedTypes]],
    ) -> None:
        annotation = self._take_out_of_union(
            named_tuple_cls.__annotations__.get(
                named_tuple_cls._fields[index], None,
            )
        )
        if self._type is None and annotation is None:
            raise ValueError(f'Missing type for {named_tuple_cls._fields[index]!r}')
        if self._type is None:
            self._type = annotation

        type_is_literal = get_origin(self._type) is Literal
        if annotation is not None and (
            (self._type if not type_is_literal else self._type.__args__[0])  # type: ignore
            != (annotation if get_origin(annotation) is not Literal else annotation.__args__[0])
        ):
            raise ValueError(f'Type annotation and type mismatch {annotation!r} {self._type!r}')
        if type_is_literal:
            options: list[AllowedTypes] = list(self._type.__args__)  # type: ignore
            if self.options is not None:
                smallest, largest = min((self.options, options), key=len), max((self.options, options), key=len)
                if not all(o in largest for o in smallest):
                    raise ValueError(f'Options mismatch {self.options!r} {options!r}')
            else:
                self.options = options
            self._type = type(options[0])

        if not isinstance(self._type, type):
            raise ValueError(f'Invalid type {self._type!r}')
        if not issubclass(self._type, AllowedTypes):
            raise ValueError(f'Invalid type {self._type.__name__}')

    def _check_name(
        self,
        *,
        named_tuple_cls: type[NamedTuple],
        index: int,
        parsed_arguments: list[ParsedArgument[AllowedTypes]],
    ) -> None:
        self.field_name = named_tuple_cls._fields[index]
        if self.name is None:
            self.name = self.field_name
        if any(argument.name == self.name for argument in parsed_arguments):
            raise ValueError('Duplicate argument name')

    def _check_default(
        self,
        *,
        named_tuple_cls: type[NamedTuple],
        index: int,
        parsed_arguments: list[ParsedArgument[AllowedTypes]],
    ) -> None:
        if not self.has_default:
            for parsed in parsed_arguments:
                if not parsed.required:
                    raise ValueError('Cannot have non-required argument after required argument')
            return
        assert self._type is not None
        if self.allow_none and self.default is None:
            return
        if not isinstance(self.default, self._type):
            raise ValueError(f'Default is not of type {self._type.__name__}')
        if self.options is not None and self.default not in self.options:
            raise ValueError(f'Default not in options {self.default!r}')
        self.default = self._type(self.default)  # type: ignore

    def _check_allow_none(
        self,
        *,
        named_tuple_cls: type[NamedTuple],
        index: int,
        parsed_arguments: list[ParsedArgument[AllowedTypes]],
    ) -> None:
        if self.allow_none is None:
            self.allow_none = False
            return
        if self.allow_none is True:
            if self.options is not None and None in self.options:
                raise ValueError('Do not add None in the options.')

    def _check_required(
        self,
        *,
        named_tuple_cls: type[NamedTuple],
        index: int,
        parsed_arguments: list[ParsedArgument[AllowedTypes]],
    ) -> None:
        ...

    def _check_options(
        self,
        *,
        named_tuple_cls: type[NamedTuple],
        index: int,
        parsed_arguments: list[ParsedArgument[AllowedTypes]],
    ) -> None:
        assert self._type is not None
        if self.options is None:
            if not issubclass(self._type, Enum):
                return
            self.options = list(self._type)
        if len(self.options) <= 1:
            raise ValueError('Options must contain more than one element')
        if len(self.options) != len(set(self.options)):
            raise ValueError('Options cannot contain duplicates')
        if not all(isinstance(o, self._type) for o in self.options):
            raise ValueError(f'Options are not all of type {self._type.__name__}')
        for i, option in enumerate(self.options):
            self.options[i] = self._type(option)  # type: ignore

    def _check_flags(
        self,
        *,
        named_tuple_cls: type[NamedTuple],
        index: int,
        parsed_arguments: list[ParsedArgument[AllowedTypes]],
        parsed_cls: type[ParsedArgument[AllowedTypes]],
    ) -> None:
        for flag in self.flags:
            if not isinstance(flag, Flag):
                raise ValueError(f'Invalid flag {flag!r}')
            if parsed_cls not in flag.allowed_parsed_argument_types():
                raise ValueError(f'Flag {flag!r} does not support {parsed_cls.__name__} arguments')

    def check_everything(
        self,
        *,
        named_tuple_cls: type[NamedTuple],
        index: int,
        parsed_arguments: list[ParsedArgument[AllowedTypes]],
    ) -> None:
        for check in (
            self._check_name,
            self._check_description,
            self._check_type,
            self._check_options,
            self._check_default,
            self._check_required,
            self._check_allow_none,
        ):
            check(
                named_tuple_cls=named_tuple_cls,
                index=index,
                parsed_arguments=parsed_arguments,
            )

    def check_everything_with_parsed_cls(
        self,
        *,
        named_tuple_cls: type[NamedTuple],
        index: int,
        parsed_arguments: list[ParsedArgument[AllowedTypes]],
        parsed_cls: type[ParsedArgument[AllowedTypes]],
    ) -> None:
        for check in (
            self._check_flags,
        ):
            check(
                named_tuple_cls=named_tuple_cls,
                index=index,
                parsed_arguments=parsed_arguments,
                parsed_cls=parsed_cls,
            )
