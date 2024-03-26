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
    'argument',
)


T = TypeVar('T', bound=AllowedTypes)


@overload
def argument(
    description: str = MISSING,
    *,
    type: type[T] = MISSING,
    name: str = MISSING,
    default: Optional[T] = MISSING,
    allow_none: Literal[False] = False,
    options: Iterable[T] = MISSING,
    flag: Flag = MISSING,
    flags: Iterable[Flag] = MISSING,
) -> T:
    ...

@overload
def argument(
    description: str = MISSING,
    *,
    type: type[T] = MISSING,
    name: str = MISSING,
    default: Optional[T] = MISSING,
    allow_none: Literal[True] = True,
    options: Iterable[T] = MISSING,
    flag: Flag = MISSING,
    flags: Iterable[Flag] = MISSING,
) -> Optional[T]:
    ...

@overload
def argument(
    description: str = MISSING,
    *,
    type: type[T] = MISSING,
    name: str = MISSING,
    default: Optional[T] = MISSING,
    allow_none: bool = MISSING,
    options: Iterable[T] = MISSING,
    flag: Flag = MISSING,
    flags: Iterable[Flag] = MISSING,
) -> Optional[T]:
    ...

def argument(
    description: str = MISSING,
    *,
    type: type[T] = MISSING,
    name: str = MISSING,
    default: Optional[T] = MISSING,
    allow_none: bool = MISSING,
    options: Iterable[T] = MISSING,
    flag: Flag = MISSING,
    flags: Iterable[Flag] = MISSING,
) -> Optional[T]:
    argument = UnparsedArgument(
        description=description,
        type=type,
        name=name,
        default=default,
        allow_none=allow_none,
        options=options,
        flag=flag,
        flags=flags,
    )
    return argument  # type: ignore


# from typing import TYPE_CHECKING
# if (
#     TYPE_CHECKING
#     and not TYPE_CHECKING
# ):
#     a: int = argument()                                                # works         int
#     reveal_type(a)
#     b: int = argument(type=str)                                        # doesnt work
#     reveal_type(b)
#     c: int = argument(type=int, default=123, options=[123])            # works         int
#     reveal_type(c)
#     d: int = argument(type=int, default=123, options=['a'])            # doesnt work
#     reveal_type(d)
#     e: int = argument(type=int, options=['a'])                         # doesnt work
#     reveal_type(e)
#     f: Optional[int] = argument()                                      # works         int | None
#     reveal_type(f)
#     g: Optional[int] = argument(type=int, required=False)              # works         int | None
#     reveal_type(g)
#     h = argument(type=int, required=False)                             # works         int | None
#     reveal_type(h)
#     i = argument(type=int, required=False, default=None, options=[1])  # works         int | None
#     reveal_type(i)
#     j: int = argument(required=False)                                  # doesnt work
#     reveal_type(j)
