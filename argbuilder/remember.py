from enum import Enum
from pathlib import Path
import json

from typing import TYPE_CHECKING, Any, TypedDict, Optional
if TYPE_CHECKING:
    from .builder import Builder
    from .arguments import ParsedArgument


HERE: Path = Path(__file__).resolve().parent
MEMORY_FOLDER: Path = HERE / 'memory'
if not MEMORY_FOLDER.exists():
    MEMORY_FOLDER.mkdir(parents=True)
assert MEMORY_FOLDER.is_dir()


__all__ = (
    'RememberMode',
    'maybe_remember_before',
    'maybe_remember_after',
)


class RememberMode(Enum):
    EVERYWHERE = 0
    CWD = 1
    NONE = 2


class Memory(TypedDict):
    memorized: int
    are_none: int
    names: list[Optional[str]]
    values: list[Optional[str]]


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


def save_json(name: str, data: MemoryFileJson) -> None:
    name = normalize_name(name)
    path = MEMORY_FOLDER / f'{name}.json'
    with path.open('w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, separators=(',', ':'))


def bit_is_set(n: int, i: int) -> bool:
    return bool(n >> i & 1)


def maybe_fetch_memory(builder: 'Builder[Any]') -> Optional[Memory]:
    try:
        data = fetch_json(builder.name)
    except FileNotFoundError:
        return None

    mode = builder.remember_mode if builder.remember_mode is not RememberMode.NONE else RememberMode.EVERYWHERE
    if mode is RememberMode.EVERYWHERE:
        return data.get('everywhere_memory', None)
    elif mode is RememberMode.CWD:
        return data.get('cwd_memories', {}).get(get_cwd(), None)
    else:
        raise ValueError(f'Invalid remember mode {mode!r}')


def create_memories_mapping(
    memory: Memory,
    arguments: set['ParsedArgument[Any]'],
) -> dict['ParsedArgument[Any]', tuple[str, bool]]:
    memorized: int = memory.get('memorized', 0)
    are_none: int = memory.get('are_none', 0)
    names: list[Optional[str]] = memory.get('names', [])
    values: list[Optional[str]] = memory.get('values', [])
    name_to_argument: dict[str, 'ParsedArgument[Any]'] = {
        normalize_name(argument.name): argument
        for argument in arguments
    }
    mapping: dict['ParsedArgument[Any]', tuple[str, bool]] = {}
    for i, (name, value) in enumerate(zip(names, values)):
        if not bit_is_set(memorized, i):
            continue
        assert name is not None and value is not None
        argument = name_to_argument.get(name, None)
        if argument is None:
            continue
        mapping[argument] = (value, bit_is_set(are_none, i))
    return mapping


def create_memory(builder: 'Builder[Any]') -> Memory:
    memory: Memory = {
        'memorized': 0,
        'are_none': 0,
        'names': [],
        'values': [],
    }
    for i, argument in enumerate(builder.arguments):
        remember = argument.remember if argument.remember is not None else (builder.remember_mode is not RememberMode.NONE)
        if remember:
            memory['memorized'] |= 1 << i
            memory['are_none'] |= argument.is_none << i
            memory['names'].append(normalize_name(argument.name))
            memory['values'].append(argument.string_value)
        else:
            memory['names'].append(None)
            memory['values'].append(None)
    return memory


def update_data(builder: 'Builder[Any]', memory: Memory) -> None:
    data: MemoryFileJson
    try:
        data = fetch_json(builder.name)
    except FileNotFoundError:
        data = {}  # type: ignore
    mode = builder.remember_mode if builder.remember_mode is not RememberMode.NONE else RememberMode.EVERYWHERE
    if mode is RememberMode.EVERYWHERE:
        data['everywhere_memory'] = memory
        data['cwd_memories'] = {}
    elif mode is RememberMode.CWD:
        data['everywhere_memory'] = None
        data.setdefault('cwd_memories', {})[get_cwd()] = memory
    else:
        raise ValueError(f'Invalid remember mode {mode!r}')
    save_json(builder.name, data)


def maybe_remember_before(builder: 'Builder[Any]') -> None:
    arguments: set['ParsedArgument[Any]']
    if builder.remember_mode is RememberMode.NONE:
        arguments = set(argument for argument in builder.arguments if argument.remember)
    else:
        arguments = set(argument for argument in builder.arguments if argument.remember is not False)
    if len(arguments) == 0:
        return
    memory = maybe_fetch_memory(builder)
    if memory is None:
        return
    mapping = create_memories_mapping(memory, arguments)
    for argument, (value, is_none) in mapping.items():
        argument.string_value = value
        argument.is_none = is_none


def maybe_remember_after(builder: 'Builder[Any]') -> None:
    memory = create_memory(builder)
    if len(memory.get('names', [])) == 0:
        return
    update_data(builder, memory)
