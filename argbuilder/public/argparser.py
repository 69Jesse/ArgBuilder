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
    NamedTupleMeta,  # type: ignore
    _NamedTuple,  # type: ignore
    Self,
)


__all__ = (
    'ArgParser',
)


NT = TypeVar('NT', bound=NamedTuple)


class ArgParser(NamedTuple):
    @staticmethod
    def __parse_args(
        named_tuple_cls: type[NT],
        description: str = 'No description provided',
        *,
        name: str = MISSING,
        author: str = '69Jesse',
        remember: bool | RememberMode = False,
    ) -> NT:
        name = name if name is not MISSING else os.path.basename(sys.argv[0]).rsplit('.', 1)[0]
        if isinstance(remember, bool):
            remember = RememberMode.EVERYWHERE if remember else RememberMode.NONE
        builder = Builder.from_named_tuple_cls(
            named_tuple_cls=named_tuple_cls,
            name=name,
            description=description,
            author=author,
            remember_mode=remember,
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
            remember: bool | RememberMode = False,
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
