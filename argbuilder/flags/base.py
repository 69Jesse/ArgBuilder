from abc import (
    ABC,
    abstractmethod,
)
from typing import TYPE_CHECKING, Any, Optional
if TYPE_CHECKING:
    from ..arguments import ParsedArgument
    from ..builder import Builder


__all__ = (
    'Flag',
)


class Flag(ABC):
    @abstractmethod
    def allowed_parsed_argument_types(self) -> Optional[set[type['ParsedArgument']]]:
        """Return the set of parsed argument types that this flag can be applied to. If None, the flag can be applied to any parsed argument type."""
        raise NotImplementedError

    @abstractmethod
    def check_maybe_raise(
        self,
        argument: 'ParsedArgument',
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        """Check if the flag is satisfied by the parsed argument. This can raise a ValueError, on raise, it assumes the check failed."""
        raise NotImplementedError

    def check(
        self,
        argument: 'ParsedArgument',
        *,
        builder: 'Builder[Any]',
    ) -> bool:
        """Check if the flag is satisfied by the parsed argument."""
        try:
            return self.check_maybe_raise(argument, builder=builder)
        except ValueError:
            return False

    @abstractmethod
    def maybe_change_display(
        self,
        argument: 'ParsedArgument',
        display: str,
        *,
        builder: 'Builder[Any]',
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError
