import colorsys
from typing import Optional
import random


__all__ = (
    'random_rgb_neon_colour',
    'colour',
)


def random_rgb_neon_colour() -> tuple[int, int, int]:
    rgb = colorsys.hsv_to_rgb(random.random(), 0.7, 1.0)
    return tuple(int(c * 255) for c in rgb)  # type: ignore


def colour(
    text: str,
    *,
    rgb: Optional[tuple[int, int, int]] = None,
    hex: Optional[str] = None,
    background_rgb: Optional[tuple[int, int, int]] = None,
    background_hex: Optional[str] = None,
    bold: bool = False,
) -> str:
    if rgb is None and hex is None:
        raise ValueError('Either rgb or hex must be provided')
    if rgb is not None and hex is not None:
        raise ValueError('Both rgb and hex cannot be provided')
    if hex is not None:
        hex = hex.lstrip('#')
        if len(hex) != 6:
            raise ValueError('Hex must be 6 characters long')
        rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))  # type: ignore
    if background_rgb is None and background_hex is not None:
        background_hex = background_hex.lstrip('#')
        if len(background_hex) != 6:
            raise ValueError('Background hex must be 6 characters long')
        background_rgb = tuple(int(background_hex[i:i+2], 16) for i in (0, 2, 4))  # type: ignore
    assert rgb is not None
    prefix = f'\033[{'1;' if bold else ''}38;2;{rgb[0]};{rgb[1]};{rgb[2]}m' + (
        f'\033[48;2;{background_rgb[0]};{background_rgb[1]};{background_rgb[2]}m' if background_rgb is not None else ''
    )
    suffix = '\033[0m'
    return prefix + text.replace(suffix, f'{suffix}{prefix}') + suffix
