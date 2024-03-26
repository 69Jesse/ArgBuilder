from ..builder import Builder
from ..utils import MISSING

import os
import sys

from typing import (
    NamedTuple,
    Self,
)


__all__ = (
    'ArgParser',
)


class ArgParser(NamedTuple):
    @classmethod
    def parse_args(
        cls,
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
