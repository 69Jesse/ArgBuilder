from ..builder import Builder
from ..utils import MISSING

import os
import sys

from typing import (
    NamedTuple,
    Any,
    TYPE_CHECKING,
    TypeVar,
    NamedTupleMeta,  # type: ignore
    _NamedTuple,  # type: ignore
    Self,
)


__all__ = (
    'ArgParser',
)


NT = TypeVar('NT', bound=NamedTuple)


def parse_args(
    cls: type[NT],
    *,
    name: str = MISSING,
    description: str = 'No description provided',
    author: str = '69Jesse',
) -> NT:
    name = name if name is not MISSING else os.path.basename(sys.argv[0]).rsplit('.', 1)[0]
    builder = Builder.from_named_tuple_cls(
        named_tuple_cls=cls,
        name=name,
        description=description,
        author=author,
    )
    while not builder.finished:
        builder.iterate()
    return builder.create_named_tuple()


class ArgParser(NamedTuple):
    if TYPE_CHECKING:
        @classmethod
        def parse_args(
            cls,
            *,
            name: str = MISSING,
            description: str = 'No description provided',
            author: str = '69Jesse',
        ) -> Self:
            ...
    else:
        @staticmethod
        def parse_args(
            cls: Self,
            *,
            name: str = MISSING,
            description: str = 'No description provided',
            author: str = '69Jesse',
        ) -> Self:
            name = name if name is not MISSING else os.path.basename(sys.argv[0]).rsplit('.', 1)[0]
            builder = Builder.from_named_tuple_cls(
                named_tuple_cls=cls,
                name=name,
                description=description,
                author=author,
            )
            while not builder.finished:
                builder.iterate()
            return builder.create_named_tuple()

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
