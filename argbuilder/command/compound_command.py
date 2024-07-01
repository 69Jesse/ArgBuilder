
from .command import Command
from .set_command import SetCommand

from typing import Optional, final, TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..builder import Builder


@final
class CompoundCommand(Command):
    commands: list[Command]
    def __init__(
        self,
        commands: Optional[list[Command]] = None,
    ) -> None:
        super().__init__()
        self.commands = commands if commands is not None else []

    def execute(self, *, builder: 'Builder[Any]') -> None:
        assert not self.executed
        for command in self.commands:
            if not command.executed:
                command.execute(builder=builder)
        return super().execute(builder=builder)

    def undo(self, *, builder: 'Builder[Any]') -> None:
        assert self.executed
        for command in reversed(self.commands):
            if command.executed:
                command.undo(builder=builder)
        return super().undo(builder=builder)

    @staticmethod
    def maybe_create_merged(this: Command, other: Command) -> Optional['CompoundCommand']:
        if isinstance(this, CompoundCommand):
            if len(this.commands) == 0:
                return None
            maybe_this = this.commands[-1]
        else:
            maybe_this = this

        if not SetCommand.should_merge(maybe_this, other):
            return None
        if isinstance(this, CompoundCommand):
            this.commands.append(other)
            return this
        return CompoundCommand([this, other])
