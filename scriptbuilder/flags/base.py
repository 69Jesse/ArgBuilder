from abc import (
    ABC,
    abstractmethod,
)
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..arguments import ParsedArgument
    from ..builder import Builder


class Flag(ABC):
    @abstractmethod
    def allowed_parsed_argument_types(self) -> set[type['ParsedArgument']]:
        raise NotImplementedError

    @abstractmethod
    def check_maybe_raise(
        self,
        argument: 'ParsedArgument',
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        raise NotImplementedError

    def check(
        self,
        argument: 'ParsedArgument',
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        try:
            return self.check_maybe_raise(argument, builder=builder)
        except ValueError:
            return False

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError
