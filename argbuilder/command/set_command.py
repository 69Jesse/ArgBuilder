from .command import Command

from typing import Any, final, TYPE_CHECKING
if TYPE_CHECKING:
    from ..arguments import ParsedArgument
    from ..builder import Builder


@final
class SetCommand(Command):
    argument: 'ParsedArgument[Any]'
    after_string_value: str
    after_is_none: bool
    after_index: int
    after_inner_index: int
    before_string_value: str
    before_is_none: bool
    before_index: int
    before_inner_index: int
    def __init__(
        self,
        argument: 'ParsedArgument[Any]',
        after_string_value: str,
        after_is_none: bool,
        after_index: int,
        after_inner_index: int,
    ) -> None:
        super().__init__()
        self.argument = argument
        self.after_string_value = after_string_value
        self.after_is_none = after_is_none
        self.after_index = after_index
        self.after_inner_index = after_inner_index

    def execute(self, *, builder: 'Builder[Any]') -> None:
        self.before_string_value = self.argument.string_value
        self.before_is_none = self.argument.is_none
        self.before_index = builder.index
        self.before_inner_index = builder.inner_index
        self.argument.string_value = self.after_string_value
        self.argument.is_none = self.after_is_none
        builder.index = self.after_index
        builder.inner_index = self.after_inner_index
        builder.higher_inner_index = self.after_inner_index
        super().execute(builder=builder)

    def undo(self, *, builder: 'Builder[Any]') -> None:
        self.argument.string_value = self.before_string_value
        self.argument.is_none = self.before_is_none
        builder.index = self.before_index
        builder.inner_index = self.before_inner_index
        builder.higher_inner_index = self.before_inner_index
        super().undo(builder=builder)

    @staticmethod
    def should_merge(this: 'Command', other: 'Command') -> bool:
        return (
            isinstance(this, SetCommand)
            and isinstance(other, SetCommand)
            and -0.3 <= this.created_at - other.created_at <= 0.0
        )
