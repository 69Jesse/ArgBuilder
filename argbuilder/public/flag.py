from ..flags import (
    GreaterThanFlag,
    GreaterThanOrEqualFlag,
    LessThanFlag,
    LessThanOrEqualFlag,
    ExistsFlag,
    DoesNotExistFlag,
    IsDirFlag,
    IsFileFlag,
)

from typing import final


__all__ = (
    'Flag',
)


@final
class Flag:
    """A flag to assign to an argument to specify additional constraints on the argument's value.

    # Example
    ```python
    from argbuilder import ArgParser, arg, Flag
    from pathlib import Path

    class Arguments(ArgParser):
        number: int = arg('The number', flag=Flag.GreaterThanOrEqual(5))
        path: Path = arg('Some directory', flags=(Flag.IsDir(), Flag.Exists()))
        letter: str = arg('A, B or C', default='A', options=('A', 'B', 'C'))

    args = Arguments.parse_args('This is a test program')
    assert args.number >= 5
    assert args.letter in ('A', 'B', 'C')
    assert args.path.is_dir() and args.path.exists()
    ```
    This has created three arguments, `number`, `letter`, and `path`.
    The `number` argument is required and must be greater than or equal to 5.
    The `path` argument is required and must be a directory that exists.
    The `letter` argument has a default value of `'A'` and must be one of `'A'`, `'B'`, or `'C'.
    """
    __slots__ = ()

    def __new__(cls) -> None:
        raise TypeError('Do not instantiate this class, use "Flag.xyz()" instead.')

    LessThan = LessThanFlag
    LessThanOrEqual = LessThanOrEqualFlag
    GreaterThan = GreaterThanFlag
    GreaterThanOrEqual = GreaterThanOrEqualFlag
    Exists = ExistsFlag
    DoesNotExist = DoesNotExistFlag
    IsDir = IsDirFlag
    IsFile = IsFileFlag
