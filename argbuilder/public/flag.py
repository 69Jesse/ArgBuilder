from ..flags import (
    GreaterThanFlag,
    GreaterThanOrEqualFlag,
    LessThanFlag,
    LessThanOrEqualFlag,
    ExistsFlag,
    DoesNotExistFlag,
    IsDirFlag,
    IsFileFlag,
    PasswordFlag,
    HardPasswordFlag,
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
        password: str = arg('A password', flags=(Flag.Password(), Flag.GreaterThanOrEqual(8)))
        letter: str = arg('A, B or C', default='A', options=('A', 'B', 'C'))

    args = Arguments.parse_args('This is a test program')
    assert args.number >= 5
    assert args.path.is_dir() and args.path.exists()
    assert len(args.password) >= 8
    assert args.letter in ('A', 'B', 'C')
    ```
    This has created three arguments, `number`, `letter`, and `path`.
    The `number` argument is required and must be greater than or equal to 5.
    The `path` argument is required and must be a directory that exists.
    The `password` argument is required and must be a password of at least 8 characters.
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
    Password = PasswordFlag
    HardPassword = HardPasswordFlag
