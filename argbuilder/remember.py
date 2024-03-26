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
    everywhere_memory: Optional[Memory]
    cwd_memories: dict[str, Memory]


ALLOWED_CHARS: frozenset[str] = frozenset('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
def normalize_name(name: str) -> str:
    return ''.join(char for char in name if char in ALLOWED_CHARS) or 'script'


def get_cwd() -> str:
    return Path.cwd().resolve().as_posix()


def fetch_json(name: str) -> MemoryFileJson:
    name = normalize_name(name)
    path = MEMORY_FOLDER / f'{name}.json'
    with path.open(encoding='utf-8') as file:
        return json.load(file)


def bit_is_set(n: int, i: int) -> bool:
    return bool(n >> i & 1)


def get_memories(builder: 'Builder[Any]') -> dict['ParsedArgument[Any]', tuple[str, bool]]:
    try:
        data = fetch_json(builder.name)
    except FileNotFoundError:
        return {}

    if builder.remember_mode is RememberMode.EVERYWHERE:
        memory = data.get('everywhere_memory', None)
    elif builder.remember_mode is RememberMode.CWD:
        memory = data.get('cwd_memories', {}).get(get_cwd(), None)
    else:
        raise ValueError(f'Invalid remember mode {builder.remember_mode!r}')
    if memory is None:
        return {}

    memorized: int = memory.get('memorized', 0)
    are_none: int = memory.get('are_none', 0)
    names: list[str] = memory.get('names', [])
    values: list[str] = memory.get('values', [])
    arguments: dict[str, 'ParsedArgument[Any]'] = {
        normalize_name(argument.name): argument
        for argument in builder.arguments
    }
    result: dict['ParsedArgument[Any]', tuple[str, bool]] = {}
    for i, (name, value) in enumerate(zip(names, values)):
        if not bit_is_set(memorized, i):
            continue
        argument = arguments.get(name, None)
        if argument is None:
            continue
        result[argument] = (value, bit_is_set(are_none, i))
    return result


def maybe_remember_before(builder: 'Builder[Any]') -> None:
    if builder.remember_mode is RememberMode.NONE:
        return


def maybe_remember_after(builder: 'Builder[Any]') -> None:
    if builder.remember_mode is RememberMode.NONE:
        return
