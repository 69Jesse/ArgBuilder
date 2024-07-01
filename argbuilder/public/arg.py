from ..unparsed import UnparsedArgument
from ..flags import Flag
from ..utils import (
    AllowedTypes,
    MISSING,
)

from typing import (
    Iterable,
    Optional,
    TypeVar,
    overload,
    Literal,
)


__all__ = (
    'arg',
)


T = TypeVar('T', bound=AllowedTypes)


@overload
def arg(
    description: str = MISSING,
    *,
    type: type[T] = MISSING,
    name: str = MISSING,
    default: Optional[T] = MISSING,
    allow_none: Literal[False] = False,
    options: Iterable[T] = MISSING,
    flag: Flag = MISSING,
    flags: Flag | Iterable[Flag] = MISSING,
    remember: bool | int = MISSING,
) -> T:
    ...

@overload
def arg(
    description: str = MISSING,
    *,
    type: type[T] = MISSING,
    name: str = MISSING,
    default: Optional[T] = MISSING,
    allow_none: Literal[True] = True,
    options: Iterable[T] = MISSING,
    flag: Flag = MISSING,
    flags: Flag | Iterable[Flag] = MISSING,
    remember: bool | int = MISSING,
) -> Optional[T]:
    ...

@overload
def arg(
    description: str = MISSING,
    *,
    type: type[T] = MISSING,
    name: str = MISSING,
    default: Optional[T] = MISSING,
    allow_none: bool = MISSING,
    options: Iterable[T] = MISSING,
    flag: Flag = MISSING,
    flags: Flag | Iterable[Flag] = MISSING,
    remember: bool | int = MISSING,
) -> Optional[T]:
    ...

def arg(
    description: str = MISSING,
    *,
    type: type[T] = MISSING,
    name: str = MISSING,
    default: Optional[T] = MISSING,
    allow_none: bool = MISSING,
    options: Iterable[T] = MISSING,
    flag: Flag = MISSING,
    flags: Flag | Iterable[Flag] = MISSING,
    remember: bool | int = MISSING,
) -> Optional[T]:
    """Creates an argument for the argument parser.

    Parameters
    ------------
    description: :class:`str`
        The description of the argument.
    type: :class:`type[T]`
        The type of the argument.
    name: :class:`str`
        The name of the argument.
    default: :class:`Optional[T]`
        The default value of the argument.
    allow_none: :class:`bool`
        Indicates if the argument can be None.
    options: :class:`Iterable[T]`
        The options of the argument.
        If left empty, uses logic to determine the options.
    flag: :class:`~argbuilder.Flag`
        The flag of the argument. Alias for `flags`.
    flags: Union[:class:`~argbuilder.Flag`, :class:`Iterable[~argbuilder.Flag]`]
        The flags of the argument.
    remember: Union[:class:`bool`, :class:`int`]
        Indicates if the argument should be remembered.
        If an integer is provided, it is the number of seconds the argument should be remembered for.

    Returns
    ---------
    :class:`T`
        The argument provided via the console.
        This is only correct if ArgParser.parse_args is used.

    # Example
    ```python
    from argbuilder import ArgParser, arg
    from pathlib import Path

    class Arguments(ArgParser):
        number: int = arg('The number')
        boolean: bool | None = arg('The boolean')
        message: str = arg('The message', default='Hello, World!')
        path: Path | None = arg('The path', default=None)

    args = Arguments.parse_args('This is a test program')
    print(args)
    ```
    """
    argument = UnparsedArgument(
        description=description,
        type=type,
        name=name,
        default=default,
        allow_none=allow_none,
        options=options,
        flag=flag,
        flags=flags,
        remember=remember,
    )
    return argument  # type: ignore


# from typing import TYPE_CHECKING
# if (
#     TYPE_CHECKING
#     # and not TYPE_CHECKING
# ):
#     a: int = arg()                                                # works         int
#     reveal_type(a)
#     b: int = arg(type=str)                                        # doesnt work
#     reveal_type(b)
#     c: int = arg(type=int, default=123, options=[123])            # works         int
#     reveal_type(c)
#     d: int = arg(type=int, default=123, options=['a'])            # doesnt work
#     reveal_type(d)
#     e: int = arg(type=int, options=['a'])                         # doesnt work
#     reveal_type(e)
#     f: Optional[int] = arg()                                      # works         int | None
#     reveal_type(f)
#     g: Optional[int] = arg(type=int, required=False)              # works         int | None
#     reveal_type(g)
#     h = arg(type=int, required=False)                             # works         int | None
#     reveal_type(h)
#     i = arg(type=int, required=False, default=None, options=[1])  # works         int | None
#     reveal_type(i)
#     j: int = arg(required=False)                                  # doesnt work
#     reveal_type(j)
