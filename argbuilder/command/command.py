from abc import ABC, abstractmethod

import time

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..builder import Builder


class Command(ABC):
    created_at: float
    executed_at: float
    def __init__(self) -> None:
        self.created_at = 0.0
        self.executed_at = 0.0

    @property
    def executed(self) -> bool:
        return self.executed_at > 0.0

    @abstractmethod
    def execute(self, *, builder: 'Builder[Any]') -> None:
        self.executed_at = time.time()

    @abstractmethod
    def undo(self, *, builder: 'Builder[Any]') -> None:
        self.executed_at = 0.0
