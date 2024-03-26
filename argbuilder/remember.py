from enum import Enum
from pathlib import Path
import json

from typing import TYPE_CHECKING, Any, TypedDict, Optional, NotRequired
if TYPE_CHECKING:
    from .builder import Builder
    from .arguments import ParsedArgument


HERE: Path = Path(__file__).resolve().parent
MEMORY_FOLDER: Path = HERE / 'memory'
if not MEMORY_FOLDER.exists():
    MEMORY_FOLDER.mkdir(parents=True)
assert MEMORY_FOLDER.is_dir()


class RememberMode(Enum):
    EVERYWHERE = 0
    CWD = 1
    NONE = 2


class Memory(TypedDict):
    memorized: int
    are_none: int
    names: list[str]
    values: list[str]


class MemoryFileJson(TypedDict):
    everywhere_memory: NotRequired[Optional[Memory]]
    cwd_memories: NotRequired[dict[str, Memory]]


ALLOWED_CHARS: frozenset[str] = frozenset('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
def normalize_name(name: str) -> str:
    return ''.join(char for char in name if char in ALLOWED_CHARS) or 'script'


def fetch_json(name: str) -> MemoryFileJson:
    name = normalize_name(name)
    path = MEMORY_FOLDER / f'{name}.json'
    with path.open(encoding='utf-8') as file:
        return json.load(file)


def get_memories(builder: 'Builder[Any]') -> dict['ParsedArgument[Any]', tuple[str, bool]]:
    try:
        data = fetch_json(builder.name)
    except FileNotFoundError:
        return {}
    ... # TODO OOOOO


def maybe_remember_before(builder: 'Builder[Any]') -> None:
    if builder.remember_mode is RememberMode.NONE:
        return


def maybe_remember_after(builder: 'Builder[Any]') -> None:
    if builder.remember_mode is RememberMode.NONE:
        return
