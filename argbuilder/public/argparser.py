# I am terribly sorry
from ..builder import Builder
from ..utils import MISSING
from ..remember import RememberMode

import os
import sys

from typing import (
    NamedTuple,
    Any,
    TYPE_CHECKING,
    TypeVar,
    NamedTupleMeta,  # pyright: ignore[reportAttributeAccessIssue]
    _NamedTuple,  # pyright: ignore[reportAttributeAccessIssue]
    Self,
)


__all__ = (
    'ArgParser',
)


NT = TypeVar('NT', bound=NamedTuple)


class ArgParser(NamedTuple):
    """NamedTuple class to parse command line arguments and return a NamedTuple instance.

    # Simple Example
    ```python
    from argbuilder import ArgParser

    class Arguments(ArgParser):
        number: int
        message: str = 'Hello, World!'

    args = Arguments.parse_args('This is a test program')
    print(args.number, args.message)
    ```
    This has created two arguments, `number` and `message`.
    The `number` argument is required, and the `message` argument has a default value of `'Hello, World!'`.
    # Advanced Example
    ```python
    from argbuilder import ArgParser, arg, Flag

    class Arguments(ArgParser):
        number: int = arg('The number', flag=Flag.GreaterThanOrEqual(5))
        letter: str = arg('The message', default='A', options=('A', 'B', 'C'))

    args = Arguments.parse_args('This is a test program')
    assert args.number >= 5
    assert args.letter in ('A', 'B', 'C')
    ```
    This has created two arguments, `number` and `letter`.
    The `number` argument is required and must be greater than or equal to 5.
    The `letter` argument has a default value of `'A'` and must be one of `'A'`, `'B'`, or `'C'`.
    """
    @staticmethod
    def __parse_args(
        named_tuple_cls: type[NT],
        description: str = 'No description provided',
        *,
        name: str = MISSING,
        author: str = '69Jesse',
        remember: bool | int | RememberMode | tuple[bool, int] | tuple[RememberMode, int] = False,
    ) -> NT:
        name = name if name is not MISSING else os.path.basename(sys.argv[0]).rsplit('.', 1)[0]
        if isinstance(remember, bool):
            remember = RememberMode.EVERYWHERE if remember else RememberMode.NONE
        if isinstance(remember, int):
            remember = (RememberMode.EVERYWHERE, remember)
        if isinstance(remember, tuple) and isinstance(remember[0], bool):
            remember = (RememberMode.EVERYWHERE if remember[0] else RememberMode.NONE, remember[1])
        if not isinstance(remember, tuple):
            remember = (remember, -1)

        builder = Builder.from_named_tuple_cls(
            named_tuple_cls=named_tuple_cls,
            name=name,
            description=description,
            author=author,
            remember_mode=remember,  # pyright: ignore[reportArgumentType]
        )
        while not builder.finished:
            builder.iterate()
        return builder.create_named_tuple()

    if TYPE_CHECKING:
        @classmethod
        def parse_args(
            cls,
            description: str = 'No description provided',
            *,
            name: str = MISSING,
            author: str = '69Jesse',
            remember: bool | RememberMode | tuple[bool, int] | tuple[RememberMode, int] = False,
        ) -> Self:
            ...
    else:
        parse_args = __parse_args


if not TYPE_CHECKING:
    old_arg_parser = ArgParser
    class Meta(NamedTupleMeta):
        def __new__(cls, *args: Any) -> Any:
            kwargs = args[2]
            kwargs['__orig_bases__'] = (NamedTuple,)
            nt = NamedTupleMeta.__new__(
                NamedTupleMeta,
                args[0],
                (_NamedTuple,),
                kwargs,
            )
            nt.parse_args = classmethod(old_arg_parser.parse_args)
            return nt
    ArgParser = type.__new__(Meta, 'ArgParser', (), {})
