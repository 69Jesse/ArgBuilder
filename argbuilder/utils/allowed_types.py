from enum import Enum
from pathlib import Path

from typing import (
    TypeAlias,
    Union,
)


__all__ = (
    'AllowedTypes',
)


AllowedTypes: TypeAlias = Union[
    bool,
    str,
    int,
    float,
    Enum,
    Path,
]
