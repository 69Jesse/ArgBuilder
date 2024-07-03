from enum import Enum
from pathlib import Path
import json
import time

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

    @classmethod
    def EVERYWHERE_WITH_DURATION(cls, seconds: int) -> tuple['RememberMode', int]:
        return (cls.EVERYWHERE, seconds)

    @classmethod
    def CWD_WITH_DURATION(cls, seconds: int) -> tuple['RememberMode', int]:
        return (cls.CWD, seconds)


class Memory(TypedDict):
    memorized: int
    are_none: int
    names: list[Optional[str]]
    values: list[Optional[str]]
    timestamp: int


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

    mode, _ = builder.remember_data if builder.remember_data[0] is not RememberMode.NONE else (RememberMode.EVERYWHERE, builder.remember_data[1])
    if mode is RememberMode.EVERYWHERE:
        memory = data.get('everywhere_memory', None)
    elif mode is RememberMode.CWD:
        memory = data.get('cwd_memories', {}).get(get_cwd(), None)
    else:
        raise ValueError(f'Invalid remember mode {mode!r}')
    if memory is None:
        return None

    return memory


def create_memories_mapping(
    memory: Memory,
    arguments: set['ParsedArgument[Any]'],
    builder: 'Builder[Any]',
) -> dict['ParsedArgument[Any]', tuple[str, bool]]:
    memorized: int = memory.get('memorized', 0)
    are_none: int = memory.get('are_none', 0)
    names: list[Optional[str]] = memory.get('names', [])
    values: list[Optional[str]] = memory.get('values', [])
    name_to_argument: dict[str, 'ParsedArgument[Any]'] = {
        normalize_name(argument.name): argument
        for argument in arguments
    }
    now: int = int(time.time())
    mapping: dict['ParsedArgument[Any]', tuple[str, bool]] = {}  # {argument: (value, is_none)}
    _, timestamp = builder.remember_data if builder.remember_data[0] is not RememberMode.NONE else (RememberMode.EVERYWHERE, builder.remember_data[1])
    for i, (name, value) in enumerate(zip(names, values)):
        if not bit_is_set(memorized, i):
            continue
        assert name is not None and value is not None
        argument = name_to_argument.get(name, None)
        if argument is None:
            continue
        if isinstance(argument.remember, int):
            if now - memory.get('timestamp', now) > argument.remember:
                continue
        else:
            if timestamp != -1 and memory.get('timestamp', now) < now - timestamp:
                continue
        mapping[argument] = (value, bit_is_set(are_none, i))
    return mapping


def create_memory(builder: 'Builder[Any]') -> Memory:
    memory: Memory = {
        'memorized': 0,
        'are_none': 0,
        'names': [],
        'values': [],
        'timestamp': int(time.time()),
    }
    for i, argument in enumerate(builder.arguments):
        remember = argument.remember if argument.remember is not None else (builder.remember_data[0] is not RememberMode.NONE)
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
    mode, _ = builder.remember_data if builder.remember_data[0] is not RememberMode.NONE else (RememberMode.EVERYWHERE, builder.remember_data[1])
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
    if builder.remember_data[0] is RememberMode.NONE:
        arguments = set(argument for argument in builder.arguments if argument.remember)
    else:
        arguments = set(argument for argument in builder.arguments if argument.remember is not False)
    if len(arguments) == 0:
        return
    memory = maybe_fetch_memory(builder)
    if memory is None:
        return
    mapping = create_memories_mapping(memory, arguments, builder)
    for argument, (string_value, is_none) in mapping.items():
        try:
            argument.raw_set_string_value_and_is_none(
                string_value, is_none, builder=builder,
            )
        except ValueError:
            continue


def maybe_remember_after(builder: 'Builder[Any]') -> None:
    memory = create_memory(builder)
    if len(memory.get('names', [])) == 0:
        return
    update_data(builder, memory)


def clear_memory(builder: 'Builder[Any]') -> None:
    name = normalize_name(builder.name)
    path = MEMORY_FOLDER / f'{name}.json'
    if path.exists():
        path.unlink()
    print(f'Cleared memory for "{builder.name}"')
