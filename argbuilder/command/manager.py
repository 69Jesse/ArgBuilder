from .command import Command
from .compound_command import CompoundCommand

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..builder import Builder


class CommandManager:
    undo_stack: list[Command]
    redo_stack: list[Command]
    def __init__(self) -> None:
        self.undo_stack = []
        self.redo_stack = []

    def do(self, command: Command, *, builder: 'Builder[Any]') -> None:
        command.execute(builder=builder)
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def peek(self) -> Command:
        return self.undo_stack[-1]

    def undo(self, *, builder: 'Builder[Any]') -> None:
        if len(self.undo_stack) == 0:
            return
        command = self.undo_stack.pop()
        command.undo(builder=builder)
        self.redo_stack.append(command)

    def redo(self, *, builder: 'Builder[Any]') -> None:
        if len(self.redo_stack) == 0:
            return
        command = self.redo_stack.pop()
        command.execute(builder=builder)
        self.undo_stack.append(command)

    def check_merge(self, *, builder: 'Builder[Any]') -> None:
        if len(self.undo_stack) < 2:
            return
        this = self.undo_stack[-1]
        other = self.undo_stack[-2]
        merged = CompoundCommand.maybe_create_merged(this, other)
        if merged is not None:
            merged.execute(builder=builder)
            self.undo_stack.pop()
            self.undo_stack.pop()
            self.do(merged, builder=builder)
