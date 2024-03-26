from ..builder import Builder
from ..utils import MISSING
from .arguments_cls import BaseArguments

import os
import sys

from typing import (
    TypeVar,
)


__all__ = (
    'get_arguments',
)


NT = TypeVar('NT', bound=BaseArguments)


def get_arguments(
    named_tuple_cls: type[NT],
    /,
    *,
    name: str = MISSING,
    description: str = 'No description provided',
    author: str = '69Jesse',
) -> NT:
    name = name if name is not MISSING else os.path.basename(sys.argv[0]).rsplit('.', 1)[0]
    builder = Builder.from_named_tuple_cls(
        named_tuple_cls=named_tuple_cls,
        name=name,
        description=description,
        author=author,
    )
    while not builder.finished:
        builder.iterate()
    return builder.create_named_tuple()
